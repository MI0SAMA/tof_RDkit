from __future__ import annotations

from pathlib import Path
from typing import Any


def default_config() -> dict[str, Any]:
    return {
        "io": {
            "data_dir": "data",
            "spectra_glob": "data/**/*.txt",
            "compounds_file": "data/compounds.csv",
            "rf_candidates_file": "data/rf_candidates.csv",
            "output_dir": "outputs",
        },
        "spectrum": {
            "min_mz": 1.0,
            "max_mz": 2000.0,
            "min_intensity": 0.0,
            "top_n_peaks": 300,
            "normalize_intensity": True,
            "peak_match_ppm": 20,
            "peak_match_da": 0.01,
        },
        "fragmentation": {
            "max_bond_breaks": 2,
            "min_heavy_atoms_per_fragment": 2,
            "allow_ring_bond_break": False,
            "allow_aromatic_bond_break": False,
            "max_generated_formulas_per_compound": 20000,
        },
        "ion_rules": {
            "h_shift_range": [-2, -1, 0, 1, 2],
            "common_adducts_positive": ["H", "Na", "K"],
            "common_adducts_negative": ["-H", "Cl", "O", "OH"],
            "neutral_losses": ["H2", "H2O", "CO", "CO2", "NH3", "CH3", "OH", "HCl", "HF"],
            "dimers": True,
        },
        "formula": {
            "allowed_elements": ["H", "C", "N", "O", "F", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "K", "Ca", "Ti", "Fe", "Cu", "Zn", "Br", "I"],
            "allow_external_adduct_elements": True,
        },
        "scoring": {
            "base_parent": 1.0,
            "base_fragment": 0.75,
            "penalty_per_broken_bond": 0.15,
            "penalty_per_h_shift": 0.05,
            "penalty_neutral_loss": 0.10,
            "penalty_non_h_adduct": 0.12,
            "penalty_dimer": 0.20,
            "bonus_rf_match": 0.30,
            "bonus_multi_peak_support": 0.05,
            "min_score": 0.0,
            "max_score": 1.0,
        },
    }


def load_config(path: str | Path | None) -> dict[str, Any]:
    cfg = default_config()
    if not path or not Path(path).exists():
        return cfg
    try:
        import yaml
    except ModuleNotFoundError:
        return cfg
    loaded = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    deep_update(cfg, loaded)
    return cfg


def deep_update(target: dict[str, Any], source: dict[str, Any]) -> None:
    for key, value in source.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            deep_update(target[key], value)
        else:
            target[key] = value


def ensure_dirs(output_dir: str | Path) -> dict[str, Path]:
    base = Path(output_dir)
    paths = {
        "base": base,
        "parsed_spectra": base / "parsed_spectra",
        "networks": base / "networks",
        "matches": base / "matches",
        "reports": base / "reports",
        "summary": base / "summary",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths
