from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .formula import mass_error, normalize_formula_string


def _safe_normalize(formula: str) -> str | None:
    try:
        return normalize_formula_string(formula)
    except Exception:
        return None


def load_networks(network_dir: str | Path) -> pd.DataFrame:
    frames = []
    for path in Path(network_dir).glob("*.csv"):
        frames.append(pd.read_csv(path))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def load_rf_candidates(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        return pd.DataFrame(columns=["spectrum_id", "peak_mz", "candidate_formula", "rf_rank", "rf_score"])
    return pd.read_csv(path)


def match_rf_with_network(rf_df: pd.DataFrame, network_df: pd.DataFrame, config: dict | None = None) -> pd.DataFrame:
    if rf_df.empty or network_df.empty:
        return pd.DataFrame()
    rf = rf_df.copy()
    rf["normalized_formula"] = rf["candidate_formula"].map(_safe_normalize)
    rf = rf[rf["normalized_formula"].notna()]
    net = network_df.copy()
    net["normalized_formula"] = net["formula"].map(_safe_normalize)
    net = net[net["normalized_formula"].notna()]
    merged = rf.merge(net, on="normalized_formula", how="inner", suffixes=("_rf", "_network"))
    if merged.empty:
        return pd.DataFrame()
    merged["matched_formula"] = merged["normalized_formula"]
    merged["network_score"] = merged.get("score", 0.0)
    bonus = (config or {}).get("scoring", {}).get("bonus_rf_match", 0.3)
    merged["final_score"] = (merged["network_score"].astype(float) + bonus).clip(0, 1)
    if "peak_mz" in merged and "exact_mass" in merged:
        errors = merged.apply(lambda row: mass_error(row["peak_mz"], row["exact_mass"]), axis=1)
        merged["mass_error_da"] = [err[0] for err in errors]
        merged["mass_error_ppm"] = [err[1] for err in errors]
    dedupe_cols = [col for col in ["spectrum_id", "peak_mz", "candidate_formula", "source_compound_id", "normalized_formula"] if col in merged.columns]
    return merged.sort_values("final_score", ascending=False).drop_duplicates(dedupe_cols).reset_index(drop=True)


def match_spectrum_by_mass(spectrum_df: pd.DataFrame, network_df: pd.DataFrame, ppm: float, da: float) -> pd.DataFrame:
    if spectrum_df.empty or network_df.empty:
        return pd.DataFrame()
    rows = []
    for _, peak in spectrum_df.iterrows():
        tolerance = max(float(da), float(peak["mz"]) * float(ppm) * 1e-6)
        candidates = network_df[(network_df["exact_mass"] - peak["mz"]).abs() <= tolerance]
        for _, candidate in candidates.iterrows():
            err_da, err_ppm = mass_error(peak["mz"], candidate["exact_mass"])
            rows.append({
                "spectrum_id": peak["spectrum_id"],
                "peak_mz": peak["mz"],
                "intensity": peak["intensity"],
                "rf_formula": "",
                "matched_formula": candidate["formula"],
                "compound_id": candidate["source_compound_id"],
                "compound_name": candidate["source_name"],
                "generation_type": candidate["generation_type"],
                "path": candidate["path"],
                "network_score": candidate["score"],
                "final_score": candidate["score"],
                "mass_error_da": err_da,
                "mass_error_ppm": err_ppm,
            })
    return pd.DataFrame(rows)


def calculate_final_score(match_df: pd.DataFrame, config: dict) -> pd.DataFrame:
    if match_df.empty:
        return match_df
    out = match_df.copy()
    support = out.groupby(["spectrum_id", "source_compound_id" if "source_compound_id" in out else "compound_id"])["peak_mz"].transform("nunique")
    bonus = support.clip(upper=4) * config["scoring"]["bonus_multi_peak_support"]
    out["final_score"] = (out["final_score"].astype(float) + bonus).clip(0, 1)
    return out
