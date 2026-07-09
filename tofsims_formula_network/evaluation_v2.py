from __future__ import annotations

from pathlib import Path

import pandas as pd

from .formula import mass_error
from .spectrum_io import read_spectrum_txt, preprocess_spectrum, standardize_spectrum


def infer_ion_mode(path: Path) -> str:
    name = path.name.strip()
    if name.startswith("-"):
        return "negative"
    return "positive"


def centroid_peaks(df: pd.DataFrame, da: float, ppm: float) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    rows = df.sort_values("mz").to_dict("records")
    clusters: list[list[dict]] = []
    current: list[dict] = []
    center = 0.0
    for row in rows:
        mz = float(row["mz"])
        tolerance = max(float(da), center * float(ppm) / 1_000_000.0) if current else float(da)
        if current and abs(mz - center) > tolerance:
            clusters.append(current)
            current = []
        current.append(row)
        intensity_sum = sum(float(item["intensity"]) for item in current)
        if intensity_sum > 0:
            center = sum(float(item["mz"]) * float(item["intensity"]) for item in current) / intensity_sum
        else:
            center = sum(float(item["mz"]) for item in current) / len(current)
    if current:
        clusters.append(current)

    out = []
    for idx, cluster in enumerate(clusters, start=1):
        intensity_sum = sum(float(item["intensity"]) for item in cluster)
        if intensity_sum > 0:
            mz = sum(float(item["mz"]) * float(item["intensity"]) for item in cluster) / intensity_sum
        else:
            mz = sum(float(item["mz"]) for item in cluster) / len(cluster)
        strongest = max(cluster, key=lambda item: float(item["intensity"]))
        out.append(
            {
                "cluster_id": idx,
                "mz": mz,
                "intensity": intensity_sum,
                "peak_count": len(cluster),
                "max_point_mz": float(strongest["mz"]),
                "max_point_intensity": float(strongest["intensity"]),
            }
        )
    return pd.DataFrame(out)


def _within(mz: float, item: dict) -> bool:
    return abs(float(mz) - float(item["mz"])) <= float(item.get("tolerance_da", 0.03))


def classify_peak(mz: float, ion_mode: str, config: dict) -> tuple[str, str, bool]:
    cfg = config.get("evaluation_v2", {})
    for item in cfg.get("contaminants", {}).get(ion_mode, []):
        if _within(mz, item):
            return "contaminant", str(item["label"]), False
    for item in cfg.get("low_mass_exceptions", {}).get(ion_mode, []):
        if _within(mz, item):
            return "low_mass_feature", str(item["label"]), True
    if mz < float(cfg.get("min_main_mz", 25.0)):
        return "low_mass_background", "below_min_main_mz", False
    return "structural_candidate", "", True


def load_v2_formula_summaries(network_dir: Path) -> pd.DataFrame:
    frames = []
    for path in sorted(network_dir.glob("*_formula_summary.csv")):
        frames.append(pd.read_csv(path))
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def _match_peak(mz: float, candidates: pd.DataFrame, config: dict) -> dict:
    if candidates.empty:
        return {"matched": False, "matched_formula": "", "matched_mass_error_da": "", "matched_mass_error_ppm": "", "matched_formula_score": ""}
    eval_cfg = config.get("evaluation_v2", {})
    tolerance = max(float(eval_cfg.get("match_da", 0.03)), mz * float(eval_cfg.get("match_ppm", 50)) / 1_000_000.0)
    delta = (candidates["exact_mass"].astype(float) - mz).abs()
    hits = candidates[delta <= tolerance].copy()
    if hits.empty:
        return {"matched": False, "matched_formula": "", "matched_mass_error_da": "", "matched_mass_error_ppm": "", "matched_formula_score": ""}
    hits["_delta"] = delta[hits.index]
    hits = hits.sort_values(["formula_score", "_delta"], ascending=[False, True])
    best = hits.iloc[0]
    err_da, err_ppm = mass_error(mz, float(best["exact_mass"]))
    return {
        "matched": True,
        "matched_formula": str(best["formula"]),
        "matched_mass_error_da": err_da,
        "matched_mass_error_ppm": err_ppm,
        "matched_formula_score": float(best["formula_score"]),
    }


def _network_top_n_precision_proxy(included_peaks: pd.DataFrame, candidates: pd.DataFrame, config: dict) -> tuple[int, int, float]:
    if included_peaks.empty or candidates.empty:
        return 0, 0, 0.0
    eval_cfg = config.get("evaluation_v2", {})
    top_n = int(eval_cfg.get("top_n", 50))
    top_candidates = candidates.sort_values("formula_score", ascending=False).head(top_n)
    matched = 0
    for _, candidate in top_candidates.iterrows():
        mass = float(candidate["exact_mass"])
        tolerance = max(float(eval_cfg.get("match_da", 0.03)), mass * float(eval_cfg.get("match_ppm", 50)) / 1_000_000.0)
        if ((included_peaks["mz"].astype(float) - mass).abs() <= tolerance).any():
            matched += 1
    total = len(top_candidates)
    return total, matched, matched / total if total else 0.0


def evaluate_spectrum(path: Path, networks: pd.DataFrame, config: dict) -> tuple[dict, pd.DataFrame]:
    material = path.parent.name
    ion_mode = infer_ion_mode(path)
    spectrum_id = f"{material}_{path.stem}"
    raw = read_spectrum_txt(path)
    preprocessed = preprocess_spectrum(raw, config)
    standardized = standardize_spectrum(preprocessed, spectrum_id, str(path))
    eval_cfg = config.get("evaluation_v2", {})
    centroided = centroid_peaks(standardized, float(eval_cfg.get("centroid_da", 0.03)), float(eval_cfg.get("centroid_ppm", 50)))
    material_network = networks[(networks["compound_id"].astype(str) == material) & (networks["ion_mode"].astype(str) == ion_mode)]

    peak_rows = []
    for _, peak in centroided.iterrows():
        category, label, included = classify_peak(float(peak["mz"]), ion_mode, config)
        match = _match_peak(float(peak["mz"]), material_network, config) if included else {
            "matched": False,
            "matched_formula": "",
            "matched_mass_error_da": "",
            "matched_mass_error_ppm": "",
            "matched_formula_score": "",
        }
        peak_rows.append(
            {
                "spectrum_id": spectrum_id,
                "material": material,
                "source_file": str(path),
                "ion_mode": ion_mode,
                "mz": float(peak["mz"]),
                "intensity": float(peak["intensity"]),
                "centroid_peak_count": int(peak["peak_count"]),
                "peak_category": category,
                "category_label": label,
                "included_in_main_eval": included,
                **match,
            }
        )
    peaks = pd.DataFrame(peak_rows)
    included = peaks[peaks["included_in_main_eval"] == True] if not peaks.empty else peaks
    top_n = int(eval_cfg.get("top_n", 50))
    top = included.sort_values("intensity", ascending=False).head(top_n) if not included.empty else included
    matched = int(included["matched"].sum()) if not included.empty else 0
    top_matched = int(top["matched"].sum()) if not top.empty else 0
    top_network_count, top_network_matched, top_network_precision = _network_top_n_precision_proxy(included, material_network, config)
    summary = {
        "spectrum_id": spectrum_id,
        "material": material,
        "ion_mode": ion_mode,
        "source_file": str(path),
        "raw_peaks_after_preprocess": len(standardized),
        "centroid_peaks": len(peaks),
        "included_peaks": len(included),
        "excluded_peaks": len(peaks) - len(included),
        "matched_included_peaks": matched,
        "network_recall": matched / len(included) if len(included) else 0.0,
        "top_n": top_n,
        "top_n_included_peaks": len(top),
        "top_n_matched_peaks": top_matched,
        "top_n_peak_hit_rate": top_matched / len(top) if len(top) else 0.0,
        "top_n_network_candidates": top_network_count,
        "top_n_network_matched_candidates": top_network_matched,
        "top_n_network_precision_proxy": top_network_precision,
        "contaminant_peaks": int((peaks["peak_category"] == "contaminant").sum()) if not peaks.empty else 0,
        "low_mass_background_peaks": int((peaks["peak_category"] == "low_mass_background").sum()) if not peaks.empty else 0,
        "low_mass_feature_peaks": int((peaks["peak_category"] == "low_mass_feature").sum()) if not peaks.empty else 0,
    }
    return summary, peaks


def evaluate_network_v2(data_dir: Path, network_dir: Path, config: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    networks = load_v2_formula_summaries(network_dir)
    if networks.empty:
        return pd.DataFrame(), pd.DataFrame()
    excluded = {str(item) for item in config.get("io", {}).get("excluded_compound_ids", [])}
    summaries = []
    peak_frames = []
    files = sorted(list(data_dir.glob("*/*.txt")) + list(data_dir.glob("*/*.TXT")))
    for path in files:
        if "0510" in path.parts or path.parent.name in excluded:
            continue
        if not (network_dir / f"{path.parent.name}_formula_summary.csv").exists():
            continue
        try:
            summary, peaks = evaluate_spectrum(path, networks, config)
        except Exception as exc:
            summaries.append(
                {
                    "spectrum_id": f"{path.parent.name}_{path.stem}",
                    "material": path.parent.name,
                    "ion_mode": infer_ion_mode(path),
                    "source_file": str(path),
                    "raw_peaks_after_preprocess": 0,
                    "centroid_peaks": 0,
                    "included_peaks": 0,
                    "excluded_peaks": 0,
                    "matched_included_peaks": 0,
                    "network_recall": 0.0,
                    "top_n": int(config.get("evaluation_v2", {}).get("top_n", 50)),
                    "top_n_included_peaks": 0,
                    "top_n_matched_peaks": 0,
                    "top_n_peak_hit_rate": 0.0,
                    "top_n_network_candidates": 0,
                    "top_n_network_matched_candidates": 0,
                    "top_n_network_precision_proxy": 0.0,
                    "contaminant_peaks": 0,
                    "low_mass_background_peaks": 0,
                    "low_mass_feature_peaks": 0,
                    "message": str(exc),
                }
            )
            continue
        summary["message"] = ""
        summaries.append(summary)
        peak_frames.append(peaks)
    summary_df = pd.DataFrame(summaries)
    peaks_df = pd.concat(peak_frames, ignore_index=True) if peak_frames else pd.DataFrame()
    return summary_df, peaks_df
