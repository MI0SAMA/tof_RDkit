from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from itertools import combinations
from pathlib import Path
from typing import Any

import pandas as pd

from .formula import add_formula, exact_mass, format_formula, parse_formula, subtract_formula
from .feature_rules_v2 import generate_feature_rule_candidates
from .fragmentation import Fragment, generate_fragments
from .molecule_io import get_formula_from_mol, mol_from_smiles
from .scoring import clip


@dataclass
class NetworkNode:
    node_id: str
    compound_id: str
    source_name: str
    formula: str
    counts: dict[str, int]
    exact_mass: float
    ion_mode: str
    charge: int
    generation_type: str
    operation: str
    path: list[str]
    source_nodes: list[str] = field(default_factory=list)
    fragment_atom_indices: list[int] | None = None
    reaction_site_elements: list[str] = field(default_factory=list)
    broken_bonds: int = 0
    h_shift: int = 0
    recombination_loss: str = ""
    rule_pack: str = ""
    trigger_feature: str = ""
    evidence: str = ""
    structure_score: float = 0.0
    ionization_score: float = 0.0
    path_score: float = 0.0
    formula_score: float = 0.0
    path_count: int = 1
    mechanism_count: int = 1
    source_fragment_count: int = 0


@dataclass
class NetworkEdge:
    edge_id: str
    compound_id: str
    source_node: str
    target_node: str
    operation: str
    operation_type: str
    weight: float = 1.0


@dataclass
class FormulaSummary:
    compound_id: str
    source_name: str
    formula: str
    ion_mode: str
    charge: int
    exact_mass: float
    formula_score: float
    best_path_score: float
    path_count: int
    mechanism_count: int
    source_fragment_count: int
    generation_types: str
    best_node_id: str
    representative_path: str
    all_node_ids: str


def _cfg(config: dict) -> dict[str, Any]:
    return config.get("network_v2", {})


def _score_cfg(config: dict) -> dict[str, Any]:
    return _cfg(config).get("scoring", {})


def _next_id(prefix: str, counters: dict[str, int]) -> str:
    counters[prefix] = counters.get(prefix, 0) + 1
    return f"{prefix}_{counters[prefix]:04d}"


def _source_fragment_key(node: NetworkNode) -> str:
    if node.fragment_atom_indices:
        return ",".join(str(idx) for idx in sorted(node.fragment_atom_indices))
    if node.generation_type == "recombination":
        return "+".join(node.source_nodes)
    return node.node_id


def _apply_h_shift(counts: dict[str, int], shift: int) -> dict[str, int] | None:
    if shift == 0:
        return dict(counts)
    result = dict(counts)
    result["H"] = result.get("H", 0) + shift
    if result["H"] < 0:
        return None
    return {element: count for element, count in result.items() if count}


def _ionization_variants(counts: dict[str, int], config: dict, allow_proton_transfer: bool = True) -> list[tuple[str, str, int, dict[str, int], int]]:
    ion_cfg = _cfg(config).get("ionization", {})
    variants: list[tuple[str, str, int, dict[str, int], int]] = []
    if ion_cfg.get("electron_loss", True):
        variants.append(("electron_loss", "positive", 1, dict(counts), 0))
    if ion_cfg.get("electron_gain", True):
        variants.append(("electron_gain", "negative", -1, dict(counts), 0))
    if allow_proton_transfer and ion_cfg.get("protonation", True):
        protonated = add_formula(counts, {"H": 1})
        variants.append(("protonation", "positive", 1, protonated, 1))
    if allow_proton_transfer and ion_cfg.get("deprotonation", True):
        deprotonated = subtract_formula(counts, {"H": 1})
        if deprotonated is not None:
            variants.append(("deprotonation", "negative", -1, deprotonated, -1))
    return variants


def _structure_score(generation_type: str, broken_bonds: int, config: dict) -> float:
    scoring = _score_cfg(config)
    base = scoring.get("structure_scores", {}).get(generation_type, 0.5)
    penalty = float(scoring.get("penalty_per_broken_bond", 0.08)) * broken_bonds
    return clip(base - penalty, 0.0, 1.0)


def _ionization_score(operation: str, generation_type: str, config: dict) -> float:
    scoring = _score_cfg(config)
    if generation_type == "feature_rule":
        return float(scoring.get("feature_rule_ionization_score", 0.80))
    score = scoring.get("ionization_scores", {}).get(operation, 0.0)
    if generation_type == "parent":
        score -= float(scoring.get("parent_ionization_penalty", 0.18))
    return clip(score, 0.0, 1.0)


def _mass_prior(counts: dict[str, int], config: dict) -> float:
    scoring = _score_cfg(config)
    prior = scoring.get("mass_prior", {})
    mass = exact_mass(counts)
    low = float(prior.get("preferred_min_mass", 25.0))
    high = float(prior.get("preferred_max_mass", 200.0))
    if low <= mass <= high:
        return float(prior.get("preferred_mass_bonus", 0.05))
    high_start = float(prior.get("high_mass_penalty_start", 500.0))
    if mass > high_start:
        penalty = (mass - high_start) / 100.0 * float(prior.get("penalty_per_100_da", 0.02))
        return -min(penalty, float(prior.get("max_high_mass_penalty", 0.15)))
    return 0.0


def _path_score(structure_score: float, ionization_score: float, generation_type: str, h_shift: int, counts: dict[str, int], config: dict) -> float:
    scoring = _score_cfg(config)
    structure_weight = float(scoring.get("structure_weight", 0.60))
    ion_weight = float(scoring.get("ionization_weight", 0.40))
    score = structure_weight * structure_score + ion_weight * ionization_score
    score -= float(scoring.get("penalty_per_h_shift", 0.03)) * abs(h_shift)
    if generation_type == "recombination":
        score -= float(scoring.get("penalty_recombination", 0.06))
    score += _mass_prior(counts, config)
    return clip(score, 0.0, 1.0)


def _add_node(
    nodes: list[NetworkNode],
    counters: dict[str, int],
    row: dict,
    counts: dict[str, int],
    ion_mode: str,
    charge: int,
    generation_type: str,
    operation: str,
    path: list[str],
    config: dict,
    source_nodes: list[str] | None = None,
    fragment_atom_indices: list[int] | None = None,
    reaction_site_elements: list[str] | None = None,
    broken_bonds: int = 0,
    h_shift: int = 0,
    recombination_loss: str = "",
    rule_pack: str = "",
    trigger_feature: str = "",
    evidence: str = "",
) -> NetworkNode:
    node_id = _next_id("node", counters)
    structure = _structure_score(generation_type, broken_bonds, config)
    ionization = _ionization_score(operation, generation_type, config)
    node = NetworkNode(
        node_id=node_id,
        compound_id=str(row["compound_id"]),
        source_name=str(row["name"]),
        formula=format_formula(counts),
        counts=dict(counts),
        exact_mass=exact_mass(counts),
        ion_mode=ion_mode,
        charge=charge,
        generation_type=generation_type,
        operation=operation,
        path=path,
        source_nodes=source_nodes or [],
        fragment_atom_indices=fragment_atom_indices,
        reaction_site_elements=reaction_site_elements or [],
        broken_bonds=broken_bonds,
        h_shift=h_shift,
        recombination_loss=recombination_loss,
        rule_pack=rule_pack,
        trigger_feature=trigger_feature,
        evidence=evidence,
        structure_score=structure,
        ionization_score=ionization,
        path_score=_path_score(structure, ionization, generation_type, h_shift, counts, config),
    )
    nodes.append(node)
    return node


def _add_edge(
    edges: list[NetworkEdge],
    counters: dict[str, int],
    compound_id: str,
    source_node: str,
    target_node: str,
    operation: str,
    operation_type: str,
    weight: float = 1.0,
) -> None:
    edges.append(
        NetworkEdge(
            edge_id=_next_id("edge", counters),
            compound_id=compound_id,
            source_node=source_node,
            target_node=target_node,
            operation=operation,
            operation_type=operation_type,
            weight=weight,
        )
    )


def _dedupe_fragments(fragments: list[Fragment]) -> list[Fragment]:
    by_key: dict[tuple[str, tuple[int, ...]], Fragment] = {}
    for fragment in fragments:
        key = (format_formula(fragment.counts), tuple(sorted(fragment.atom_indices)))
        if key not in by_key:
            by_key[key] = fragment
    return list(by_key.values())


def _generate_fragment_nodes(
    row: dict,
    fragments: list[Fragment],
    parent_node: NetworkNode,
    nodes: list[NetworkNode],
    edges: list[NetworkEdge],
    counters: dict[str, int],
    config: dict,
) -> list[NetworkNode]:
    out: list[NetworkNode] = []
    for fragment in fragments:
        node = _add_node(
            nodes,
            counters,
            row,
            fragment.counts,
            "neutral",
            0,
            "fragment",
            "bond_break",
            parent_node.path + [f"break {fragment.broken_bonds} bond(s)"],
            config,
            source_nodes=[parent_node.node_id],
            fragment_atom_indices=fragment.atom_indices,
            reaction_site_elements=fragment.boundary_elements or [],
            broken_bonds=fragment.broken_bonds,
        )
        _add_edge(edges, counters, str(row["compound_id"]), parent_node.node_id, node.node_id, "bond_break", "fragmentation")
        out.append(node)
    return out


def _generate_feature_rule_nodes(
    row: dict,
    mol,
    parent_counts: dict[str, int],
    nodes: list[NetworkNode],
    edges: list[NetworkEdge],
    counters: dict[str, int],
    config: dict,
    parent_node: NetworkNode,
) -> list[NetworkNode]:
    out: list[NetworkNode] = []
    for candidate in generate_feature_rule_candidates(mol, parent_counts, config):
        node = _add_node(
            nodes,
            counters,
            row,
            candidate.counts,
            candidate.ion_mode,
            candidate.charge,
            "feature_rule",
            candidate.operation,
            ["M", candidate.trigger_feature, candidate.rule_pack, candidate.operation],
            config,
            source_nodes=[parent_node.node_id],
            rule_pack=candidate.rule_pack,
            trigger_feature=candidate.trigger_feature,
            evidence=candidate.evidence,
        )
        _add_edge(edges, counters, str(row["compound_id"]), parent_node.node_id, node.node_id, candidate.operation, "feature_rule", 0.7)
        out.append(node)
    return out


def _generate_fragment_h_shift_nodes(
    row: dict,
    fragment_nodes: list[NetworkNode],
    nodes: list[NetworkNode],
    edges: list[NetworkEdge],
    counters: dict[str, int],
    config: dict,
) -> list[NetworkNode]:
    h_cfg = _cfg(config).get("fragment_h_shift", {})
    if not h_cfg.get("enabled", True):
        return []
    shifts = [int(shift) for shift in h_cfg.get("shifts", [-1, 1]) if int(shift) != 0]
    out: list[NetworkNode] = []
    for fragment in fragment_nodes:
        for shift in shifts:
            counts = _apply_h_shift(fragment.counts, shift)
            if counts is None:
                continue
            operation = f"h_shift_{shift:+d}"
            node = _add_node(
                nodes,
                counters,
                row,
                counts,
                "neutral",
                0,
                "fragment_h_shift",
                operation,
                fragment.path + [operation],
                config,
                source_nodes=[fragment.node_id],
                fragment_atom_indices=fragment.fragment_atom_indices,
                reaction_site_elements=fragment.reaction_site_elements,
                broken_bonds=fragment.broken_bonds,
                h_shift=shift,
            )
            _add_edge(edges, counters, str(row["compound_id"]), fragment.node_id, node.node_id, operation, "h_shift", 0.9)
            out.append(node)
    return out


def _generate_ion_nodes(
    row: dict,
    bases: list[NetworkNode],
    nodes: list[NetworkNode],
    edges: list[NetworkEdge],
    counters: dict[str, int],
    config: dict,
) -> None:
    for base in bases:
        allow_proton_transfer = base.generation_type != "fragment_h_shift"
        for operation, mode, charge, counts, ion_h_shift in _ionization_variants(base.counts, config, allow_proton_transfer):
            node = _add_node(
                nodes,
                counters,
                row,
                counts,
                mode,
                charge,
                base.generation_type,
                operation,
                base.path + [operation],
                config,
                source_nodes=[base.node_id],
                fragment_atom_indices=base.fragment_atom_indices,
                reaction_site_elements=base.reaction_site_elements,
                broken_bonds=base.broken_bonds,
                h_shift=base.h_shift + ion_h_shift,
                recombination_loss=base.recombination_loss,
            )
            _add_edge(edges, counters, str(row["compound_id"]), base.node_id, node.node_id, operation, "ionization")


def _original_fragment_key(node: NetworkNode) -> str:
    if node.fragment_atom_indices:
        return ",".join(str(idx) for idx in sorted(node.fragment_atom_indices))
    return node.node_id


def _allowed_h_shift_pair(left: NetworkNode, right: NetworkNode, recomb_cfg: dict) -> str | None:
    pair = tuple(sorted((left.h_shift, right.h_shift)))
    labels = {
        (-1, -1): "dehydrogenative_coupling",
        (-1, 0): "single_dehydrogenative_recombination",
        (-1, 1): "h_transfer_recombination",
        (0, 0): "neutral_fragment_association",
    }
    allowed = {tuple(pair) for pair in recomb_cfg.get("allowed_h_shift_pairs", [[-1, -1], [-1, 0], [-1, 1]])}
    if pair not in allowed:
        return None
    return labels.get(pair, "fragment_recombination")


def _site_compatible(left: NetworkNode, right: NetworkNode, recomb_cfg: dict) -> bool:
    if not recomb_cfg.get("require_site_compatibility", True):
        return True
    left_sites = left.reaction_site_elements
    right_sites = right.reaction_site_elements
    if not left_sites or not right_sites:
        return False
    allowed = {tuple(sorted(pair)) for pair in recomb_cfg.get("allowed_site_pairs", [["C", "C"], ["C", "O"], ["C", "N"], ["C", "S"], ["Si", "O"]])}
    for left_site in left_sites:
        for right_site in right_sites:
            if tuple(sorted((left_site, right_site))) in allowed:
                return True
    return False


def _generate_recombination_nodes(
    row: dict,
    fragment_nodes: list[NetworkNode],
    nodes: list[NetworkNode],
    edges: list[NetworkEdge],
    counters: dict[str, int],
    config: dict,
) -> list[NetworkNode]:
    recomb_cfg = _cfg(config).get("recombination", {})
    if not recomb_cfg.get("enabled", True):
        return []
    max_pairs = int(recomb_cfg.get("max_pairs", 5000))
    max_mass = float(recomb_cfg.get("max_mass", 2000.0))
    out: list[NetworkNode] = []
    pair_count = 0
    seen: set[tuple[str, str, str]] = set()
    for left, right in combinations(fragment_nodes, 2):
        if _original_fragment_key(left) == _original_fragment_key(right):
            continue
        operation = _allowed_h_shift_pair(left, right, recomb_cfg)
        if operation is None or not _site_compatible(left, right, recomb_cfg):
            continue
        pair_count += 1
        if pair_count > max_pairs:
            break
        counts = add_formula(left.counts, right.counts)
        if exact_mass(counts) > max_mass:
            continue
        key = (left.node_id, right.node_id, format_formula(counts))
        if key in seen:
            continue
        seen.add(key)
        node = _add_node(
            nodes,
            counters,
            row,
            counts,
            "neutral",
            0,
            "recombination",
            operation,
            [" + ".join([left.node_id, right.node_id]), operation],
            config,
            source_nodes=[left.node_id, right.node_id],
            reaction_site_elements=sorted(set(left.reaction_site_elements + right.reaction_site_elements)),
            broken_bonds=left.broken_bonds + right.broken_bonds,
            h_shift=left.h_shift + right.h_shift,
            recombination_loss={-2: "H2", -1: "H", 0: ""}.get(left.h_shift + right.h_shift, ""),
        )
        _add_edge(edges, counters, str(row["compound_id"]), left.node_id, node.node_id, operation, "recombination", 0.8)
        _add_edge(edges, counters, str(row["compound_id"]), right.node_id, node.node_id, operation, "recombination", 0.8)
        out.append(node)
    return out


def summarize_formula_nodes(nodes: list[NetworkNode], config: dict) -> list[FormulaSummary]:
    scoring = _score_cfg(config)
    max_score = float(scoring.get("max_score", 1.0))
    path_bonus = scoring.get("path_support_bonus", {"2": 0.05, "3": 0.08, "4": 0.10})
    mech_bonus = scoring.get("mechanism_diversity_bonus", {"2": 0.05, "3": 0.08})
    source_bonus = scoring.get("source_fragment_diversity_bonus", {"2": 0.04, "3": 0.07})

    def bonus(table: dict[str, float], count: int) -> float:
        if count <= 1:
            return 0.0
        best = 0.0
        for key, value in table.items():
            if count >= int(key):
                best = float(value)
        return best

    grouped: dict[tuple[str, str, int], list[NetworkNode]] = {}
    for node in nodes:
        if node.ion_mode == "neutral":
            continue
        grouped.setdefault((node.formula, node.ion_mode, node.charge), []).append(node)

    summaries: list[FormulaSummary] = []
    formula_scores: dict[tuple[str, str, int], tuple[float, int, int, int]] = {}
    for (formula, ion_mode, charge), group in grouped.items():
        best = max(group, key=lambda node: node.path_score)
        mechanisms = {node.generation_type for node in group}
        sources = {_source_fragment_key(node) for node in group}
        path_count = len(group)
        mechanism_count = len(mechanisms)
        source_count = len(sources)
        formula_score = clip(
            best.path_score
            + bonus(path_bonus, path_count)
            + bonus(mech_bonus, mechanism_count)
            + bonus(source_bonus, source_count),
            0.0,
            max_score,
        )
        formula_scores[(formula, ion_mode, charge)] = (formula_score, path_count, mechanism_count, source_count)
        summaries.append(
            FormulaSummary(
                compound_id=best.compound_id,
                source_name=best.source_name,
                formula=formula,
                ion_mode=ion_mode,
                charge=charge,
                exact_mass=best.exact_mass,
                formula_score=formula_score,
                best_path_score=best.path_score,
                path_count=path_count,
                mechanism_count=mechanism_count,
                source_fragment_count=source_count,
                generation_types=";".join(sorted(mechanisms)),
                best_node_id=best.node_id,
                representative_path=" | ".join(best.path),
                all_node_ids=";".join(node.node_id for node in group),
            )
        )

    for node in nodes:
        key = (node.formula, node.ion_mode, node.charge)
        if key in formula_scores:
            node.formula_score, node.path_count, node.mechanism_count, node.source_fragment_count = formula_scores[key]

    return sorted(summaries, key=lambda item: (-item.formula_score, item.formula))


def generate_formula_network_v2(compound_row, config: dict) -> tuple[list[NetworkNode], list[NetworkEdge], list[FormulaSummary]]:
    row = dict(compound_row)
    mol = mol_from_smiles(row["smiles"])
    parent_formula = row.get("formula") or get_formula_from_mol(mol)
    parent_counts = parse_formula(parent_formula)
    counters: dict[str, int] = {}
    nodes: list[NetworkNode] = []
    edges: list[NetworkEdge] = []

    parent = _add_node(
        nodes,
        counters,
        row,
        parent_counts,
        "neutral",
        0,
        "parent",
        "source_molecule",
        ["M"],
        config,
    )
    fragments = _dedupe_fragments(generate_fragments(mol, config))
    max_fragments = int(_cfg(config).get("max_fragment_nodes", 300))
    fragment_nodes = _generate_fragment_nodes(row, fragments[:max_fragments], parent, nodes, edges, counters, config)
    h_shift_nodes = _generate_fragment_h_shift_nodes(row, fragment_nodes, nodes, edges, counters, config)
    recombination_pool = [*fragment_nodes, *h_shift_nodes]
    recombination_nodes = _generate_recombination_nodes(row, recombination_pool, nodes, edges, counters, config)
    _generate_feature_rule_nodes(row, mol, parent_counts, nodes, edges, counters, config, parent)
    _generate_ion_nodes(row, [parent, *fragment_nodes, *h_shift_nodes, *recombination_nodes], nodes, edges, counters, config)
    summaries = summarize_formula_nodes(nodes, config)
    return nodes, edges, summaries


def _frame(records: list[Any]) -> pd.DataFrame:
    rows = []
    for record in records:
        row = asdict(record)
        if "path" in row:
            row["path"] = " | ".join(row["path"])
        if "source_nodes" in row:
            row["source_nodes"] = ";".join(row["source_nodes"])
        if "fragment_atom_indices" in row:
            indices = row["fragment_atom_indices"]
            row["fragment_atom_indices"] = "" if indices is None else ";".join(str(idx) for idx in indices)
        if "reaction_site_elements" in row:
            row["reaction_site_elements"] = ";".join(row["reaction_site_elements"])
        if "counts" in row:
            row["counts"] = json.dumps(row["counts"], sort_keys=True)
        rows.append(row)
    return pd.DataFrame(rows)


def write_network_v2(nodes: list[NetworkNode], edges: list[NetworkEdge], summaries: list[FormulaSummary], output_dir: Path, compound_row: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_id = str(compound_row["compound_id"]).replace("/", "_")
    _frame(nodes).to_csv(output_dir / f"{safe_id}_nodes.csv", index=False, encoding="utf-8-sig")
    _frame(edges).to_csv(output_dir / f"{safe_id}_edges.csv", index=False, encoding="utf-8-sig")
    _frame(summaries).to_csv(output_dir / f"{safe_id}_formula_summary.csv", index=False, encoding="utf-8-sig")
    payload = {
        "compound_id": str(compound_row["compound_id"]),
        "name": str(compound_row["name"]),
        "smiles": str(compound_row["smiles"]),
        "parent_formula": str(compound_row.get("formula", "")),
        "nodes": [asdict(node) for node in nodes],
        "edges": [asdict(edge) for edge in edges],
        "formula_summary": [asdict(summary) for summary in summaries],
    }
    (output_dir / f"{safe_id}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
