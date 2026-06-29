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
            "excluded_compound_ids": ["PEEK20%GFR", "PPS40%GFR"],
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
            "generation_type_scores": {
                "carbon_cluster": 0.22,
                "siloxane_fragment": 0.28,
                "external_adduct": 0.25,
            },
            "min_score": 0.0,
            "max_score": 1.0,
        },
        "oligomer": {
            "max_extend": 12,
            "max_mass": 2000,
            "penalty_per_extend": 0.08,
        },
        "rule_packs": {
            "enabled": True,
            "carbon_cluster": {
                "enabled": True,
                "compound_ids": ["COC", "EVA", "PET", "POMC", "POMH"],
                "min_c": 3,
                "max_c": 14,
                "max_h_extra": 2,
                "max_o": 3,
                "max_mass": 220.0,
            },
            "siloxane_fragment": {
                "enabled": True,
                "compound_ids": ["PDMS"],
                "max_si": 6,
                "max_mass": 360.0,
            },
            "external_adduct": {
                "enabled": True,
                "compound_ids": ["POMC", "POMH", "EVA"],
                "adducts": ["Na", "K", "Cs", "Na2O", "HNa2O"],
                "max_base_mass": 500.0,
            },
        },
        "network_v2": {
            "max_fragment_nodes": 300,
            "feature_rules": {
                "enabled": True,
                "max_mass": 220.0,
                "fluorocarbon_fragmentation": {"enabled": True},
                "acetal_oxonium_series": {"enabled": True},
                "aromatic_stable_fragments": {"enabled": True},
                "sulfur_aromatic_fragments": {"enabled": True},
            },
            "fragment_h_shift": {
                "enabled": True,
                "shifts": [-1, 1],
            },
            "ionization": {
                "electron_loss": True,
                "electron_gain": True,
                "protonation": True,
                "deprotonation": True,
            },
            "recombination": {
                "enabled": True,
                "allowed_h_shift_pairs": [[-1, -1], [-1, 0], [-1, 1]],
                "require_site_compatibility": True,
                "allowed_site_pairs": [["C", "C"], ["C", "O"], ["C", "N"], ["C", "S"], ["Si", "O"]],
                "max_pairs": 5000,
                "max_mass": 2000.0,
            },
            "scoring": {
                "structure_scores": {
                    "parent": 0.45,
                    "fragment": 0.72,
                    "fragment_h_shift": 0.68,
                    "recombination": 0.64,
                    "feature_rule": 0.70,
                },
                "feature_rule_ionization_score": 0.80,
                "ionization_scores": {
                    "electron_loss": 0.55,
                    "electron_gain": 0.55,
                    "protonation": 0.72,
                    "deprotonation": 0.72,
                },
                "structure_weight": 0.60,
                "ionization_weight": 0.40,
                "parent_ionization_penalty": 0.18,
                "penalty_per_broken_bond": 0.08,
                "penalty_per_h_shift": 0.03,
                "penalty_recombination": 0.06,
                "path_support_bonus": {"2": 0.05, "3": 0.08, "4": 0.10},
                "mechanism_diversity_bonus": {"2": 0.05, "3": 0.08},
                "source_fragment_diversity_bonus": {"2": 0.04, "3": 0.07},
                "mass_prior": {
                    "preferred_min_mass": 25.0,
                    "preferred_max_mass": 200.0,
                    "preferred_mass_bonus": 0.05,
                    "high_mass_penalty_start": 500.0,
                    "penalty_per_100_da": 0.02,
                    "max_high_mass_penalty": 0.15,
                },
                "max_score": 1.0,
            },
        },
        "evaluation_v2": {
            "centroid_da": 0.03,
            "centroid_ppm": 50,
            "match_da": 0.03,
            "match_ppm": 50,
            "top_n": 50,
            "min_main_mz": 25.0,
            "contaminants": {
                "positive": [
                    {"label": "Na+", "mz": 22.9898, "tolerance_da": 0.03},
                    {"label": "K+", "mz": 38.9637, "tolerance_da": 0.03},
                    {"label": "Na2OH+", "mz": 62.984, "tolerance_da": 0.05},
                    {"label": "NaKOH+", "mz": 78.958, "tolerance_da": 0.05},
                    {"label": "K2OH+", "mz": 94.932, "tolerance_da": 0.05},
                    {"label": "Cs+", "mz": 132.9055, "tolerance_da": 0.05},
                ],
                "negative": [
                    {"label": "O-", "mz": 15.9949, "tolerance_da": 0.03},
                    {"label": "OH-", "mz": 17.0027, "tolerance_da": 0.03},
                    {"label": "Cl-", "mz": 34.9689, "tolerance_da": 0.03},
                    {"label": "Cl37-", "mz": 36.9659, "tolerance_da": 0.03},
                ],
            },
            "low_mass_exceptions": {
                "positive": [
                    {"label": "C2H3+", "mz": 27.0235, "tolerance_da": 0.03},
                    {"label": "C2H5+", "mz": 29.0391, "tolerance_da": 0.03},
                    {"label": "CF+", "mz": 30.9984, "tolerance_da": 0.03},
                    {"label": "CH3O+", "mz": 31.0184, "tolerance_da": 0.03},
                ],
                "negative": [
                    {"label": "F-", "mz": 18.9984, "tolerance_da": 0.03},
                    {"label": "CN-", "mz": 26.0031, "tolerance_da": 0.03},
                ],
            },
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
