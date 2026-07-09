from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

import pandas as pd

from .formula import add_formula, exact_mass, format_formula, parse_formula
from .fragmentation import generate_fragments
from .ion_rules import BaseRecord, generate_dimer_records, process_base_records
from .molecule_io import get_formula_from_mol, mol_from_smiles
from .rule_packs import generate_rule_pack_candidates
from .scoring import score_record


@dataclass
class FormulaRecord:
    formula: str
    counts: dict[str, int]
    exact_mass: float
    ion_mode: str
    charge: int
    source_compound_id: str
    source_name: str
    generation_type: str
    path: list[str]
    broken_bonds: int = 0
    h_shift: int = 0
    adduct: str | None = None
    neutral_losses: list[str] = field(default_factory=list)
    fragment_atom_indices: list[int] | None = None
    score: float = 0.0


def _record(row: dict, counts: dict[str, int], ion_mode: str, charge: int, generation_type: str, path: list[str], cfg: dict, **kwargs) -> FormulaRecord:
    formula = format_formula(counts)
    rec = FormulaRecord(
        formula=formula,
        counts=counts,
        exact_mass=exact_mass(counts),
        ion_mode=ion_mode,
        charge=charge,
        source_compound_id=str(row["compound_id"]),
        source_name=str(row["name"]),
        generation_type=generation_type,
        path=path,
        **kwargs,
    )
    rec.score = score_record(rec, cfg)
    return rec


def generate_formula_network(compound_row, config: dict) -> list[FormulaRecord]:
    row = dict(compound_row)
    mol = mol_from_smiles(row["smiles"])
    parent_formula = row.get("formula") or get_formula_from_mol(mol)
    parent_counts = parse_formula(parent_formula)
    bases: list[BaseRecord] = [(parent_counts, "parent", ["M"], 0, None)]
    for fragment in generate_fragments(mol, config):
        bases.append(
            (
                fragment.counts,
                "fragment",
                [f"break {fragment.broken_bonds} bond(s)"],
                fragment.broken_bonds,
                fragment.atom_indices,
            )
        )

    records = process_base_records(row, bases, config, _record)

    # ── Oligomer extension ──────────────────────────────────────────────
    extend_formula_str = str(row.get("extend_formula", "")).strip()
    oligo_cfg = config.get("oligomer", {})
    max_extend = int(oligo_cfg.get("max_extend", 0))
    max_mass = float(oligo_cfg.get("max_mass", 2000))
    penalty_per_extend = float(oligo_cfg.get("penalty_per_extend", 0.08))

    if extend_formula_str and max_extend > 0:
        extend_counts = parse_formula(extend_formula_str)
        # Extend each base (parent + fragments), not the already-processed records
        for n in range(1, max_extend + 1):
            extended_bases = []
            for counts, base_type, base_path, breaks, atom_indices in bases:
                new_counts = dict(counts)
                for _ in range(n):
                    new_counts = add_formula(new_counts, extend_counts)
                mass = exact_mass(new_counts)
                if mass > max_mass:
                    continue
                ext_path = [f"{base_path[0]} + {n}×repeat"]
                gen_type = "oligomer" if base_type == "parent" else base_type
                extended_bases.append((new_counts, gen_type, ext_path, breaks, atom_indices))

            if not extended_bases:
                break  # all bases exceeded max_mass, stop extending

            ext_records = process_base_records(
                row, extended_bases, config, _record,
                extend_penalty=penalty_per_extend * n,
            )
            # Mark generation type for parent-extended records
            for rec in ext_records:
                if rec.generation_type == "parent":
                    rec.generation_type = "oligomer"
            records.extend(ext_records)

    # ── Dimers ──────────────────────────────────────────────────────────
    records.extend(generate_dimer_records(row, parent_counts, config, _record))
    base_counts = [counts for counts, _, _, _, _ in bases]
    for candidate in generate_rule_pack_candidates(row, parent_counts, base_counts, config):
        records.append(
            _record(
                row,
                candidate.counts,
                candidate.ion_mode,
                candidate.charge,
                candidate.generation_type,
                candidate.path,
                config,
            )
        )

    return merge_duplicate_formula_records(records)


def merge_duplicate_formula_records(records: list[FormulaRecord]) -> list[FormulaRecord]:
    by_key: dict[tuple[str, str, str], FormulaRecord] = {}
    for record in records:
        key = (record.formula, record.ion_mode, record.generation_type)
        existing = by_key.get(key)
        if existing is None or record.score > existing.score:
            by_key[key] = record
        elif existing and len(existing.path) < 9:
            existing.path += [";"] + record.path
    return sorted(by_key.values(), key=lambda r: (-r.score, r.formula))


def write_network_json(records: list[FormulaRecord], path: Path, compound_row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "compound_id": str(compound_row["compound_id"]),
        "name": str(compound_row["name"]),
        "smiles": str(compound_row["smiles"]),
        "parent_formula": str(compound_row.get("formula", "")),
        "records": [asdict(record) for record in records],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_network_csv(records: list[FormulaRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([{**asdict(record), "path": " | ".join(record.path), "neutral_losses": ";".join(record.neutral_losses)} for record in records]).to_csv(path, index=False)
