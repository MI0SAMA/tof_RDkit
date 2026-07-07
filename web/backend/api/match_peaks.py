"""Peak matching API — upload spectra and match against formula networks.

Uses the same preprocessing pipeline as the CLI: spectrum_io + centroid binning.
"""

import os
import tempfile
from pathlib import Path

import pandas as pd
import yaml
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import FormulaSummary

router = APIRouter(prefix="/api", tags=["match-peaks"])

DATA_DIR = Path(os.environ.get("DATA_DIR", "/app/data"))
CONFIG_DIR = Path(os.environ.get("CONFIG_DIR", "/app/config"))


def _load_config():
    with open(CONFIG_DIR / "default.yaml") as f:
        return yaml.safe_load(f)


def _detect_polarity(filename: str) -> str:
    name = filename.lower()
    if "positive" in name or name.startswith("+") or "pos" in name:
        return "positive"
    if "negative" in name or name.startswith("-") or "neg" in name:
        return "negative"
    return "unknown"


def _parse_and_preprocess(content: str, filename: str) -> tuple[list[dict], dict]:
    """Parse peak file using spectrum_io pipeline + centroid binning.
    Returns (centroid_peaks, stats).
    """
    from tofsims_formula_network.spectrum_io import (
        preprocess_spectrum,
        read_spectrum_txt,
        standardize_spectrum,
    )

    cfg = _load_config()
    eval_cfg = cfg.get("evaluation_v2", {})

    # Write content to temp file for spectrum_io (expects file path)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tf:
        tf.write(content)
        tmp_path = Path(tf.name)

    try:
        # Parse with project's spectrum_io
        df = read_spectrum_txt(tmp_path)
        raw_count = len(df)

        # Apply preprocessing (min_mz, max_mz, min_intensity, top_n)
        pre = preprocess_spectrum(df, cfg)
        pre_count = len(pre)

        # Standardize
        std = standardize_spectrum(pre, "spectrum", filename)
        std_count = len(std)

        # Centroid binning (same as evaluation_v2)
        centroid_da = float(eval_cfg.get("centroid_da", 0.03))
        centroid_ppm = float(eval_cfg.get("centroid_ppm", 50))
        top_n = int(eval_cfg.get("top_n", 50))

        centroids = _centroid_peaks(std, centroid_da, centroid_ppm)
        # Take top N by intensity
        centroids.sort(key=lambda x: -x["intensity"])
        centroids = centroids[:top_n]

        stats = {
            "raw_count": raw_count,
            "preprocessed_count": pre_count,
            "standardized_count": std_count,
            "centroid_count": len(centroids),
            "top_n": top_n,
        }

        return centroids, stats
    finally:
        tmp_path.unlink(missing_ok=True)


def _centroid_peaks(df: pd.DataFrame, da: float, ppm: float) -> list[dict]:
    """Group nearby peaks into centroids (intensity-weighted average m/z)."""
    if df.empty:
        return []

    sorted_df = df.sort_values("mz").reset_index(drop=True)
    centroids = []
    current_group = [sorted_df.iloc[0]]

    for i in range(1, len(sorted_df)):
        row = sorted_df.iloc[i]
        prev = current_group[-1]
        tolerance = max(da, prev["mz"] * ppm * 1e-6)
        if row["mz"] - prev["mz"] <= tolerance:
            current_group.append(row)
        else:
            # Finalize current group
            total_intensity = sum(r["intensity"] for r in current_group)
            weighted_mz = sum(r["mz"] * r["intensity"] for r in current_group) / max(total_intensity, 1e-12)
            centroids.append({
                "mz": weighted_mz,
                "intensity": total_intensity,
                "n_peaks": len(current_group),
            })
            current_group = [row]

    # Final group
    if current_group:
        total_intensity = sum(r["intensity"] for r in current_group)
        weighted_mz = sum(r["mz"] * r["intensity"] for r in current_group) / max(total_intensity, 1e-12)
        centroids.append({
            "mz": weighted_mz,
            "intensity": total_intensity,
            "n_peaks": len(current_group),
        })

    return centroids


def _match_peaks(peaks: list[dict], compound_id: str, ion_mode: str, db: Session) -> dict:
    """Match centroid peaks against all formulas in the material's network."""
    cfg = _load_config()
    eval_cfg = cfg.get("evaluation_v2", {})
    match_da = float(eval_cfg.get("match_da", 0.03))
    match_ppm = float(eval_cfg.get("match_ppm", 50))
    min_main_mz = float(eval_cfg.get("min_main_mz", 25.0))

    formulas = (
        db.query(FormulaSummary)
        .filter(FormulaSummary.compound_id == compound_id)
        .all()
    )

    if not formulas:
        return {"error": f"No formulas found for {compound_id}", "peaks": [], "stats": {}}

    # Filter peaks: only match peaks above min_main_mz
    main_peaks = [p for p in peaks if p["mz"] >= min_main_mz]
    low_mass_peaks = [p for p in peaks if p["mz"] < min_main_mz]

    matched = []
    unmatched = []

    for peak in main_peaks:
        mz = peak["mz"]
        intensity = peak["intensity"]
        tolerance = max(match_da, mz * match_ppm * 1e-6)

        best_match = None
        best_error = float("inf")

        for f in formulas:
            # Include ALL formulas (including structural_only) for mass matching
            if ion_mode != "unknown" and f.ion_mode != "neutral" and f.ion_mode != ion_mode:
                continue

            error = abs(f.exact_mass - mz)
            if error <= tolerance and error < best_error:
                best_error = error
                ppm_error = error / mz * 1e6 if mz > 0 else float("inf")
                best_match = {
                    "mz": round(mz, 4),
                    "intensity": intensity,
                    "matched_formula": f.formula,
                    "ion_mode": f.ion_mode,
                    "exact_mass": f.exact_mass,
                    "mass_error_da": round(error, 6),
                    "mass_error_ppm": round(ppm_error, 2),
                    "formula_score": f.formula_score,
                    "diagnostic_tag": f.diagnostic_tag,
                    "generation_types": f.generation_types,
                    "representative_path": f.representative_path,
                }

        if best_match:
            matched.append(best_match)
        else:
            unmatched.append({
                "mz": round(mz, 4),
                "intensity": intensity,
                "reason": "no_match",
            })

    matched.sort(key=lambda x: -x["formula_score"])

    included_peaks = len(main_peaks)
    matched_count = len(matched)

    return {
        "compound_id": compound_id,
        "detected_polarity": ion_mode,
        "total_centroid_peaks": len(peaks),
        "included_peaks": included_peaks,
        "low_mass_peaks": len(low_mass_peaks),
        "matched_peaks": matched_count,
        "unmatched_peaks": included_peaks - matched_count,
        "match_rate": round(matched_count / max(included_peaks, 1) * 100, 1),
        "tolerance_ppm": match_ppm,
        "tolerance_da": match_da,
        "min_main_mz": min_main_mz,
        "matched": matched,
        "unmatched": unmatched,
    }


@router.post("/materials/{material_id}/match-peaks")
async def match_peaks_endpoint(
    material_id: str,
    file: UploadFile = File(...),
    polarity: str = Query("auto"),
    db: Session = Depends(get_db),
):
    """Upload a peak list file and match against formula network."""
    content = (await file.read()).decode("utf-8", errors="replace")
    if polarity == "auto":
        polarity = _detect_polarity(file.filename or "")

    try:
        centroids, stats = _parse_and_preprocess(content, file.filename or "upload")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Parse error: {e}")

    result = _match_peaks(centroids, material_id, polarity, db)
    result["preprocess_stats"] = stats
    return result


@router.get("/materials/{material_id}/spectra")
def list_available_spectra(material_id: str):
    """List available experimental peak files from data/{material}/ and data/0510/{material}/."""
    spectra = []

    # Check main data directory
    material_dir = DATA_DIR / material_id
    if material_dir.exists():
        for f in sorted(material_dir.iterdir()):
            if f.suffix.lower() in (".txt", ".csv", ".tsv"):
                spectra.append(_fmt_spectrum(f, material_id, annotated=False))

    # Also check 0510 subdirectory for annotated data
    anno_dir = DATA_DIR / "0510" / material_id
    if anno_dir.exists():
        for f in sorted(anno_dir.iterdir()):
            if f.suffix.lower() in (".txt", ".csv", ".tsv"):
                spectra.append(_fmt_spectrum(f, material_id, annotated=True))

    return {"material_id": material_id, "spectra": spectra}


def _fmt_spectrum(f: Path, material_id: str, annotated: bool) -> dict:
    """Format a spectrum file entry."""
    polarity = _detect_polarity(f.name)
    return {
        "filename": f.name,
        "path": str(f.relative_to(DATA_DIR)),
        "polarity": polarity,
        "size_kb": round(f.stat().st_size / 1024, 1),
        "annotated": annotated,
    }


@router.post("/materials/{material_id}/match-existing")
def match_existing_spectrum(
    material_id: str,
    filename: str = Query(...),
    path: str = Query(None),
    polarity: str = Query("auto"),
    db: Session = Depends(get_db),
):
    """Match an existing experimental data file against the material's network."""
    # Try path first (e.g., "0510/PET/+PET-..."), then material dir, then 0510 subdir
    file_path = None
    if path:
        candidate = DATA_DIR / path
        if candidate.exists():
            file_path = candidate
    if not file_path:
        for candidate in [
            DATA_DIR / material_id / filename,
            DATA_DIR / "0510" / material_id / filename,
        ]:
            if candidate.exists():
                file_path = candidate
                break

    if not file_path:
        raise HTTPException(status_code=404, detail=f"Spectrum file not found: {filename}")

    content = file_path.read_text(encoding="utf-8", errors="replace")
    if polarity == "auto":
        polarity = _detect_polarity(filename)

    try:
        centroids, stats = _parse_and_preprocess(content, filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Parse error: {e}")

    result = _match_peaks(centroids, material_id, polarity, db)
    result["preprocess_stats"] = stats
    return result
