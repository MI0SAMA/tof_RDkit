from __future__ import annotations

from dataclasses import dataclass

from rdkit import Chem

from .formula import exact_mass, parse_formula


@dataclass(frozen=True)
class FeatureRuleCandidate:
    counts: dict[str, int]
    ion_mode: str
    charge: int
    rule_pack: str
    trigger_feature: str
    operation: str
    evidence: str


def _element_counts(mol: Chem.Mol) -> dict[str, int]:
    counts: dict[str, int] = {}
    for atom in mol.GetAtoms():
        symbol = atom.GetSymbol()
        counts[symbol] = counts.get(symbol, 0) + 1
    return counts


def _has_c_f_bond(mol: Chem.Mol) -> bool:
    for bond in mol.GetBonds():
        symbols = {bond.GetBeginAtom().GetSymbol(), bond.GetEndAtom().GetSymbol()}
        if symbols == {"C", "F"}:
            return True
    return False


def _has_aromatic_ring(mol: Chem.Mol) -> bool:
    return any(atom.GetIsAromatic() for atom in mol.GetAtoms())


def _has_aromatic_sulfur(mol: Chem.Mol) -> bool:
    for atom in mol.GetAtoms():
        if atom.GetSymbol() != "S":
            continue
        if any(neighbor.GetIsAromatic() for neighbor in atom.GetNeighbors()):
            return True
    return False


def _has_acetal_or_ether(mol: Chem.Mol) -> bool:
    patterns = [
        Chem.MolFromSmarts("[OX2]-[CX4]-[OX2]"),
        Chem.MolFromSmarts("[CX4]-[OX2]-[CX4]"),
    ]
    return any(pattern is not None and mol.HasSubstructMatch(pattern) for pattern in patterns)


def detect_structure_features(mol: Chem.Mol) -> dict[str, bool]:
    return {
        "fluorocarbon_motif": _has_c_f_bond(mol),
        "aromatic_ring": _has_aromatic_ring(mol),
        "sulfur_aromatic": _has_aromatic_sulfur(mol),
        "acetal_or_ether": _has_acetal_or_ether(mol),
    }


def _candidate(
    formula: str,
    ion_mode: str,
    charge: int,
    rule_pack: str,
    trigger_feature: str,
    operation: str,
    evidence: str,
) -> FeatureRuleCandidate:
    return FeatureRuleCandidate(parse_formula(formula), ion_mode, charge, rule_pack, trigger_feature, operation, evidence)


def _formula_possible(formula: str, parent_counts: dict[str, int], strict_counts: bool = True) -> bool:
    counts = parse_formula(formula)
    for element, count in counts.items():
        if element == "H":
            continue
        if parent_counts.get(element, 0) <= 0:
            return False
        if strict_counts and parent_counts.get(element, 0) < count:
            return False
    return True


def _add_if_possible(out: list[FeatureRuleCandidate], parent_counts: dict[str, int], formula: str, ion_mode: str, charge: int, rule_pack: str, trigger_feature: str, operation: str, evidence: str, max_mass: float, strict_counts: bool = True) -> None:
    counts = parse_formula(formula)
    if exact_mass(counts) > max_mass:
        return
    if _formula_possible(formula, parent_counts, strict_counts=strict_counts):
        out.append(_candidate(formula, ion_mode, charge, rule_pack, trigger_feature, operation, evidence))


def generate_feature_rule_candidates(mol: Chem.Mol, parent_counts: dict[str, int], config: dict) -> list[FeatureRuleCandidate]:
    cfg = config.get("network_v2", {}).get("feature_rules", {})
    if not cfg.get("enabled", True):
        return []
    features = detect_structure_features(mol)
    parent_elements = _element_counts(mol)
    max_mass = float(cfg.get("max_mass", 220.0))
    out: list[FeatureRuleCandidate] = []

    if features["fluorocarbon_motif"] and cfg.get("fluorocarbon_fragmentation", {}).get("enabled", True):
        evidence = f"C-F bonds present; heavy element counts={parent_elements}"
        for formula, ion_mode, charge in [
            ("F", "negative", -1),
            ("CF", "positive", 1),
            ("CF2", "positive", 1),
            ("CF3", "positive", 1),
            ("CF3", "negative", -1),
            ("C2F3", "positive", 1),
            ("C2F3", "negative", -1),
            ("C2F4", "positive", 1),
            ("C2F4", "negative", -1),
            ("C2F5", "positive", 1),
            ("C3F5", "positive", 1),
            ("C3F7", "positive", 1),
        ]:
            _add_if_possible(out, parent_counts, formula, ion_mode, charge, "fluorocarbon_fragmentation", "fluorocarbon_motif", f"diagnostic_{formula}", evidence, max_mass)

    if features["acetal_or_ether"] and cfg.get("acetal_oxonium_series", {}).get("enabled", True):
        evidence = f"acetal/ether C-O-C motif present; heavy element counts={parent_elements}"
        for formula in ["CH3O", "C2H5O", "C2H5O2", "C3H7O2", "C3H7O3"]:
            _add_if_possible(out, parent_counts, formula, "positive", 1, "acetal_oxonium_series", "acetal_or_ether", f"oxonium_{formula}", evidence, max_mass, strict_counts=False)

    if features["aromatic_ring"] and cfg.get("aromatic_stable_fragments", {}).get("enabled", True):
        evidence = f"aromatic atoms present; heavy element counts={parent_elements}"
        for formula, ion_mode, charge in [
            ("C6H5", "positive", 1),
            ("C6H5", "negative", -1),
            ("C7H7", "positive", 1),
            ("C6H5O", "positive", 1),
            ("C6H5O", "negative", -1),
        ]:
            _add_if_possible(out, parent_counts, formula, ion_mode, charge, "aromatic_stable_fragments", "aromatic_ring", f"aromatic_{formula}", evidence, max_mass)

    if features["sulfur_aromatic"] and cfg.get("sulfur_aromatic_fragments", {}).get("enabled", True):
        evidence = f"sulfur attached to aromatic environment; heavy element counts={parent_elements}"
        for formula, ion_mode, charge in [
            ("S", "negative", -1),
            ("HS", "negative", -1),
            ("CS", "negative", -1),
            ("C6H5S", "positive", 1),
            ("C6H5S", "negative", -1),
            ("C6H4S", "negative", -1),
            ("C6H6S", "positive", 1),
        ]:
            _add_if_possible(out, parent_counts, formula, ion_mode, charge, "sulfur_aromatic_fragments", "sulfur_aromatic", f"sulfur_aromatic_{formula}", evidence, max_mass)

    by_key: dict[tuple[str, str, str], FeatureRuleCandidate] = {}
    for candidate in out:
        key = (str(candidate.counts), candidate.ion_mode, candidate.operation)
        by_key[key] = candidate
    return list(by_key.values())
