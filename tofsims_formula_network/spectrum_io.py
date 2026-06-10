from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


def find_spectrum_files(data_dir: str) -> list[Path]:
    root = Path(data_dir)
    files = list(root.rglob("*.txt")) + list(root.rglob("*.TXT"))
    return sorted(path for path in files if path.name not in {"compounds.csv", "rf_candidates.csv"})


def _looks_like_header(values: list[str]) -> bool:
    """Check if a row looks like a column header (contains non-numeric text)."""
    numeric_count = 0
    for v in values:
        v = v.strip()
        try:
            float(v)
            numeric_count += 1
        except ValueError:
            pass
    # A header row should have at least one non-numeric entry
    return numeric_count < len(values)


def _map_columns(
    df: pd.DataFrame, numeric_cols: list[tuple[int, pd.Series]]
) -> tuple[pd.Series, pd.Series]:
    """Map numeric columns to mz and intensity using header detection.

    Returns (mz_series, intensity_series).
    """
    mz_keywords = {"m/z", "mz", "mass", "m_z", "mass(u)", "(u)"}
    intensity_keywords = {"intensity", "int", "intens", "counts", "count", "cts"}

    first_row = [str(v) for v in df.iloc[0].tolist()]

    # Try to detect header row
    if _looks_like_header(first_row):
        header_lower = [h.lower().strip() for h in first_row]
        mz_col_idx = None
        intensity_col_idx = None

        for idx, h in enumerate(header_lower):
            if h in mz_keywords:
                mz_col_idx = idx
            elif h in intensity_keywords:
                intensity_col_idx = idx

        # If we found m/z header, use that column for mz
        mz_series = None
        intensity_series = None

        # Build a dict of col_idx -> series for quick lookup
        numeric_map = {col_idx: series for col_idx, series in numeric_cols}

        if mz_col_idx is not None and mz_col_idx in numeric_map:
            mz_series = numeric_map[mz_col_idx]
        if intensity_col_idx is not None and intensity_col_idx in numeric_map:
            intensity_series = numeric_map[intensity_col_idx]

        # Fill in missing with remaining numeric cols (skip used ones)
        used = {mz_col_idx, intensity_col_idx}
        remaining = [(c, s) for c, s in numeric_cols if c not in used]

        if mz_series is None and remaining:
            mz_series = remaining.pop(0)[1]
        if intensity_series is None and remaining:
            intensity_series = remaining.pop(0)[1]
        elif intensity_series is None and mz_series is not None:
            # Find a different column for intensity
            for c, s in numeric_cols:
                if s is not mz_series:
                    intensity_series = s
                    break

        if mz_series is not None and intensity_series is not None:
            return mz_series, intensity_series

    # Fallback: first two numeric columns
    return numeric_cols[0][1], numeric_cols[1][1]


def read_spectrum_txt(path: Path) -> pd.DataFrame:
    raw = path.read_bytes()
    sample = raw[:4096]
    printable = sum(1 for byte in sample if byte in b"\r\n\t" or 32 <= byte <= 126)
    printable_ratio = printable / max(1, len(sample))
    if sample.count(0) > 8 or printable_ratio < 0.85:
        raise ValueError("No numeric peak columns found; file appears binary or proprietary")
    text = raw.decode("utf-8", errors="ignore")
    rows: list[list[str]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [part for part in re.split(r"[\s,]+", line) if part]
        if len(parts) >= 2:
            rows.append(parts)
    if not rows:
        raise ValueError("No numeric peak columns found")
    max_cols = max(len(row) for row in rows)
    padded = [row + [""] * (max_cols - len(row)) for row in rows]
    df = pd.DataFrame(padded)
    numeric_cols = []
    for col in df.columns:
        converted = pd.to_numeric(df[col], errors="coerce")
        if converted.notna().sum() > 0:
            numeric_cols.append((col, converted))
    if len(numeric_cols) < 2:
        raise ValueError("No numeric peak columns found")
    mz_series, intensity_series = _map_columns(df, numeric_cols)
    out = pd.DataFrame({"mz": mz_series, "intensity": intensity_series}).dropna()
    # Drop header rows that produced NaN after pd.to_numeric
    out = out[out["mz"] > 0].sort_values("mz").reset_index(drop=True)
    if out.empty:
        raise ValueError("No valid mz/intensity rows found")
    return out


def standardize_spectrum(df: pd.DataFrame, spectrum_id: str, source_file: str) -> pd.DataFrame:
    out = df[["mz", "intensity"]].copy()
    out.insert(0, "spectrum_id", spectrum_id)
    out["source_file"] = source_file
    return out[["spectrum_id", "mz", "intensity", "source_file"]]


def preprocess_spectrum(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    spec = cfg["spectrum"]
    out = df[(df["mz"] >= spec["min_mz"]) & (df["mz"] <= spec["max_mz"])]
    out = out[out["intensity"] >= spec["min_intensity"]].copy()
    if spec.get("normalize_intensity", True) and not out.empty and out["intensity"].max() > 0:
        out["intensity"] = out["intensity"] / out["intensity"].max() * 100.0
    top_n = spec.get("top_n_peaks")
    if top_n:
        out = out.sort_values("intensity", ascending=False).head(int(top_n)).sort_values("mz")
    return out.reset_index(drop=True)


def write_parsed_spectrum(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
