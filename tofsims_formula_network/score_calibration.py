"""v5.1 evidence-prior ranking — unsupervised scoring signals.

No longer depends on validated_diagnostic alone.  Uses traceability,
rule reliability, material-family profiles, and complexity priors
that work for ALL materials (with or without annotations).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .formula import parse_formula
from .specificity import (
    DIAGNOSTIC_DISPLAY_ORDER,
    annotate_v291,
    compute_cross_material_frequency,
)


# ═══════════════════════════════════════════════════════════════════════════════
# 5.1 Rule reliability prior (unsupervised — works without annotations)
# ═══════════════════════════════════════════════════════════════════════════════

def _rule_reliability(generation_types: str, diagnostic_tag: str) -> float:
    """Return 0-1 reliability score based on how the formula was generated."""
    if not isinstance(generation_types, str):
        return 0.10

    gt = generation_types.lower()

    # Validated (has annotation match) — highest
    if diagnostic_tag == "validated_diagnostic":
        return 1.00
    if diagnostic_tag == "validated_generic":
        return 0.85

    # Has BOTH structural (fragment) AND feature_rule support
    if "fragment" in gt and "feature_rule" in gt:
        return 0.75
    # Has BOTH structural AND recombination
    if "fragment" in gt and "recombination" in gt:
        return 0.65
    # Pure structural (fragment only)
    if "fragment" in gt:
        return 0.45
    # Feature rule only (empirical small fragment)
    if "feature_rule" in gt:
        return 0.35
    # Recombination, h_shift, parent etc.
    if "recombination" in gt:
        return 0.30
    if "parent" in gt and "fragment" not in gt:
        return 0.40

    return 0.10  # fallback


# ═══════════════════════════════════════════════════════════════════════════════
# 5.2 Traceability score — bond-type-aware path quality
# ═══════════════════════════════════════════════════════════════════════════════

def _traceability_score(generation_types: str) -> float:
    """Score 0-1: does this formula have a clear structural derivation path?"""
    if not isinstance(generation_types, str):
        return 0.0
    gt = generation_types.lower()
    if "fragment" in gt:
        return 0.60  # has structural path
    if "feature_rule" in gt:
        return 0.30  # has rule rationale but no structural path
    if "recombination" in gt:
        return 0.25  # speculative
    return 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# 5.3 Material-family profile — per-material element/bond-type priority
# ═══════════════════════════════════════════════════════════════════════════════

# Material → set of "family-signature" elements
MATERIAL_SIGNATURES: dict[str, set[str]] = {
    "PPS": {"S"},
    "PDMS": {"Si"},
    "PI": {"N"},
    "Nomex": {"N"},
    "PEI": {"N", "O"},
    "PET": {"O"},
    "PEN": {"O"},
    "PEEK": {"O"},
    "EVA": {"O"},
    "PTFE": {"F"},
    "PVDF": {"F"},
    "ETFE": {"F"},
    "FEP": {"F"},
    "PFA": {"F"},
    "POMC": {"O"},
    "POMH": {"O"},
    "COC": set(),
}

# Material → high-priority bond types for traceability bonus
MATERIAL_BOND_PRIORITY: dict[str, set[str]] = {
    "PPS": {"C-S"},
    "PDMS": {"Si-O"},
    "PI": {"C-N"},
    "Nomex": {"C-N"},
    "PEI": {"C-O", "C-N"},
    "PET": {"C-O"},
    "PEN": {"C-O"},
    "PEEK": {"C-O"},
    "PTFE": {"C-F"},
    "PVDF": {"C-F"},
    "ETFE": {"C-F"},
    "FEP": {"C-F"},
    "PFA": {"C-F"},
    "POMC": {"C-O"},
    "POMH": {"C-O"},
}


def _material_family_bonus(
    compound_id: str,
    formula: str,
    generation_types: str,
    representative_path: str,
) -> float:
    """Bonus for formulas that match material-family signature elements."""
    sig = MATERIAL_SIGNATURES.get(compound_id, set())
    if not sig:
        return 0.0

    try:
        counts = parse_formula(str(formula))
    except Exception:
        return 0.0

    formula_elems = set(counts.keys())

    # Signature bonus: formula contains material-characteristic element
    sig_match = sig & formula_elems
    if not sig_match:
        return 0.0

    # Base: formula contains signature element
    bonus = 0.04

    # Extra: traceable path + matching bond type
    if "fragment" in str(generation_types).lower():
        path_str = str(representative_path).lower()
        bond_priority = MATERIAL_BOND_PRIORITY.get(compound_id, set())
        for bp in bond_priority:
            if bp.lower().replace("-", " ") in path_str or bp.lower() in path_str:
                bonus += 0.04
                break

    return min(bonus, 0.10)


# ═══════════════════════════════════════════════════════════════════════════════
# 5.4 Complexity / oversize penalty
# ═══════════════════════════════════════════════════════════════════════════════

def _complexity_penalty(
    formula: str,
    exact_mass: float,
    generation_types: str,
    diagnostic_tag: str,
) -> float:
    """Penalize overly complex or large unvalidated formulas."""
    penalty = 0.0

    # Already validated — no penalty
    if diagnostic_tag in ("validated_diagnostic", "validated_generic"):
        return 0.0

    try:
        counts = parse_formula(str(formula))
    except Exception:
        return 0.0

    # Large mass + no validation
    mass = float(exact_mass) if exact_mass else 0
    if mass > 300:
        penalty += 0.06
    elif mass > 200:
        penalty += 0.03

    # Many elements + unvalidated
    heavy_elems = {e for e in counts if e != "H"}
    if len(heavy_elems) > 4:
        penalty += 0.04

    # High carbon count but no structural path
    c_count = counts.get("C", 0)
    if c_count > 15 and "fragment" not in str(generation_types).lower():
        penalty += 0.04

    return min(penalty, 0.12)


# ═══════════════════════════════════════════════════════════════════════════════
# 5.5 Combined scoring
# ═══════════════════════════════════════════════════════════════════════════════

# Weights for each component
W_TRACE = 0.15
W_RULE = 0.20
W_FAMILY = 0.10


def compute_v51_score(row: pd.Series) -> float:
    """Compute v5.1 evidence-prior score for one formula_summary row."""
    base = float(row.get("formula_score", 0))
    gen_types = str(row.get("generation_types", ""))
    tag = str(row.get("diagnostic_tag", "structural_candidate_only"))
    cid = str(row.get("compound_id", ""))
    formula = str(row.get("formula", ""))
    path = str(row.get("representative_path", ""))
    mass = float(row.get("exact_mass", 0))

    # Components
    trace = _traceability_score(gen_types)
    rule = _rule_reliability(gen_types, tag)
    family = _material_family_bonus(cid, formula, gen_types, path)
    complex_pen = _complexity_penalty(formula, mass, gen_types, tag)

    # Generic HC penalty
    if tag == "generic_hydrocarbon_background":
        rule *= 0.5  # halve reliability for generic HC

    # Structural-only penalty (strong)
    if tag == "structural_candidate_only":
        rule *= 0.7

    # Large network: slightly compress base
    # (handled by caller through total_mat check)

    score = (
        base * 0.60
        + trace * W_TRACE
        + rule * W_RULE
        + family * W_FAMILY
        - complex_pen
    )

    return round(max(0.0, min(1.0, score)), 4)


# ═══════════════════════════════════════════════════════════════════════════════
# Main pipeline
# ═══════════════════════════════════════════════════════════════════════════════

def calibrate_scores_v51(
    formula_summaries: pd.DataFrame,
    specificity_csv: str | Path = "outputs/summary/formula_summary_v292.csv",
    output_dir: str | Path = "outputs/summary",
) -> pd.DataFrame:
    """Apply v5.1 evidence-prior scoring to formula_summary."""

    # Load or compute diagnostic tags
    try:
        spec = pd.read_csv(specificity_csv)
    except FileNotFoundError:
        freq = compute_cross_material_frequency()
        spec = annotate_v291(formula_summaries, freq)

    # Build tag lookup
    tag_lookup: dict[tuple[str, str, str], str] = {}
    if "diagnostic_tag" in spec.columns:
        for _, row in spec.iterrows():
            key = (str(row["compound_id"]), str(row["formula"]), str(row["ion_mode"]))
            tag_lookup[key] = str(row["diagnostic_tag"])

    out = formula_summaries.copy()

    # Add diagnostic tags if not present
    if "diagnostic_tag" not in out.columns:
        tags = []
        for _, row in out.iterrows():
            key = (str(row["compound_id"]), str(row["formula"]), str(row["ion_mode"]))
            tags.append(tag_lookup.get(key, "structural_candidate_only"))
        out["diagnostic_tag"] = tags

    # Compute v5.1 scores
    new_scores = []
    for _, row in out.iterrows():
        new_scores.append(compute_v51_score(row))

    out["formula_score_original"] = out.get("formula_score", 0)
    out["formula_score"] = new_scores

    return out


def apply_and_save(
    formula_summaries: pd.DataFrame,
    output_dir: str | Path = "outputs/summary",
    network_dir: str | Path = "outputs/networks_v2",
) -> pd.DataFrame:
    """Calibrate, re-rank by diagnostic priority, and save per material."""
    output_dir = Path(output_dir)
    network_dir = Path(network_dir)

    calibrated = calibrate_scores_v51(formula_summaries)

    # Per-material priority re-rank
    tag_rank = {t: i for i, t in enumerate(DIAGNOSTIC_DISPLAY_ORDER)}

    for cid in calibrated["compound_id"].unique():
        mat = calibrated[calibrated["compound_id"] == cid].copy()
        if "diagnostic_tag" in mat.columns:
            mat["_tag_rank"] = mat["diagnostic_tag"].map(tag_rank).fillna(99)
            mat = mat.sort_values(["_tag_rank", "formula_score"], ascending=[True, False])
            mat = mat.drop(columns=["_tag_rank"])
        else:
            mat = mat.sort_values("formula_score", ascending=False)

        safe = str(cid).replace("/", "_")
        mat.to_csv(network_dir / ("%s_formula_summary.csv" % safe), index=False, encoding="utf-8-sig")

    calibrated.to_csv(output_dir / "formula_summary_v51.csv", index=False)
    return calibrated
