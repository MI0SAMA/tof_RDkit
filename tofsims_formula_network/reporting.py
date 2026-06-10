from __future__ import annotations

from pathlib import Path

import pandas as pd


def _markdown_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in cols) + " |")
    return "\n".join(lines)


def write_matches_csv(matches: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if matches.empty and len(matches.columns) == 0:
        matches = pd.DataFrame(columns=[
            "spectrum_id",
            "peak_mz",
            "intensity",
            "rf_formula",
            "matched_formula",
            "compound_id",
            "compound_name",
            "generation_type",
            "path",
            "network_score",
            "final_score",
            "mass_error_da",
            "mass_error_ppm",
        ])
    matches.to_csv(path, index=False)


def write_markdown_report(spectrum_id: str, matches: pd.DataFrame, spectrum_df: pd.DataFrame, output_path: Path, config: dict) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    peak_count = 0 if spectrum_df.empty else len(spectrum_df)
    match_count = 0 if matches.empty else len(matches)
    lines = [
        f"# TOF-SIMS Formula Network Matching Report: {spectrum_id}",
        "",
        "## 1. Input",
        "",
        f"- Peak count: {peak_count}",
        f"- Matching tolerance: {config['spectrum']['peak_match_ppm']} ppm or {config['spectrum']['peak_match_da']} Da",
        "",
        "## 2. Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Total peaks | {peak_count} |",
        f"| Network matched rows | {match_count} |",
        "",
        "## 3. Top matched peaks",
        "",
    ]
    if matches.empty:
        lines.append("No matches.")
    else:
        show_cols = [col for col in ["peak_mz", "intensity", "candidate_formula", "matched_formula", "source_name", "compound_name", "generation_type", "path", "final_score"] if col in matches.columns]
        lines.append(_markdown_table(matches.sort_values("final_score", ascending=False).head(25)[show_cols]))
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
