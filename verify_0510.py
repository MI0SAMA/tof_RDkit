"""Compare algorithm-generated formula networks against 0510 manual annotations."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

from tofsims_formula_network.formula import normalize_formula_string, parse_formula
from tofsims_formula_network.utils import load_config

# ── Step 1: Extract manual annotations from 0510 files ──────────────────────
def extract_0510_annotations(data_dir: str = "data/0510") -> dict:
    """Parse the Area Statistics format files. Returns {material_polarity: [annotations]}."""
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
                # Normalize: strip +/-, replace underscores
                formula_clean = formula_raw.rstrip("+-").replace("_", "")
                try:
                    normalized = normalize_formula_string(formula_clean)
                except Exception:
                    normalized = formula_clean  # keep raw if can't parse
                annotations.append({
                    "raw_formula": formula_raw,
                    "formula": normalized,
                    "mz": mz,
                    "intensity": intensity,
                    "polarity": polarity,
                })
            key = f"{material}_{polarity}"
            results[key] = annotations
            print(f"  {material} {polarity:3s}: {len(annotations):3d} manual annotations")
    return results


# ── Step 2: Load algorithm-generated networks ───────────────────────────────
def load_all_networks(network_dir: str = "outputs/networks") -> pd.DataFrame:
    """Load all network CSVs into one DataFrame."""
    root = Path(network_dir)
    frames = []
    for path in sorted(root.glob("*.csv")):
        df = pd.read_csv(path)
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


# ── Step 3: Match annotations against networks ──────────────────────────────
def match_annotations(annotations: dict, networks: pd.DataFrame) -> dict:
    """For each 0510 material, find which manual formulas appear in the network."""

    # Map 0510 material names to compound_ids in the network
    material_to_compound = {
        "COC": "COC",
        "EVA": "EVA",
        "PDMS": "PDMS",
        "PET": "PET",
        "POMC": "POMC",
        "POMH": "POMH",
    }

    results = {}
    for key, ann_list in annotations.items():
        material, polarity = key.rsplit("_", 1)
        compound_id = material_to_compound.get(material)
        if compound_id is None:
            print(f"  {key}: no matching compound_id, skipping")
            continue

        # Get network formulas for this compound
        net = networks[networks["source_compound_id"] == compound_id].copy()
        net["formula_normalized"] = net["formula"].apply(
            lambda f: normalize_formula_string(f) if pd.notna(f) else ""
        )
        network_formulas = set(net["formula_normalized"])

        # Match: check if each annotated formula exists in network
        matched = []
        unmatched = []
        for ann in ann_list:
            ann_formula = ann["formula"]
            if ann_formula in network_formulas:
                # Find the best matching network record
                net_match = net[net["formula_normalized"] == ann_formula]
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

        hit_rate = len(matched) / len(ann_list) * 100 if ann_list else 0
        intensity_matched = sum(a["intensity"] for a in matched)
        intensity_total = sum(a["intensity"] for a in ann_list)
        intensity_coverage = intensity_matched / intensity_total * 100 if intensity_total else 0

        results[key] = {
            "material": material,
            "polarity": polarity,
            "compound_id": compound_id,
            "total_annotations": len(ann_list),
            "matched": len(matched),
            "unmatched": len(unmatched),
            "hit_rate_pct": round(hit_rate, 1),
            "intensity_coverage_pct": round(intensity_coverage, 1),
            "matched_list": matched,
            "unmatched_list": unmatched,
            "network_size": len(net),
            "network_unique_formulas": len(network_formulas),
        }

        print(f"  {key:20s}: {len(matched):3d}/{len(ann_list):3d} matched "
              f"({hit_rate:5.1f}%)  intensity_cov={intensity_coverage:5.1f}%  "
              f"network_size={len(network_formulas)}")

    return results


# ── Main ────────────────────────────────────────────────────────────────────
def main():
    cfg = load_config("config/default.yaml")

    print("=" * 70)
    print("Extracting 0510 manual annotations...")
    annotations = extract_0510_annotations()

    print(f"\n{'=' * 70}")
    print("Loading algorithm-generated networks...")
    networks = load_all_networks()
    print(f"  Total network records: {len(networks)}")
    print(f"  Compounds in network: {networks['source_compound_id'].nunique()}")

    print(f"\n{'=' * 70}")
    print("Matching annotations against networks...")
    results = match_annotations(annotations, networks)

    # ── Summary table ──
    print(f"\n{'=' * 70}")
    print("SUMMARY: 0510 Manual Annotation vs Algorithm Network Match")
    print(f"{'=' * 70}")
    print(f"{'Material':8s} {'Pol':4s} {'Annot':6s} {'Match':6s} {'Hit%':7s} {'IntCov%':8s} {'NetSize':8s}")
    print("-" * 55)

    total_ann = 0
    total_match = 0
    total_intensity = 0
    total_intensity_matched = 0

    for key in sorted(results.keys()):
        r = results[key]
        total_ann += r["total_annotations"]
        total_match += r["matched"]
        total_intensity += sum(a["intensity"] for a in r["matched_list"] + r["unmatched_list"])
        total_intensity_matched += sum(a["intensity"] for a in r["matched_list"])
        print(f"{r['material']:8s} {r['polarity']:4s} "
              f"{r['total_annotations']:5d}  {r['matched']:5d}  "
              f"{r['hit_rate_pct']:5.1f}%  {r['intensity_coverage_pct']:6.1f}%  "
              f"{r['network_unique_formulas']:5d}")

    print("-" * 55)
    overall_hit = total_match / total_ann * 100 if total_ann else 0
    overall_int = total_intensity_matched / total_intensity * 100 if total_intensity else 0
    print(f"{'TOTAL':8s} {'':4s} {total_ann:5d}  {total_match:5d}  "
          f"{overall_hit:5.1f}%  {overall_int:6.1f}%")

    # Save detailed results
    output = {k: {kk: vv for kk, vv in v.items()
                  if kk not in ("matched_list", "unmatched_list")}
              for k, v in results.items()}
    # Add unmatched details
    for k, v in results.items():
        output[k]["unmatched_formulas"] = [
            {"formula": a["formula"], "raw": a["raw_formula"],
             "mz": a["mz"], "intensity": a["intensity"]}
            for a in v["unmatched_list"]
        ]

    with open("outputs/summary/0510_verification.json", "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nDetailed results saved to outputs/summary/0510_verification.json")

    # Show unmatched examples for each material
    print(f"\n{'=' * 70}")
    print("UNMATCHED ANNOTATIONS (top 5 by intensity per material)")
    print(f"{'=' * 70}")
    for key in sorted(results.keys()):
        r = results[key]
        if r["unmatched"] == 0:
            continue
        unmatched_sorted = sorted(r["unmatched_list"],
                                  key=lambda x: x["intensity"], reverse=True)
        print(f"\n--- {key} ({r['unmatched']} unmatched) ---")
        for a in unmatched_sorted[:5]:
            print(f"  {a['raw_formula']:20s} → {a['formula']:16s}  "
                  f"mz={a['mz']:10.4f}  intensity={a['intensity']:12.2f}")


if __name__ == "__main__":
    main()
