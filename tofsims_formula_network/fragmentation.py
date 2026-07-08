"""RDKit bond-breaking fragment generation with v4.0 bond-type-aware rules.

v4.0 replaces the global "no ring/aromatic bond break" with per-bond-type
overrides, so that chemically labile bonds (C-S, Si-O, C-O_ether, C-N_amide)
can be broken even inside rings or aromatic systems.  This provides structurally
traceable paths for fragments that previously required empirical Layer 3 rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Any

from rdkit import Chem


# ── Bond-type classification ────────────────────────────────────────────────

# Atomic number → symbol
_AN = {
    1: "H", 6: "C", 7: "N", 8: "O", 9: "F",
    14: "Si", 15: "P", 16: "S", 17: "Cl",
}

# (atomic_number_1, atomic_number_2) → bond_type_label (sorted)
_BOND_TYPE_MAP: dict[tuple[int, int], str] = {
    (6, 6): "C-C",
    (6, 7): "C-N",
    (6, 8): "C-O",
    (6, 9): "C-F",
    (6, 14): "C-Si",
    (6, 16): "C-S",
    (6, 17): "C-Cl",
    (8, 14): "Si-O",
    (8, 16): "S-O",
    (7, 8): "N-O",
}


def classify_bond(mol: Chem.Mol, bond_idx: int) -> str:
    """Return bond type label for a bond, e.g. 'C-S', 'Si-O'."""
    bond = mol.GetBondWithIdx(bond_idx)
    a1 = bond.GetBeginAtom().GetAtomicNum()
    a2 = bond.GetEndAtom().GetAtomicNum()
    pair = tuple(sorted((a1, a2)))
    return _BOND_TYPE_MAP.get(pair, "other")


# ── Bond-type rule lookup ────────────────────────────────────────────────────

def _bond_type_rule(config: dict, bond_type: str) -> dict[str, Any]:
    """Return per-bond-type config overrides, or empty dict."""
    rules = config.get("fragmentation", {}).get("bond_type_rules", {})
    return rules.get(bond_type, {})


def _check_structural_conditions(mol: Chem.Mol, conditions: dict) -> bool:
    """Check molecule-level structural conditions for a bond-type rule.

    Supported conditions:
      require_acetal_or_ether : molecule must have O-C-O or C-O-C pattern
      require_no_aromatic      : molecule must have NO aromatic atoms
      require_no_carbonyl      : molecule must have NO C=O bonds
    """
    if conditions.get("require_acetal_or_ether"):
        patterns = [
            Chem.MolFromSmarts("[OX2]-[CX4]-[OX2]"),  # O-C-O (acetal)
            Chem.MolFromSmarts("[CX4]-[OX2]-[CX4]"),  # C-O-C (ether)
        ]
        if not any(p is not None and mol.HasSubstructMatch(p) for p in patterns):
            return False

    if conditions.get("require_no_aromatic"):
        if any(atom.GetIsAromatic() for atom in mol.GetAtoms()):
            return False

    if conditions.get("require_no_carbonyl"):
        carbonyl = Chem.MolFromSmarts("[#6]=[OX1]")
        if carbonyl is not None and mol.HasSubstructMatch(carbonyl):
            return False

    if conditions.get("require_carbonyl"):
        carbonyl = Chem.MolFromSmarts("[#6]=[OX1]")
        if carbonyl is None or not mol.HasSubstructMatch(carbonyl):
            return False

    return True


# Cache for structural condition results per molecule
_structural_condition_cache: dict[int, dict[str, bool]] = {}


def _meets_structural_conditions(mol: Chem.Mol, conditions: dict) -> bool:
    """Check conditions with caching per molecule."""
    if not conditions:
        return True
    mol_id = id(mol)
    if mol_id not in _structural_condition_cache:
        _structural_condition_cache[mol_id] = {}
    # Use a frozenset of condition items as cache key
    cache_key = frozenset(conditions.items())
    if cache_key not in _structural_condition_cache[mol_id]:
        _structural_condition_cache[mol_id][cache_key] = _check_structural_conditions(mol, conditions)
    return _structural_condition_cache[mol_id][cache_key]


def _is_breakable(
    bond: Chem.Bond,
    bond_type: str,
    mol: Chem.Mol,
    config: dict,
) -> bool:
    """Decide if a bond is breakable under v4.1 bond-type-aware rules.

    Priority: bond-type rule (with structural conditions) > global config.
    """
    frag_cfg = config["fragmentation"]
    bt_rule = _bond_type_rule(config, bond_type)

    # Check structural conditions: if gate is closed, use global rules
    # (do NOT deny breakability — just don't apply bond-type overrides)
    conditions = bt_rule.get("structural_conditions", {})
    use_bt_overrides = (not conditions) or _meets_structural_conditions(mol, conditions)

    # Single bond only (hard constraint, not overridable)
    if bond.GetBondType() != Chem.BondType.SINGLE:
        return False

    # Ring bond: check bond-type override (if gate open), else global
    if bond.IsInRing():
        if use_bt_overrides and bt_rule.get("allow_ring_bond_break", False):
            pass
        elif not frag_cfg.get("allow_ring_bond_break", False):
            return False

    # Aromatic bond: check bond-type override (if gate open), else global
    if bond.GetIsAromatic():
        if use_bt_overrides and bt_rule.get("allow_aromatic_bond_break", False):
            pass
        elif not frag_cfg.get("allow_aromatic_bond_break", False):
            return False

    return True


# ── Single-atom fragment support ─────────────────────────────────────────────

def _can_generate_single_atom(
    atom_idx: int,
    mol: Chem.Mol,
    config: dict,
    broken_bond_indices: list[int],
) -> bool:
    """Check if a single atom can be a valid fragment under bond-type rules.

    A single heavy atom (e.g. S from C-S break) is allowed as a fragment
    only if ALL broken bonds that detached it have bond-type rules with
    allow_single_atom_fragment=True.
    """
    bt_rules = config.get("fragmentation", {}).get("bond_type_rules", {})
    atom = mol.GetAtomWithIdx(atom_idx)
    if atom.GetAtomicNum() == 1:  # never generate H-only fragments
        return False

    for bond_idx in broken_bond_indices:
        bond_type = classify_bond(mol, bond_idx)
        bt_rule = bt_rules.get(bond_type, {})
        if not bt_rule.get("allow_single_atom_fragment", False):
            return False

    return True


# ── Fragment dataclass ───────────────────────────────────────────────────────

@dataclass(frozen=True)
class Fragment:
    counts: dict[str, int]
    atom_indices: list[int]
    broken_bonds: int
    boundary_atom_indices: list[int] | None = None
    boundary_elements: list[str] | None = None
    # v4.0: structural traceability
    bond_types_broken: list[str] | None = None
    single_atom_fragment: bool = False
    derivation: str = ""  # human-readable structural path description


def fragment_counts(mol: Chem.Mol, atom_indices: tuple[int, ...]) -> dict[str, int]:
    counts: dict[str, int] = {}
    atoms = set(atom_indices)
    for idx in atoms:
        atom = mol.GetAtomWithIdx(idx)
        symbol = atom.GetSymbol()
        counts[symbol] = counts.get(symbol, 0) + 1
    return counts


# ── Public API ───────────────────────────────────────────────────────────────

def breakable_bond_indices(mol: Chem.Mol, config: dict) -> list[int]:
    """Return indices of bonds that can be broken under v4.0 rules."""
    breakable = []
    for bond in mol.GetBonds():
        begin = bond.GetBeginAtom()
        end = bond.GetEndAtom()
        # Hard constraint: no H-X bonds
        if begin.GetAtomicNum() == 1 or end.GetAtomicNum() == 1:
            continue

        bond_type = classify_bond(mol, bond.GetIdx())
        if _is_breakable(bond, bond_type, mol, config):
            breakable.append(bond.GetIdx())

    return breakable


def generate_fragments(mol: Chem.Mol, config: dict) -> list[Fragment]:
    """Generate fragments by enumerating bond-break combinations.

    v4.0 additions:
    - Bond-type-aware breakability (C-S in rings, Si-O in rings, etc.)
    - Single-atom fragment support for specific bond types
    - Derivation path metadata on each fragment
    """
    frag_cfg = config["fragmentation"]
    breakable = breakable_bond_indices(mol, config)

    # Per-bond-type max_bond_breaks override (take the max across all bond types)
    bt_rules = config.get("fragmentation", {}).get("bond_type_rules", {})
    max_breaks = int(frag_cfg["max_bond_breaks"])
    for bond_idx in breakable:
        bt = classify_bond(mol, bond_idx)
        bt_max = bt_rules.get(bt, {}).get("max_bond_breaks_override", 0)
        if bt_max > max_breaks:
            max_breaks = bt_max

    fragments: list[Fragment] = []
    min_heavy = int(frag_cfg["min_heavy_atoms_per_fragment"])
    max_gen = int(frag_cfg["max_generated_formulas_per_compound"])

    for k in range(1, max_breaks + 1):
        for combo in combinations(breakable, k):
            # Classify each broken bond
            bond_types_broken = [classify_bond(mol, idx) for idx in combo]

            frag_mol = Chem.FragmentOnBonds(mol, list(combo), addDummies=False)
            for atoms in Chem.GetMolFrags(frag_mol, asMols=False, sanitizeFrags=False):
                atom_set = set(atoms)

                # Boundary tracking
                boundary_indices: list[int] = []
                boundary_elements: list[str] = []
                for bond_idx in combo:
                    bond = mol.GetBondWithIdx(bond_idx)
                    begin_idx = bond.GetBeginAtomIdx()
                    end_idx = bond.GetEndAtomIdx()
                    if begin_idx in atom_set and end_idx not in atom_set:
                        boundary_indices.append(begin_idx)
                    elif end_idx in atom_set and begin_idx not in atom_set:
                        boundary_indices.append(end_idx)
                for idx in boundary_indices:
                    boundary_elements.append(mol.GetAtomWithIdx(idx).GetSymbol())

                heavy_count = sum(1 for idx in atoms if mol.GetAtomWithIdx(idx).GetAtomicNum() > 1)

                # v4.0: single-atom fragment check
                single_atom = False
                if heavy_count < min_heavy:
                    if heavy_count == 1:
                        # Find the single heavy atom
                        heavy_idx = next(idx for idx in atoms if mol.GetAtomWithIdx(idx).GetAtomicNum() > 1)
                        if _can_generate_single_atom(heavy_idx, mol, config, list(combo)):
                            single_atom = True
                        else:
                            continue  # skip this fragment
                    else:
                        continue  # skip fragments with too few heavy atoms

                # Derivation description
                elem_str = ",".join(sorted(set(
                    mol.GetAtomWithIdx(idx).GetSymbol() for idx in atoms
                )))
                bt_str = "+".join(bond_types_broken)
                if single_atom:
                    derivation = f"single-atom {elem_str} from {bt_str} bond break"
                else:
                    derivation = f"fragment {elem_str} from {bt_str} bond break(s)"

                fragments.append(
                    Fragment(
                        counts=fragment_counts(mol, tuple(atoms)),
                        atom_indices=list(atoms),
                        broken_bonds=k,
                        boundary_atom_indices=boundary_indices,
                        boundary_elements=boundary_elements,
                        bond_types_broken=bond_types_broken,
                        single_atom_fragment=single_atom,
                        derivation=derivation,
                    )
                )

                if len(fragments) >= max_gen:
                    return fragments

    return fragments
