"""Peak matching API — delegates to evaluation_v2 for algorithm consistency.

Uses the EXACT same functions as the CLI: evaluation_v2.evaluate_spectrum().
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
    if name.startswith("-"):
        return "negative"
    return "positive"


def _match_spectrum_file(file_path: Path, material_id: str, db: Session) -> dict:
    """Match a spectrum file against the material's network using evaluation_v2 logic."""
    # Import project modules (same as CLI)
    from tofsims_formula_network.evaluation_v2 import (
        centroid_peaks,
        classify_peak,
        _match_peak,
    )
    from tofsims_formula_network.spectrum_io import (
        preprocess_spectrum,
        read_spectrum_txt,
        standardize_spectrum,
    )

    cfg = _load_config()
    eval_cfg = cfg.get("evaluation_v2", {})

    # Step 1: Parse and preprocess (same as CLI)
    df = read_spectrum_txt(file_path)
    pre = preprocess_spectrum(df, cfg)
    std = standardize_spectrum(pre, "web_match", str(file_path))

    # Step 2: Centroid (uses EXACT project code)
    centroid_da = float(eval_cfg.get("centroid_da", 0.03))
    centroid_ppm = float(eval_cfg.get("centroid_ppm", 50))
    centroided = centroid_peaks(std, centroid_da, centroid_ppm)

    # Step 3: Build formula network DataFrame (same as evaluation loads from CSV)
    formulas = (
        db.query(FormulaSummary)
        .filter(FormulaSummary.compound_id == material_id)
        .all()
    )
    if not formulas:
        return {"error": f"No formulas found for {material_id}"}

    material_network = pd.DataFrame([{
        "compound_id": f.compound_id,
        "formula": f.formula,
        "ion_mode": f.ion_mode,
        "exact_mass": f.exact_mass,
        "formula_score": f.formula_score,
        "diagnostic_tag": f.diagnostic_tag,
        "generation_types": f.generation_types,
        "representative_path": f.representative_path,
    } for f in formulas])

    # Step 4: Match each peak (same classify + match logic as CLI)
    ion_mode = _detect_polarity(file_path.name)
    material_network_filtered = material_network[
        material_network["ion_mode"].astype(str) == ion_mode
    ]

    matched = []
    unmatched = []
    peak_rows = []

    for _, peak in centroided.iterrows():
        mz = float(peak["mz"])
        intensity = float(peak["intensity"])
        category, label, included = classify_peak(mz, ion_mode, cfg)

        # Contaminants and low-mass: match anyway but flag as suspect
        suspect = category in ("contaminant", "low_mass_background")
        do_match = included or suspect

        if do_match and not material_network_filtered.empty:
            match_result = _match_peak(mz, material_network_filtered, cfg)
        else:
            match_result = {
                "matched": False,
                "matched_formula": "",
                "matched_mass_error_da": "",
                "matched_mass_error_ppm": "",
                "matched_formula_score": "",
            }

        peak_rows.append({
            "mz": round(mz, 4),
            "intensity": intensity,
            "category": category,
            "category_label": label,
            "included": included or suspect,  # suspect peaks are "included" for recall calc
            "suspect": suspect,
            "matched": match_result["matched"],
            "matched_formula": match_result["matched_formula"],
            "mass_error_da": round(float(match_result.get("matched_mass_error_da", 0) or 0), 6),
            "mass_error_ppm": round(float(match_result.get("matched_mass_error_ppm", 0) or 0), 2),
            "formula_score": float(match_result.get("matched_formula_score", 0) or 0),
        })

        if match_result["matched"]:
            f = next((x for x in formulas if x.formula == match_result["matched_formula"] and x.ion_mode == ion_mode), None)
            matched.append({
                "mz": round(mz, 4),
                "intensity": intensity,
                "matched_formula": match_result["matched_formula"],
                "ion_mode": ion_mode,
                "exact_mass": f.exact_mass if f else 0,
                "mass_error_da": round(float(match_result.get("matched_mass_error_da", 0) or 0), 6),
                "mass_error_ppm": round(float(match_result.get("matched_mass_error_ppm", 0) or 0), 2),
                "formula_score": float(match_result.get("matched_formula_score", 0) or 0),
                "diagnostic_tag": f.diagnostic_tag if f else "",
                "generation_types": f.generation_types if f else "",
                "representative_path": f.representative_path if f else "",
                "suspect": suspect,
            })
        elif included or suspect:
            unmatched.append({
                "mz": round(mz, 4),
                "intensity": intensity,
                "reason": "no_match",
                "suspect": suspect,
            })

    matched.sort(key=lambda x: -x["formula_score"])

    # Count categories
    categories = {}
    for r in peak_rows:
        cat = r["category"]
        categories[cat] = categories.get(cat, 0) + 1

    included_peaks = [r for r in peak_rows if r["included"]]
    included_matched = [r for r in included_peaks if r["matched"]]

    total_centroid = len(peak_rows)
    total_included = len(included_peaks)
    total_matched = len(included_matched)

    return {
        "compound_id": material_id,
        "detected_polarity": ion_mode,
        "total_centroid_peaks": total_centroid,
        "included_peaks": total_included,
        "excluded_peaks": total_centroid - total_included,
        "matched_peaks": total_matched,
        "unmatched_peaks": total_included - total_matched,
        "match_rate": round(total_matched / max(total_included, 1) * 100, 1),
        "tolerance_ppm": float(eval_cfg.get("match_ppm", 50)),
        "tolerance_da": float(eval_cfg.get("match_da", 0.03)),
        "min_main_mz": float(eval_cfg.get("min_main_mz", 25.0)),
        "categories": categories,
        "matched": matched,
        "unmatched": unmatched,
        "all_peaks": peak_rows,
    }


@router.post("/materials/{material_id}/match-peaks")
async def match_peaks_endpoint(
    material_id: str,
    file: UploadFile = File(...),
    polarity: str = Query("auto"),
    db: Session = Depends(get_db),
):
    """Upload a peak list file and match against formula network (same algorithm as CLI)."""
    content = await file.read()
    # Write to temp file (spectrum_io reads from file path)
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".txt", delete=False) as tf:
        tf.write(content)
        tmp_path = Path(tf.name)

    try:
        result = _match_spectrum_file(tmp_path, material_id, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Processing error: {e}")
    finally:
        tmp_path.unlink(missing_ok=True)


@router.get("/materials/{material_id}/spectra")
def list_available_spectra(material_id: str):
    """List available experimental peak files from data/{material}/ and data/0510/{material}/."""
    spectra = []

    for base_dir in [DATA_DIR / material_id, DATA_DIR / "0510" / material_id]:
        if base_dir.exists():
            for f in sorted(base_dir.iterdir()):
                if f.suffix.lower() in (".txt", ".csv", ".tsv"):
                    polarity = _detect_polarity(f.name)
                    spectra.append({
                        "filename": f.name,
                        "path": str(f.relative_to(DATA_DIR)),
                        "polarity": polarity,
                        "size_kb": round(f.stat().st_size / 1024, 1),
                        "annotated": "0510" in str(f),
                    })

    return {"material_id": material_id, "spectra": spectra}


@router.post("/materials/{material_id}/match-existing")
def match_existing_spectrum(
    material_id: str,
    filename: str = Query(...),
    path: str = Query(None),
    db: Session = Depends(get_db),
):
    """Match an existing experimental data file against the material's network."""
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

    try:
        return _match_spectrum_file(file_path, material_id, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Processing error: {e}")
