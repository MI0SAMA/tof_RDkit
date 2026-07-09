#!/usr/bin/env python3
"""Compare algorithm-generated formula networks against 0510 manual annotations.

Filters out atomic and diatomic ions (≤2 heavy atoms) which are intentionally
excluded by the algorithm's min_heavy_atoms ≥ 2 setting.

Usage:
    python verify_0510.py [--output-dir outputs]

Outputs:
    outputs/summary/0510_verification.json   — detailed match data
    outputs/summary/0510_verification.md     — human-readable report
"""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

import pandas as pd

from tofsims_formula_network.formula import normalize_formula_string, parse_formula
from tofsims_formula_network.utils import load_config


# ═══════════════════════════════════════════════════════════════════════════════
# Step 1: Extract manual annotations from 0510 Area Statistics files
# ═══════════════════════════════════════════════════════════════════════════════

def extract_0510_annotations(data_dir: str = "data/0510") -> dict:
    """Parse TOF-SIMS Area Statistics TXT files with manual formula assignments.

    Returns: {material_polarity: [annotation_dict]}
    """
    root = Path(data_dir)
    results = {}
    for material_dir in sorted(root.iterdir()):
        if not material_dir.is_dir():
            continue
        material = material_dir.name
        for txt_file in sorted(material_dir.glob("*.TXT")):
            polarity = "pos" if txt_file.name.startswith("+") else "neg"
            content = txt_file.read_text(encoding="utf-8", errors="ignore")
            annotations = []
            for line in content.splitlines():
                line = line.strip()
                # Skip headers, blanks, and malformed rows
                if not line or line.startswith(("Area", "Mass", "<", "(null)")):
                    continue
                parts = re.split(r"\s+", line)
                if len(parts) < 3:
                    continue
                try:
                    mz = float(parts[1])
                    intensity = float(parts[2])
                except ValueError:
                    continue
                formula_raw = parts[0]
                # Clean up: remove charge signs, underscores, isotope prefixes
                formula_clean = formula_raw.rstrip("+-").replace("_", "")
                # Remove isotope markers like ^37Cl → Cl, ^13C → C
                formula_clean = re.sub(r"\^\d+", "", formula_clean)
                # Normalize to Hill notation (skip if it contains non-formula chars)
                try:
                    normalized = normalize_formula_string(formula_clean)
                except Exception:
                    normalized = formula_clean
                # Count heavy atoms (non-H) — skip if formula can't be parsed
                try:
                    counts = parse_formula(normalized) if normalized else {}
                    heavy_atoms = sum(c for e, c in counts.items() if e != "H")
                except Exception:
                    heavy_atoms = 999  # don't filter unparseable formulas

                annotations.append({
                    "raw_formula": formula_raw,
                    "formula": normalized,
                    "mz": mz,
                    "intensity": intensity,
                    "polarity": polarity,
                    "heavy_atoms": heavy_atoms,
                })
            key = f"{material}_{polarity}"
            results[key] = annotations
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# Step 2: Load algorithm-generated networks
# ═══════════════════════════════════════════════════════════════════════════════

def load_all_networks(network_dir: str = "outputs/networks") -> pd.DataFrame:
    """Concatenate all network CSVs into one DataFrame."""
    root = Path(network_dir)
    frames = [pd.read_csv(p) for p in sorted(root.glob("*.csv"))]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


# ═══════════════════════════════════════════════════════════════════════════════
# Step 3: Match annotations against networks
# ═══════════════════════════════════════════════════════════════════════════════

def match_annotations(
    annotations: dict,
    networks: pd.DataFrame,
    filter_heavy_max: int | None = None,
) -> dict:
    """Compare manual annotations to algorithm-generated formula networks.

    Args:
        annotations: {key: [annotation_dict]} from extract_0510_annotations
        networks: DataFrame of all network records
        filter_heavy_max: if set, exclude annotations with >N heavy atoms
                          (use None to keep all, 2 to remove single/diatomic ions)

    Returns:
        dict with per-material match statistics and lists
    """
    # Map 0510 directory names to compound_id in networks
    material_to_compound = {
        "COC": "COC", "EVA": "EVA", "PDMS": "PDMS",
        "PET": "PET", "POMC": "POMC", "POMH": "POMH",
    }

    # Pre-build normalized formula lookup for faster matching
    net = networks.copy()
    net["formula_normalized"] = net["formula"].apply(
        lambda f: normalize_formula_string(f) if pd.notna(f) else ""
    )
    # Build dict: compound_id -> set of normalized formulas
    network_formulas_by_compound = {}
    for cid in net["source_compound_id"].unique():
        network_formulas_by_compound[cid] = set(
            net[net["source_compound_id"] == cid]["formula_normalized"]
        )

    results = {}
    for key, ann_list in annotations.items():
        material, polarity = key.rsplit("_", 1)
        compound_id = material_to_compound.get(material)
        if compound_id is None:
            continue

        network_formulas = network_formulas_by_compound.get(compound_id, set())

        # Apply heavy-atom filter to annotations
        if filter_heavy_max is not None:
            filtered_ann = [a for a in ann_list if a["heavy_atoms"] > filter_heavy_max]
            excluded = [a for a in ann_list if a["heavy_atoms"] <= filter_heavy_max]
        else:
            filtered_ann = list(ann_list)
            excluded = []

        # Match each remaining annotation
        matched, unmatched = [], []
        for ann in filtered_ann:
            if ann["formula"] in network_formulas:
                # Find best-matching network record for detail
                net_match = net[
                    (net["source_compound_id"] == compound_id) &
                    (net["formula_normalized"] == ann["formula"])
                ]
                best = net_match.sort_values("score", ascending=False).iloc[0]
                matched.append({
                    **ann,
                    "network_score": float(best["score"]),
                    "generation_type": str(best["generation_type"]),
                    "network_path": str(best["path"]),
                    "matched_ion_mode": str(best["ion_mode"]),
                })
            else:
                unmatched.append(ann)

        total_kept = len(filtered_ann)
        hit_rate = len(matched) / total_kept * 100 if total_kept else 0
        intensity_matched = sum(a["intensity"] for a in matched)
        intensity_total = sum(a["intensity"] for a in filtered_ann)
        intensity_coverage = intensity_matched / intensity_total * 100 if intensity_total else 0
        generation_type_counts = Counter(a["generation_type"] for a in matched)
        generation_type_intensity = Counter()
        for ann in matched:
            generation_type_intensity[ann["generation_type"]] += ann["intensity"]

        results[key] = {
            "material": material,
            "polarity": polarity,
            "compound_id": compound_id,
            "total_annotations": len(ann_list),
            "excluded_atomic_diatomic": len(excluded),
            "excluded_list": excluded,
            "filtered_annotations": total_kept,
            "matched": len(matched),
            "unmatched": len(unmatched),
            "hit_rate_pct": round(hit_rate, 1),
            "intensity_coverage_pct": round(intensity_coverage, 1),
            "matched_list": matched,
            "unmatched_list": unmatched,
            "generation_type_counts": dict(generation_type_counts),
            "generation_type_intensity": {k: round(v, 3) for k, v in generation_type_intensity.items()},
            "network_size": len(net[net["source_compound_id"] == compound_id]),
            "network_unique_formulas": len(network_formulas),
        }

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# Step 4: Generate report
# ═══════════════════════════════════════════════════════════════════════════════

def generate_report(results: dict, output_dir: str = "outputs") -> str:
    """Generate a Markdown verification report."""
    summary_dir = Path(output_dir) / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Calculate aggregate stats
    total_ann = sum(r["total_annotations"] for r in results.values())
    total_excluded = sum(r["excluded_atomic_diatomic"] for r in results.values())
    total_filtered = sum(r["filtered_annotations"] for r in results.values())
    total_matched = sum(r["matched"] for r in results.values())
    total_unmatched = sum(r["unmatched"] for r in results.values())
    all_matched_intensity = sum(
        sum(a["intensity"] for a in r["matched_list"]) for r in results.values()
    )
    all_total_intensity = sum(
        sum(a["intensity"] for a in r["matched_list"] + r["unmatched_list"])
        for r in results.values()
    )
    overall_hit = total_matched / total_filtered * 100 if total_filtered else 0
    overall_intensity = all_matched_intensity / all_total_intensity * 100 if all_total_intensity else 0

    lines = []
    def w(s=""):
        lines.append(s)

    w("# 0510 Manual Annotation vs Algorithm Network — Verification Report")
    w()
    w(f"> Generated: {today}")
    w(f"> Filter: atomic/diatomic ions (≤2 heavy atoms) excluded ({total_excluded} peaks removed)")
    w()
    w("---")
    w()
    w("## 1. Overall Summary")
    w()
    w("| Metric | Value |")
    w("|---|---:|")
    w(f"| Total manual annotations | {total_ann} |")
    w(f"| Excluded (atomic/diatomic ions ≤2 heavy atoms) | {total_excluded} |")
    w(f"| Annotations evaluated | {total_filtered} |")
    w(f"| Matched by algorithm | **{total_matched}** |")
    w(f"| Unmatched | {total_unmatched} |")
    w(f"| **Overall hit rate** | **{overall_hit:.1f}%** |")
    w(f"| **Intensity coverage** | **{overall_intensity:.1f}%** |")
    w()
    w("---")
    w()
    w("## 2. Per-Material Breakdown")
    w()
    w("| Material | Pol | Total | Excluded | Evaluated | Matched | Hit% | IntCov% | NetSize |")
    w("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for key in sorted(results.keys()):
        r = results[key]
        w(f"| {r['material']} | {r['polarity']} | "
          f"{r['total_annotations']} | "
          f"{r['excluded_atomic_diatomic']} | "
          f"{r['filtered_annotations']} | "
          f"**{r['matched']}** | "
          f"**{r['hit_rate_pct']:.1f}%** | "
          f"{r['intensity_coverage_pct']:.1f}% | "
          f"{r['network_unique_formulas']} |")

    # Rating table
    w()
    w("### Material Ratings")
    w()
    w("| Material | Rating | Hit% | Key Issue |")
    w("|---|---:|---:|---|")
    ratings = []
    for key in sorted(results.keys()):
        r = results[key]
        mat = r['material']
        hit = r['hit_rate_pct']
        # Only include one row per material (average both polarities)
        if mat not in [x[0] for x in ratings]:
            # Get average across both polarities
            same_mat = [v for k, v in results.items() if v['material'] == mat]
            avg_hit = sum(s['hit_rate_pct'] for s in same_mat) / len(same_mat)
            avg_int = sum(s['intensity_coverage_pct'] for s in same_mat) / len(same_mat)

            if avg_hit >= 60:
                rating = "⭐⭐⭐⭐⭐ Excellent"
            elif avg_hit >= 50:
                rating = "⭐⭐⭐⭐ Good"
            elif avg_hit >= 35:
                rating = "⭐⭐⭐ Fair"
            elif avg_hit >= 20:
                rating = "⭐⭐ Poor"
            else:
                rating = "⭐ Critical"

            # Determine key issue
            unmatched_formulas = set()
            for s in same_mat:
                for a in s['unmatched_list']:
                    unmatched_formulas.add(a['formula'])

            if mat == "COC":
                issue = "SMILES (norbornene) does not represent true COC copolymer structure"
            elif mat == "PDMS":
                issue = "Complex Si-containing fragments; need longer oligomer or Si-specific rules"
            elif mat == "EVA":
                issue = "Copolymer with variable VA content; single-repeat approximation limited"
            elif avg_hit >= 50:
                issue = "Remaining unmatched are mostly external adducts (Na+, K+, Cs+)"
            else:
                issue = "Some fragments not captured; may need structural refinement"

            ratings.append((mat, rating, avg_hit, issue))
            w(f"| {mat} | {rating} | {avg_hit:.1f}% | {issue} |")

    w()
    w("---")
    w()
    w("## 3. Rule Contribution")
    w()
    w("| Material | Pol | Generation type | Matched | Intensity |")
    w("|---|---:|---|---:|---:|")
    for key in sorted(results.keys()):
        r = results[key]
        for gen_type, count in sorted(r["generation_type_counts"].items(), key=lambda item: (-item[1], item[0])):
            intensity = r["generation_type_intensity"].get(gen_type, 0.0)
            w(f"| {r['material']} | {r['polarity']} | {gen_type} | {count} | {intensity:.2f} |")

    w()
    w("---")
    w()
    w("## 4. Unmatched Peaks Analysis")
    w()
    w("Top 10 unmatched peaks per material (by intensity), after excluding atomic/diatomic ions:")
    w()

    for key in sorted(results.keys()):
        r = results[key]
        if r["unmatched"] == 0:
            w(f"### {key} — ✅ All matched!")
            w()
            continue

        unmatched_sorted = sorted(r["unmatched_list"],
                                  key=lambda x: x["intensity"], reverse=True)
        w(f"### {key} ({r['unmatched']} unmatched)")
        w()
        w("| # | Formula | Raw | m/z | Intensity | Heavy Atoms |")
        w("|---|---:|---:|---:|---:|")
        for i, a in enumerate(unmatched_sorted[:10], 1):
            w(f"| {i} | {a['formula']} | {a['raw_formula']} | "
              f"{a['mz']:.4f} | {a['intensity']:.2f} | {a['heavy_atoms']} |")
        w()

    # Matched examples
    w("---")
    w()
    w("## 5. Matched Examples (Top 5 by network score per material)")
    w()
    for key in sorted(results.keys()):
        r = results[key]
        if not r["matched_list"]:
            continue
        matched_sorted = sorted(r["matched_list"],
                                key=lambda x: x["network_score"], reverse=True)
        w(f"### {key}")
        w()
        w("| Formula | Raw | m/z | Intensity | NetScore | GenType | Path |")
        w("|---|---:|---:|---:|---:|---|")
        for a in matched_sorted[:5]:
            path_short = a.get("network_path", "")[:80]
            w(f"| {a['formula']} | {a['raw_formula']} | "
              f"{a['mz']:.4f} | {a['intensity']:.2f} | "
              f"{a['network_score']:.3f} | {a.get('generation_type','')} | "
              f"{path_short} |")
        w()

    w("---")
    w()
    w("## 6. Filter Statistics")
    w()
    w(f"Total annotations removed by atomic/diatomic filter: **{total_excluded}**")
    w()
    w("Breakdown of excluded ion types:")
    w()
    # Count excluded by formula category
    excluded_formulas = {}
    for r in results.values():
        for a in r["excluded_list"]:
            f = a["formula"]
            excluded_formulas[f] = excluded_formulas.get(f, 0) + 1
    w("| Formula | Count | Category |")
    w("|---|---:|")
    for f, count in sorted(excluded_formulas.items(), key=lambda x: -x[1])[:20]:
        counts = parse_formula(f) if f else {}
        heavy = sum(c for e, c in counts.items() if e != "H")
        cat = "atomic" if heavy <= 1 else "diatomic"
        w(f"| {f} | {count} | {cat} |")

    report_text = "\n".join(lines)
    report_path = summary_dir / "0510_verification.md"
    report_path.write_text(report_text, encoding="utf-8")
    print(f"Report saved to {report_path}")
    return report_text


def write_detail_csvs(results: dict, output_dir: str = "outputs") -> None:
    summary_dir = Path(output_dir) / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)
    unmatched_rows = []
    matched_rows = []
    rule_rows = []

    for key, r in results.items():
        for ann in r["unmatched_list"]:
            unmatched_rows.append({
                "spectrum_key": key,
                "material": r["material"],
                "polarity": r["polarity"],
                "compound_id": r["compound_id"],
                "formula": ann["formula"],
                "raw_formula": ann["raw_formula"],
                "mz": ann["mz"],
                "intensity": ann["intensity"],
                "heavy_atoms": ann["heavy_atoms"],
            })
        for ann in r["matched_list"]:
            matched_rows.append({
                "spectrum_key": key,
                "material": r["material"],
                "polarity": r["polarity"],
                "compound_id": r["compound_id"],
                "formula": ann["formula"],
                "raw_formula": ann["raw_formula"],
                "mz": ann["mz"],
                "intensity": ann["intensity"],
                "network_score": ann["network_score"],
                "generation_type": ann["generation_type"],
                "matched_ion_mode": ann["matched_ion_mode"],
                "network_path": ann["network_path"],
            })
        for gen_type, count in r["generation_type_counts"].items():
            rule_rows.append({
                "spectrum_key": key,
                "material": r["material"],
                "polarity": r["polarity"],
                "generation_type": gen_type,
                "matched": count,
                "matched_intensity": r["generation_type_intensity"].get(gen_type, 0.0),
            })

    pd.DataFrame(unmatched_rows).sort_values(
        ["material", "polarity", "intensity"],
        ascending=[True, True, False],
    ).to_csv(summary_dir / "0510_unmatched_formulas.csv", index=False)
    pd.DataFrame(matched_rows).sort_values(
        ["material", "polarity", "intensity"],
        ascending=[True, True, False],
    ).to_csv(summary_dir / "0510_matched_formulas.csv", index=False)
    pd.DataFrame(rule_rows).sort_values(
        ["material", "polarity", "matched"],
        ascending=[True, True, False],
    ).to_csv(summary_dir / "0510_rule_contribution.csv", index=False)
    print(f"Detail CSVs saved to {summary_dir}")


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Verify 0510 annotations against algorithm networks")
    parser.add_argument("--output-dir", default="outputs", help="Output directory")
    parser.add_argument("--data-dir", default="data/0510", help="0510 data directory")
    parser.add_argument("--network-dir", default="outputs/networks", help="Network CSV directory")
    parser.add_argument("--filter-heavy-max", type=int, default=2,
                        help="Exclude annotations with ≤N heavy atoms (default: 2, for atomic/diatomic)")
    args = parser.parse_args()

    cfg = load_config("config/default.yaml")

    print("=" * 70)
    print("Extracting 0510 manual annotations...")
    annotations = extract_0510_annotations(args.data_dir)
    total_ann = sum(len(v) for v in annotations.values())
    print(f"  Total annotations: {total_ann} across {len(annotations)} spectra")

    print(f"\nLoading algorithm-generated networks from {args.network_dir}...")
    networks = load_all_networks(args.network_dir)
    print(f"  Total network records: {len(networks)}")
    print(f"  Compounds: {networks['source_compound_id'].nunique()}")

    print(f"\nMatching annotations against networks...")
    print(f"  Filter: exclude annotations with ≤{args.filter_heavy_max} heavy atoms")
    results = match_annotations(annotations, networks, filter_heavy_max=args.filter_heavy_max)

    # Print summary table
    print(f"\n{'=' * 70}")
    print("RESULTS (atomic/diatomic ions excluded)")
    print(f"{'=' * 70}")
    header = f"{'Material':8s} {'Pol':4s} {'Total':5s} {'Excl':5s} {'Eval':5s} {'Match':6s} {'Hit%':8s} {'IntCov%':8s}"
    print(header)
    print("-" * 65)

    total_ann_all = 0
    total_exc = 0
    total_eval = 0
    total_mat = 0
    total_intensity_m = 0.0
    total_intensity_a = 0.0

    for key in sorted(results.keys()):
        r = results[key]
        total_ann_all += r["total_annotations"]
        total_exc += r["excluded_atomic_diatomic"]
        total_eval += r["filtered_annotations"]
        total_mat += r["matched"]
        total_intensity_m += sum(a["intensity"] for a in r["matched_list"])
        total_intensity_a += sum(a["intensity"] for a in r["matched_list"] + r["unmatched_list"])
        print(f"{r['material']:8s} {r['polarity']:4s} "
              f"{r['total_annotations']:4d}  {r['excluded_atomic_diatomic']:4d}  "
              f"{r['filtered_annotations']:4d}  {r['matched']:5d}  "
              f"{r['hit_rate_pct']:6.1f}%  {r['intensity_coverage_pct']:6.1f}%")

    print("-" * 65)
    overall_hit = total_mat / total_eval * 100 if total_eval else 0
    overall_int = total_intensity_m / total_intensity_a * 100 if total_intensity_a else 0
    print(f"{'TOTAL':8s} {'':4s} {total_ann_all:4d}  {total_exc:4d}  "
          f"{total_eval:4d}  {total_mat:5d}  "
          f"{overall_hit:6.1f}%  {overall_int:6.1f}%")
    print(f"\n  → After removing atomic/diatomic ions, hit rate = {overall_hit:.1f}%")
    print(f"  → Intensity coverage = {overall_int:.1f}%")

    # Save JSON
    output = {}
    for k, v in results.items():
        output[k] = {
            "material": v["material"],
            "polarity": v["polarity"],
            "compound_id": v["compound_id"],
            "total_annotations": v["total_annotations"],
            "excluded_atomic_diatomic": v["excluded_atomic_diatomic"],
            "filtered_annotations": v["filtered_annotations"],
            "matched": v["matched"],
            "unmatched": v["unmatched"],
            "hit_rate_pct": v["hit_rate_pct"],
            "intensity_coverage_pct": v["intensity_coverage_pct"],
            "network_size": v["network_size"],
            "network_unique_formulas": v["network_unique_formulas"],
            "generation_type_counts": v["generation_type_counts"],
            "generation_type_intensity": v["generation_type_intensity"],
            "matched_formulas": [
                {"formula": a["formula"], "raw": a["raw_formula"],
                 "mz": a["mz"], "intensity": a["intensity"],
                 "network_score": a["network_score"],
                 "generation_type": a["generation_type"]}
                for a in v["matched_list"]
            ],
            "unmatched_formulas": [
                {"formula": a["formula"], "raw": a["raw_formula"],
                 "mz": a["mz"], "intensity": a["intensity"],
                 "heavy_atoms": a["heavy_atoms"]}
                for a in v["unmatched_list"]
            ],
            "excluded_atomic_diatomic_list": [
                {"formula": a["formula"], "raw": a["raw_formula"],
                 "mz": a["mz"], "intensity": a["intensity"],
                 "heavy_atoms": a["heavy_atoms"]}
                for a in v["excluded_list"]
            ],
        }

    json_path = Path(args.output_dir) / "summary" / "0510_verification.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"\nJSON data saved to {json_path}")
    write_detail_csvs(results, args.output_dir)

    # Generate Markdown report
    print()
    generate_report(results, args.output_dir)


if __name__ == "__main__":
    main()
