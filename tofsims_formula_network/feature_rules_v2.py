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


def _has_carbonyl(mol: Chem.Mol) -> bool:
    pattern = Chem.MolFromSmarts("[#6]=[OX1]")
    return pattern is not None and mol.HasSubstructMatch(pattern)


def _has_imide(mol: Chem.Mol) -> bool:
    pattern = Chem.MolFromSmarts("[#7;D3]([#6]=[OX1])([#6]=[OX1])")
    return pattern is not None and mol.HasSubstructMatch(pattern)


def _has_amide(mol: Chem.Mol) -> bool:
    pattern = Chem.MolFromSmarts("[#7;D3][#6](=[OX1])")
    return pattern is not None and mol.HasSubstructMatch(pattern)


def _has_cyclic_aliphatic(mol: Chem.Mol) -> bool:
    ring_info = mol.GetRingInfo()
    for ring in ring_info.AtomRings():
        if any(mol.GetAtomWithIdx(idx).GetIsAromatic() for idx in ring):
            continue
        return True
    return False


def detect_structure_features(mol: Chem.Mol) -> dict[str, bool]:
    return {
        "fluorocarbon_motif": _has_c_f_bond(mol),
        "aromatic_ring": _has_aromatic_ring(mol),
        "sulfur_aromatic": _has_aromatic_sulfur(mol),
        "acetal_or_ether": _has_acetal_or_ether(mol),
        "carbonyl": _has_carbonyl(mol),
        "imide": _has_imide(mol),
        "amide": _has_amide(mol),
        "cyclic_aliphatic": _has_cyclic_aliphatic(mol),
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


def _generate_carbonyl_fragments(features: dict[str, bool], parent_counts: dict[str, int], parent_elements: dict[str, int], cfg: dict, max_mass: float) -> list[FeatureRuleCandidate]:
    out: list[FeatureRuleCandidate] = []
    if not features.get("carbonyl") or not cfg.get("carbonyl_fragmentation", {}).get("enabled", True):
        return out
    evidence = f"C=O carbonyl detected; heavy element counts={parent_elements}"
    for formula, ion_mode, charge in [
        ("CO", "positive", 1),
        ("HCO", "positive", 1),
        ("C2H3O", "positive", 1),
        ("C2HO", "positive", 1),
        ("CO2", "positive", 1),
        ("CHO2", "positive", 1),
        ("C3H3O", "positive", 1),
        ("C3H5O", "positive", 1),
        ("CO", "negative", -1),
        ("C2O", "negative", -1),
        ("C2HO", "negative", -1),
    ]:
        _add_if_possible(out, parent_counts, formula, ion_mode, charge, "carbonyl_fragmentation", "carbonyl", f"carbonyl_{formula}", evidence, max_mass)
    return out


def _generate_imide_fragments(features: dict[str, bool], parent_counts: dict[str, int], parent_elements: dict[str, int], cfg: dict, max_mass: float) -> list[FeatureRuleCandidate]:
    out: list[FeatureRuleCandidate] = []
    if not features.get("imide") or not cfg.get("imide_fragmentation", {}).get("enabled", True):
        return out
    evidence = f"imide O=C-N-C=O detected; heavy element counts={parent_elements}"
    for formula, ion_mode, charge in [
        ("NCO", "negative", -1),
        ("CNO", "negative", -1),
        ("HCN", "positive", 1),
        ("C2H2NO", "positive", 1),
        ("C7H4NO2", "positive", 1),
        ("C6H4NO", "positive", 1),
    ]:
        _add_if_possible(out, parent_counts, formula, ion_mode, charge, "imide_fragmentation", "imide", f"imide_{formula}", evidence, max_mass)
    return out


def _generate_amide_fragments(features: dict[str, bool], parent_counts: dict[str, int], parent_elements: dict[str, int], cfg: dict, max_mass: float) -> list[FeatureRuleCandidate]:
    out: list[FeatureRuleCandidate] = []
    if not features.get("amide") or not cfg.get("amide_fragmentation", {}).get("enabled", True):
        return out
    evidence = f"amide N-C=O detected; heavy element counts={parent_elements}"
    for formula, ion_mode, charge in [
        ("CH2NO", "positive", 1),
        ("CH4N", "positive", 1),
        ("C2H2NO", "positive", 1),
        ("C2H4NO", "positive", 1),
        ("C6H6N", "positive", 1),
        ("CNO", "negative", -1),
    ]:
        _add_if_possible(out, parent_counts, formula, ion_mode, charge, "amide_fragmentation", "amide", f"amide_{formula}", evidence, max_mass)
    return out


def _generate_hydrocarbon_small_fragments(features: dict[str, bool], parent_counts: dict[str, int], parent_elements: dict[str, int], cfg: dict, max_mass: float) -> list[FeatureRuleCandidate]:
    """Universal C2-C6 small hydrocarbon fragments.

    These are TOF-SIMS secondary fragments that RDKit bond-breaking cannot
    generate because they require 3+ sequential bond breaks.  They are
    near-universal in polymer spectra and explain the dominant missing-peak
    category across all materials.

    Design:
    - Triggered for any organic material (has C)
    - Generates C2-C6 hydrocarbon cations and carbon-cluster anions
    - Mass range 25-100 Da (configured via max_mass)
    - Lower structure_score than material-specific feature rules
    """
    out: list[FeatureRuleCandidate] = []
    if not cfg.get("hydrocarbon_small_fragments", {}).get("enabled", True):
        return out
    if parent_counts.get("C", 0) <= 0:
        return out

    evidence = f"universal TOF-SIMS small HC fragments; parent C={parent_counts.get('C', 0)}"

    # Positive: common hydrocarbon cations C2-C6
    for formula in [
        "C2H3", "C2H5",
        "C3H3", "C3H5", "C3H7",
        "C4H3", "C4H5", "C4H7", "C4H9",
        "C5H5", "C5H7", "C5H9", "C5H11",
        "C6H5", "C6H7", "C6H9", "C6H11",
    ]:
        _add_if_possible(out, parent_counts, formula, "positive", 1,
                         "hydrocarbon_small_fragments", "universal_hydrocarbon",
                         f"small_hc_{formula}", evidence, max_mass)

    # Negative: carbon cluster anions C2-C6
    for formula in [
        "C2", "C2H",
        "C3", "C3H",
        "C4", "C4H",
        "C5", "C5H",
        "C6", "C6H",
    ]:
        _add_if_possible(out, parent_counts, formula, "negative", -1,
                         "hydrocarbon_small_fragments", "universal_hydrocarbon",
                         f"small_hc_{formula}", evidence, max_mass)

    return out


def _generate_oxygenated_small_fragments(features: dict[str, bool], parent_counts: dict[str, int], parent_elements: dict[str, int], cfg: dict, max_mass: float) -> list[FeatureRuleCandidate]:
    """O-gated small oxygenated fragments (25-100 Da).

    Triggered when parent contains O.  Generates common TOF-SIMS
    oxygenated small fragments that RDKit bond-breaking cannot reach
    because they require 2+ sequential bond breaks of oxygen-containing
    functional groups.
    """
    out: list[FeatureRuleCandidate] = []
    if not cfg.get("oxygenated_small_fragments", {}).get("enabled", True):
        return out
    if parent_counts.get("O", 0) <= 0:
        return out

    evidence = f"O-gated small fragments; parent O={parent_counts.get('O', 0)}"

    # Positive: common oxygenated cations C1-C3
    for formula in [
        "CHO", "CH3O",
        "C2H3O", "C2H5O",
        "C3H3O", "C3H5O", "C3H7O",
    ]:
        _add_if_possible(out, parent_counts, formula, "positive", 1,
                         "oxygenated_small_fragments", "oxygenated",
                         f"o_small_{formula}", evidence, max_mass)

    # Positive: di-oxygenated (acetals, esters)
    for formula in [
        "CH3O2", "C2H5O2", "C3H5O2", "C3H7O2",
    ]:
        _add_if_possible(out, parent_counts, formula, "positive", 1,
                         "oxygenated_small_fragments", "oxygenated",
                         f"o_small_{formula}", evidence, max_mass)

    # Negative: common oxygenated anions
    for formula in [
        "CHO", "C2HO", "C2H3O", "CHO2", "C2H3O2",
    ]:
        _add_if_possible(out, parent_counts, formula, "negative", -1,
                         "oxygenated_small_fragments", "oxygenated",
                         f"o_small_{formula}", evidence, max_mass)

    return out


def _generate_nitrogenated_small_fragments(features: dict[str, bool], parent_counts: dict[str, int], parent_elements: dict[str, int], cfg: dict, max_mass: float) -> list[FeatureRuleCandidate]:
    """N-gated small nitrogen-containing fragments (25-100 Da).

    Triggered when parent contains N.  CN- is the single most diagnostic
    negative ion for N-containing polymers in TOF-SIMS.
    """
    out: list[FeatureRuleCandidate] = []
    if not cfg.get("nitrogenated_small_fragments", {}).get("enabled", True):
        return out
    if parent_counts.get("N", 0) <= 0:
        return out

    evidence = f"N-gated small fragments; parent N={parent_counts.get('N', 0)}"

    # Positive: common N-containing cations
    for formula in [
        "CH2N", "CH4N",
        "C2H2N", "C2H4N", "C2H6N",
    ]:
        _add_if_possible(out, parent_counts, formula, "positive", 1,
                         "nitrogenated_small_fragments", "nitrogenated",
                         f"n_small_{formula}", evidence, max_mass)

    # Negative: CN- and carbon-nitrogen cluster anions
    for formula in [
        "CN", "C2N", "C3N",
    ]:
        _add_if_possible(out, parent_counts, formula, "negative", -1,
                         "nitrogenated_small_fragments", "nitrogenated",
                         f"n_small_{formula}", evidence, max_mass)

    return out


def _generate_sulfurated_small_fragments(features: dict[str, bool], parent_counts: dict[str, int], parent_elements: dict[str, int], cfg: dict, max_mass: float) -> list[FeatureRuleCandidate]:
    """S-gated small sulfur-containing fragments (25-100 Da).

    Triggered when parent contains S.  S- and HS- are key negative ions;
    CHS+ and thio-fragments are common in positive mode for S-containing polymers.
    """
    out: list[FeatureRuleCandidate] = []
    if not cfg.get("sulfurated_small_fragments", {}).get("enabled", True):
        return out
    if parent_counts.get("S", 0) <= 0:
        return out

    evidence = f"S-gated small fragments; parent S={parent_counts.get('S', 0)}"

    # Positive: common S-containing cations
    for formula in [
        "CHS", "CH3S", "C2H3S", "C2H5S",
    ]:
        _add_if_possible(out, parent_counts, formula, "positive", 1,
                         "sulfurated_small_fragments", "sulfurated",
                         f"s_small_{formula}", evidence, max_mass)

    # Negative: S-, HS-, CS- — key anions in S-containing polymer spectra
    for formula in [
        "S", "HS", "CS",
    ]:
        _add_if_possible(out, parent_counts, formula, "negative", -1,
                         "sulfurated_small_fragments", "sulfurated",
                         f"s_small_{formula}", evidence, max_mass)

    return out


def _generate_siloxane_small_fragments(features: dict[str, bool], parent_counts: dict[str, int], parent_elements: dict[str, int], cfg: dict, max_mass: float) -> list[FeatureRuleCandidate]:
    """Si-gated small siloxane fragments.  PDMS spectra are dominated by
    Si1-Si3 fragments that cannot be generated from the short dimer SMILES.
    strict_counts=False: real PDMS has hundreds of Si, not just 2."""
    out: list[FeatureRuleCandidate] = []
    if not cfg.get("siloxane_small_fragments", {}).get("enabled", True):
        return out
    if parent_counts.get("Si", 0) <= 0:
        return out
    evidence = f"Si-gated siloxane fragments; parent Si={parent_counts.get('Si', 0)}"
    # Positive: common PDMS cations (Si1-Si2, C1-C3)
    for formula in [
        "CH3Si", "CH5Si", "C2H5Si", "C2H7Si", "C3H7Si", "C3H9Si",
        "CH3OSi", "CH5OSi", "C2H5OSi", "C2H7OSi", "C3H7OSi", "C3H9OSi",
        "C2H7OSi2", "C3H9OSi2", "C4H11OSi2",
    ]:
        _add_if_possible(out, parent_counts, formula, "positive", 1,
                         "siloxane_small_fragments", "siloxane",
                         f"silox_{formula}", evidence, max_mass, strict_counts=False)
    # Negative: PDMS anions
    for formula in [
        "CH3Si", "C2H5Si", "C3H7Si",
        "CH3OSi", "C2H5OSi", "C3H7OSi",
        "CH5OSi", "C2H7OSi",
    ]:
        _add_if_possible(out, parent_counts, formula, "negative", -1,
                         "siloxane_small_fragments", "siloxane",
                         f"silox_{formula}", evidence, max_mass, strict_counts=False)
    return out


def _generate_cyclic_aliphatic_fragments(features: dict[str, bool], parent_counts: dict[str, int], parent_elements: dict[str, int], cfg: dict, max_mass: float) -> list[FeatureRuleCandidate]:
    out: list[FeatureRuleCandidate] = []
    if not features.get("cyclic_aliphatic") or not cfg.get("cyclic_aliphatic_fragments", {}).get("enabled", True):
        return out
    evidence = f"non-aromatic ring detected; heavy element counts={parent_elements}"
    # C3-C7 cycloaliphatic fragments (norbornane ring opening)
    for formula, ion_mode, charge in [
        ("C3H5", "positive", 1),
        ("C4H7", "positive", 1),
        ("C5H7", "positive", 1),
        ("C5H9", "positive", 1),
        ("C6H9", "positive", 1),
        ("C7H11", "positive", 1),
        ("C7H9", "positive", 1),
        ("C3H3", "negative", -1),
        ("C4H3", "negative", -1),
        ("C5H5", "negative", -1),
    ]:
        _add_if_possible(out, parent_counts, formula, ion_mode, charge, "cyclic_aliphatic_fragments", "cyclic_aliphatic", f"cycloaliphatic_{formula}", evidence, max_mass)
    # C8-C10 norbornane-diagnostic fragments (v2.9.3 COC)
    for formula, ion_mode, charge in [
        ("C8H9", "positive", 1),
        ("C8H11", "positive", 1),
        ("C8H13", "positive", 1),
        ("C9H9", "positive", 1),
        ("C9H11", "positive", 1),
        ("C9H13", "positive", 1),
        ("C10H9", "positive", 1),
        ("C10H11", "positive", 1),
        ("C10H13", "positive", 1),
        ("C8H7", "negative", -1),
        ("C9H7", "negative", -1),
        ("C10H7", "negative", -1),
    ]:
        _add_if_possible(out, parent_counts, formula, ion_mode, charge, "cyclic_aliphatic_fragments", "cyclic_aliphatic", f"cycloaliphatic_{formula}", evidence, max_mass)
    return out


def _generate_acetate_ethylene_fragments(features: dict[str, bool], parent_counts: dict[str, int], parent_elements: dict[str, int], cfg: dict, max_mass: float) -> list[FeatureRuleCandidate]:
    """EVA acetate-ethylene diagnostic fragments (v2.9.3).

    Trigger: carbonyl present + NO aromatic ring.  This gates to EVA among
    current compounds (PET/PEEK/PEN/Nomex all have aromatic rings).
    These are acetate group + n*ethylene combinations characteristic of
    ethylene-vinyl acetate copolymer TOF-SIMS spectra.
    """
    out: list[FeatureRuleCandidate] = []
    if not cfg.get("acetate_ethylene_fragments", {}).get("enabled", True):
        return out
    if not features.get("carbonyl"):
        return out
    if features.get("aromatic_ring"):
        return out  # EVA is the only non-aromatic carbonyl material

    evidence = f"acetate-ethylene copolymer (carbonyl + no aromatic); counts={parent_elements}"

    # Positive: acetate + n*ethylene fragments
    for formula in [
        "C4H5O2", "C4H7O2",
        "C6H9O2", "C6H11O2",
        "C8H13O2", "C8H15O2",
    ]:
        _add_if_possible(out, parent_counts, formula, "positive", 1,
                         "acetate_ethylene_fragments", "carbonyl",
                         f"eva_{formula}", evidence, max_mass,
                         strict_counts=False)

    # Negative: acetate anions
    for formula in [
        "C4H5O2", "C6H9O2", "C8H13O2",
    ]:
        _add_if_possible(out, parent_counts, formula, "negative", -1,
                         "acetate_ethylene_fragments", "carbonyl",
                         f"eva_{formula}", evidence, max_mass,
                         strict_counts=False)

    return out


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
        # strict_counts=False: fluoropolymer SMILES are short-chain approximations;
        # the real polymer has many more F atoms than the model SMILES (e.g. PVDF
        # SMILES C2H2F2 has only 2F, but real PVDF has thousands of F).
        for formula, ion_mode, charge in [
            # Positive: fluorocarbon cations
            ("CF", "positive", 1),
            ("CF2", "positive", 1),
            ("CF3", "positive", 1),
            ("C2F3", "positive", 1),
            ("C2F4", "positive", 1),
            ("C2F5", "positive", 1),
            ("C3F3", "positive", 1),
            ("C3F5", "positive", 1),
            ("C3F7", "positive", 1),
            # Negative: fluorocarbon anions
            ("F", "negative", -1),
            ("CF", "negative", -1),
            ("CF3", "negative", -1),
            ("C2F3", "negative", -1),
            ("C2F4", "negative", -1),
            ("C2F5", "negative", -1),
            ("C3F5", "negative", -1),
        ]:
            _add_if_possible(out, parent_counts, formula, ion_mode, charge,
                             "fluorocarbon_fragmentation", "fluorocarbon_motif",
                             f"diagnostic_{formula}", evidence, max_mass,
                             strict_counts=False)

    # Hydrofluorocarbon fragments: for materials with BOTH C-F AND C-H bonds
    # (PVDF, ETFE).  Gated by fluorocarbon_motif + parent has H.
    if (features["fluorocarbon_motif"]
            and parent_counts.get("H", 0) > 0
            and cfg.get("fluorocarbon_fragmentation", {}).get("enabled", True)):
        evidence_hfc = f"C-F + C-H bonds present (hydrofluorocarbon); heavy element counts={parent_elements}"
        for formula, ion_mode, charge in [
            ("CHF2", "positive", 1),
            ("CH2F", "positive", 1),
            ("C2HF2", "positive", 1),
            ("C2H2F", "positive", 1),
            ("C2H2F2", "positive", 1),
            ("C2HF4", "positive", 1),
            ("C3H2F3", "positive", 1),
            ("C3H3F2", "positive", 1),
        ]:
            _add_if_possible(out, parent_counts, formula, ion_mode, charge,
                             "fluorocarbon_fragmentation", "fluorocarbon_motif",
                             f"hfc_{formula}", evidence_hfc, max_mass,
                             strict_counts=False)

    if features["acetal_or_ether"] and cfg.get("acetal_oxonium_series", {}).get("enabled", True):
        evidence = f"acetal/ether C-O-C motif present; heavy element counts={parent_elements}"
        # Positive: oxonium and acetal-derived oxygenated cations
        for formula in [
            "CH3O", "C2H3O", "C2H4O", "C2H5O", "C2H3O2", "C2H5O2",
            "C3H3O", "C3H5O", "C3H5O2", "C3H5O3",
            "C3H6O", "C3H6O2", "C3H6O3", "C3H7O", "C3H7O2", "C3H7O3",
        ]:
            _add_if_possible(out, parent_counts, formula, "positive", 1, "acetal_oxonium_series", "acetal_or_ether", f"oxonium_{formula}", evidence, max_mass, strict_counts=False)
        # Negative: acetal-derived oxygenated anions
        for formula in [
            "CHO2", "C2H3O2", "C2H5O2",
            "C3H5O2", "C3H5O3",
        ]:
            _add_if_possible(out, parent_counts, formula, "negative", -1, "acetal_oxonium_series", "acetal_or_ether", f"oxonium_neg_{formula}", evidence, max_mass, strict_counts=False)

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

    out.extend(_generate_carbonyl_fragments(features, parent_counts, parent_elements, cfg, max_mass))
    out.extend(_generate_imide_fragments(features, parent_counts, parent_elements, cfg, max_mass))
    out.extend(_generate_amide_fragments(features, parent_counts, parent_elements, cfg, max_mass))
    out.extend(_generate_cyclic_aliphatic_fragments(features, parent_counts, parent_elements, cfg, max_mass))
    out.extend(_generate_hydrocarbon_small_fragments(features, parent_counts, parent_elements, cfg, max_mass))
    out.extend(_generate_oxygenated_small_fragments(features, parent_counts, parent_elements, cfg, max_mass))
    out.extend(_generate_nitrogenated_small_fragments(features, parent_counts, parent_elements, cfg, max_mass))
    out.extend(_generate_sulfurated_small_fragments(features, parent_counts, parent_elements, cfg, max_mass))
    out.extend(_generate_siloxane_small_fragments(features, parent_counts, parent_elements, cfg, max_mass))
    out.extend(_generate_acetate_ethylene_fragments(features, parent_counts, parent_elements, cfg, max_mass))

    by_key: dict[tuple[str, str, str], FeatureRuleCandidate] = {}
    for candidate in out:
        key = (str(candidate.counts), candidate.ion_mode, candidate.operation)
        by_key[key] = candidate
    return list(by_key.values())
