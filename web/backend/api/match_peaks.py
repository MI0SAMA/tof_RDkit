"""Peak matching API routes — upload spectra and match against formula networks."""

import csv
import io
import os
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import FormulaSummary, NetworkNode

router = APIRouter(prefix="/api", tags=["match-peaks"])

# Data directory for existing experimental spectra
DATA_DIR = Path(os.environ.get("DATA_DIR", "/app/data"))
PPM_TOLERANCE = 50  # default ppm
DA_TOLERANCE = 0.03  # default absolute tolerance


def _parse_peak_file(content: str, filename: str) -> list[dict]:
    """Parse a peak list file (CSV, TSV, or TXT). Returns list of {mz, intensity}."""
    # Try to detect format
    lines = content.strip().split("\n")
    if not lines:
        raise ValueError("Empty file")

    peaks = []
    # Try CSV/TSV first
    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff("\n".join(lines[:10]))
        delimiter = dialect.delimiter
    except Exception:
        delimiter = None

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Try delimiter-based parsing
        if delimiter:
            parts = line.split(delimiter)
        else:
            parts = line.split()

        # Try to extract mz and intensity
        numeric = []
        for p in parts:
            try:
                numeric.append(float(p.strip().rstrip(",")))
            except ValueError:
                continue

        if len(numeric) >= 2:
            mz, intensity = numeric[0], numeric[1]
        elif len(numeric) == 1:
            mz, intensity = numeric[0], 1.0
        else:
            continue

        if mz <= 0 or mz > 5000:
            continue

        peaks.append({"mz": mz, "intensity": intensity})

    if not peaks:
        raise ValueError("No valid peaks found in file")

    return peaks


def _detect_polarity(filename: str) -> str:
    """Guess polarity from filename."""
    name = filename.lower()
    if "positive" in name or "+" in name or "pos" in name:
        return "positive"
    if "negative" in name or "-" in name or "neg" in name:
        return "negative"
    return "unknown"


def _match_peaks(peaks: list[dict], compound_id: str, ion_mode: str, db: Session) -> dict:
    """Match peaks against the material's formula network by mass tolerance."""
    # Get formula summaries for this material
    formulas = (
        db.query(FormulaSummary)
        .filter(FormulaSummary.compound_id == compound_id)
        .all()
    )

    if not formulas:
        return {"error": f"No formulas found for material {compound_id}", "peaks": []}

    matched = []
    unmatched = []

    for peak in peaks:
        mz = peak["mz"]
        intensity = peak["intensity"]
        tolerance = max(DA_TOLERANCE, mz * PPM_TOLERANCE * 1e-6)

        best_match = None
        best_error = float("inf")

        for f in formulas:
            # Skip hidden formulas (structural only)
            if f.is_hidden:
                continue
            # Skip if ion_mode doesn't match (when we know polarity)
            if ion_mode != "unknown" and f.ion_mode != "neutral" and f.ion_mode != ion_mode:
                continue

            error = abs(f.exact_mass - mz)
            if error <= tolerance and error < best_error:
                best_error = error
                ppm_error = error / mz * 1e6 if mz > 0 else float("inf")
                best_match = {
                    "mz": mz,
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
                "mz": mz,
                "intensity": intensity,
                "reason": "no_match",
            })

    # Sort matched by formula_score descending
    matched.sort(key=lambda x: -x["formula_score"])

    total_peaks = len(peaks)
    matched_count = len(matched)

    return {
        "compound_id": compound_id,
        "detected_polarity": ion_mode,
        "total_peaks": total_peaks,
        "matched_peaks": matched_count,
        "unmatched_peaks": total_peaks - matched_count,
        "match_rate": round(matched_count / max(total_peaks, 1) * 100, 1),
        "tolerance_ppm": PPM_TOLERANCE,
        "tolerance_da": DA_TOLERANCE,
        "matched": matched,
        "unmatched": unmatched,
    }


@router.post("/materials/{material_id}/match-peaks")
async def match_peaks_endpoint(
    material_id: str,
    file: UploadFile = File(...),
    polarity: str = Query("auto", description="positive/negative/auto"),
    db: Session = Depends(get_db),
):
    """Upload a peak list and match against the material's formula network."""
    # Read and parse file
    content = (await file.read()).decode("utf-8", errors="replace")
    try:
        peaks = _parse_peak_file(content, file.filename or "")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if polarity == "auto":
        polarity = _detect_polarity(file.filename or "")

    return _match_peaks(peaks, material_id, polarity, db)


@router.get("/materials/{material_id}/spectra")
def list_available_spectra(material_id: str):
    """List available experimental peak files for a material from data/ directory."""
    material_dir = DATA_DIR / material_id
    if not material_dir.exists():
        return {"material_id": material_id, "spectra": []}

    spectra = []
    for f in sorted(material_dir.iterdir()):
        if f.suffix.lower() in (".txt", ".csv", ".tsv"):
            polarity = _detect_polarity(f.name)
            spectra.append({
                "filename": f.name,
                "path": str(f.relative_to(DATA_DIR)),
                "polarity": polarity,
                "size_kb": round(f.stat().st_size / 1024, 1),
            })

    return {"material_id": material_id, "spectra": spectra}


@router.post("/materials/{material_id}/match-existing")
def match_existing_spectrum(
    material_id: str,
    filename: str = Query(...),
    polarity: str = Query("auto"),
    db: Session = Depends(get_db),
):
    """Match an existing experimental data file against the material's network."""
    file_path = DATA_DIR / material_id / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Spectrum file not found: {filename}")

    content = file_path.read_text(encoding="utf-8", errors="replace")
    try:
        peaks = _parse_peak_file(content, filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if polarity == "auto":
        polarity = _detect_polarity(filename)

    return _match_peaks(peaks, material_id, polarity, db)
