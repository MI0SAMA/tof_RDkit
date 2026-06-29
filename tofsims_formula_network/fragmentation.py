from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from rdkit import Chem


@dataclass(frozen=True)
class Fragment:
    counts: dict[str, int]
    atom_indices: list[int]
    broken_bonds: int
    boundary_atom_indices: list[int] | None = None
    boundary_elements: list[str] | None = None


def fragment_counts(mol: Chem.Mol, atom_indices: tuple[int, ...]) -> dict[str, int]:
    counts: dict[str, int] = {}
    atoms = set(atom_indices)
    for idx in atoms:
        atom = mol.GetAtomWithIdx(idx)
        symbol = atom.GetSymbol()
        counts[symbol] = counts.get(symbol, 0) + 1
    return counts


def breakable_bond_indices(mol: Chem.Mol, config: dict) -> list[int]:
    frag_cfg = config["fragmentation"]
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
    return breakable


def generate_fragments(mol: Chem.Mol, config: dict) -> list[Fragment]:
    frag_cfg = config["fragmentation"]
    breakable = breakable_bond_indices(mol, config)

    fragments = []
    for k in range(1, int(frag_cfg["max_bond_breaks"]) + 1):
        for combo in combinations(breakable, k):
            frag_mol = Chem.FragmentOnBonds(mol, list(combo), addDummies=False)
            for atoms in Chem.GetMolFrags(frag_mol, asMols=False, sanitizeFrags=False):
                atom_set = set(atoms)
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
                if heavy_count < frag_cfg["min_heavy_atoms_per_fragment"]:
                    continue
                fragments.append(
                    Fragment(
                        counts=fragment_counts(mol, tuple(atoms)),
                        atom_indices=list(atoms),
                        broken_bonds=k,
                        boundary_atom_indices=boundary_indices,
                        boundary_elements=boundary_elements,
                    )
                )
                if len(fragments) >= frag_cfg["max_generated_formulas_per_compound"]:
                    return fragments
    return fragments
