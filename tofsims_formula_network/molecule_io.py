from __future__ import annotations

from pathlib import Path

import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors

from .formula import normalize_formula_string


def read_compounds(path: Path) -> pd.DataFrame:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "compound_id,name,smiles,formula,group,notes\n"
            "STD001,Toluene,Cc1ccccc1,C7H8,demo,auto-created demo row\n",
            encoding="utf-8",
        )
    df = pd.read_csv(path).fillna("")
    required = {"compound_id", "name", "smiles"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"compounds.csv missing columns: {sorted(missing)}")
    return df


def mol_from_smiles(smiles: str) -> Chem.Mol:
    mol = Chem.MolFromSmiles(str(smiles))
    if mol is None:
        raise ValueError(f"Invalid SMILES: {smiles}")
    return Chem.AddHs(mol)


def get_formula_from_mol(mol: Chem.Mol) -> str:
    return normalize_formula_string(rdMolDescriptors.CalcMolFormula(mol))


def validate_compound_row(row) -> None:
    if not str(row.get("compound_id", "")).strip():
        raise ValueError("compound_id is required")
    if not str(row.get("smiles", "")).strip():
        raise ValueError("smiles is required")
