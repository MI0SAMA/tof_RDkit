from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from itertools import combinations
from pathlib import Path

import pandas as pd
from rdkit import Chem

from .formula import add_formula, exact_mass, format_formula, parse_formula, subtract_formula
from .molecule_io import get_formula_from_mol, mol_from_smiles
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


def _apply_h_shift(counts: dict[str, int], shift: int) -> dict[str, int] | None:
    if shift == 0:
        return dict(counts)
    result = dict(counts)
    result["H"] = result.get("H", 0) + shift
    if result["H"] < 0:
        return None
    return {element: count for element, count in result.items() if count}


def _adduct_counts(adduct: str) -> tuple[dict[str, int], bool]:
    if adduct.startswith("-"):
        return parse_formula(adduct[1:]), False
    return parse_formula(adduct), True


def _apply_adduct(counts: dict[str, int], adduct: str) -> dict[str, int] | None:
    change, is_add = _adduct_counts(adduct)
    return add_formula(counts, change) if is_add else subtract_formula(counts, change)


def _fragment_counts(mol: Chem.Mol, atom_indices: tuple[int, ...]) -> dict[str, int]:
    counts: dict[str, int] = {}
    atoms = set(atom_indices)
    for idx in atoms:
        atom = mol.GetAtomWithIdx(idx)
        symbol = atom.GetSymbol()
        counts[symbol] = counts.get(symbol, 0) + 1
    return counts


def _generate_fragments(mol: Chem.Mol, cfg: dict) -> list[tuple[dict[str, int], list[int], int]]:
    frag_cfg = cfg["fragmentation"]
    breakable = []
    for bond in mol.GetBonds():
        begin = bond.GetBeginAtom()
        end = bond.GetEndAtom()
        if begin.GetAtomicNum() == 1 or end.GetAtomicNum() == 1:
            continue
        if bond.GetBondType() != Chem.BondType.SINGLE:
            continue
        if bond.IsInRing() and not frag_cfg["allow_ring_bond_break"]:
            continue
        if bond.GetIsAromatic() and not frag_cfg["allow_aromatic_bond_break"]:
            continue
        breakable.append(bond.GetIdx())

    fragments = []
    for k in range(1, int(frag_cfg["max_bond_breaks"]) + 1):
        for combo in combinations(breakable, k):
            frag_mol = Chem.FragmentOnBonds(mol, list(combo), addDummies=False)
            for atoms in Chem.GetMolFrags(frag_mol, asMols=False, sanitizeFrags=False):
                heavy_count = sum(1 for idx in atoms if mol.GetAtomWithIdx(idx).GetAtomicNum() > 1)
                if heavy_count < frag_cfg["min_heavy_atoms_per_fragment"]:
                    continue
                fragments.append((_fragment_counts(mol, tuple(atoms)), list(atoms), k))
                if len(fragments) >= frag_cfg["max_generated_formulas_per_compound"]:
                    return fragments
    return fragments


def _process_base_records(row: dict, bases: list[tuple], config: dict, extend_penalty: float = 0.0) -> list[FormulaRecord]:
    """Generate FormulaRecords from base (counts, type, path, breaks, atoms) tuples.

    If extend_penalty > 0, score is reduced (for oligomer-extended bases).
    """
    records: list[FormulaRecord] = []
    for counts, base_type, base_path, breaks, atom_indices in bases:
        for shift in config["ion_rules"]["h_shift_range"]:
            shifted = _apply_h_shift(counts, int(shift))
            if shifted is None:
                continue
            path = base_path + ([f"H shift {shift:+d}"] if shift else [])
            gen_type = base_type if shift == 0 else "h_shift"
            rec = _record(row, shifted, "neutral", 0, gen_type, path, config,
                          broken_bonds=breaks, h_shift=shift, fragment_atom_indices=atom_indices)
            if extend_penalty:
                rec.score = max(0.0, rec.score - extend_penalty)
            records.append(rec)

            for mode, charge, adducts in [
                ("positive", 1, config["ion_rules"]["common_adducts_positive"]),
                ("negative", -1, config["ion_rules"]["common_adducts_negative"]),
            ]:
                for adduct in adducts:
                    adducted = _apply_adduct(shifted, adduct)
                    if adducted is None:
                        continue
                    rec2 = _record(row, adducted, mode, charge, "adduct", path + [adduct], config,
                                   broken_bonds=breaks, h_shift=shift, adduct=adduct, fragment_atom_indices=atom_indices)
                    if extend_penalty:
                        rec2.score = max(0.0, rec2.score - extend_penalty)
                    records.append(rec2)

            for loss in config["ion_rules"]["neutral_losses"]:
                lost = subtract_formula(shifted, parse_formula(loss))
                if lost is not None:
                    rec3 = _record(row, lost, "neutral", 0, "neutral_loss", path + [f"-{loss}"], config,
                                   broken_bonds=breaks, h_shift=shift, neutral_losses=[loss], fragment_atom_indices=atom_indices)
                    if extend_penalty:
                        rec3.score = max(0.0, rec3.score - extend_penalty)
                    records.append(rec3)
    return records


def generate_formula_network(compound_row, config: dict) -> list[FormulaRecord]:
    row = dict(compound_row)
    mol = mol_from_smiles(row["smiles"])
    parent_formula = row.get("formula") or get_formula_from_mol(mol)
    parent_counts = parse_formula(parent_formula)
    bases = [(parent_counts, "parent", ["M"], 0, None)]
    for counts, atom_indices, breaks in _generate_fragments(mol, config):
        bases.append((counts, "fragment", [f"break {breaks} bond(s)"], breaks, atom_indices))

    records = _process_base_records(row, bases, config)

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

            ext_records = _process_base_records(
                row, extended_bases, config,
                extend_penalty=penalty_per_extend * n,
            )
            # Mark generation type for parent-extended records
            for rec in ext_records:
                if rec.generation_type == "parent":
                    rec.generation_type = "oligomer"
            records.extend(ext_records)

    # ── Dimers ──────────────────────────────────────────────────────────
    if config["ion_rules"].get("dimers", True):
        doubled = add_formula(parent_counts, parent_counts)
        for adduct, mode, charge in [("H", "positive", 1), ("Na", "positive", 1), ("-H", "negative", -1), ("Cl", "negative", -1)]:
            counts = _apply_adduct(doubled, adduct)
            if counts is not None:
                records.append(_record(row, counts, mode, charge, "dimer", ["2M", adduct], config, adduct=adduct))

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
