from __future__ import annotations


def clip(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def score_record(record, config: dict) -> float:
    scoring = config["scoring"]
    generation_scores = scoring.get("generation_type_scores", {})
    if record.generation_type in generation_scores:
        score = generation_scores[record.generation_type]
    else:
        score = scoring["base_parent"] if record.generation_type == "parent" else scoring["base_fragment"]
    score -= scoring["penalty_per_broken_bond"] * record.broken_bonds
    score -= scoring["penalty_per_h_shift"] * abs(record.h_shift)
    score -= scoring["penalty_neutral_loss"] * len(record.neutral_losses)
    if record.adduct not in [None, "H", "-H"]:
        score -= scoring["penalty_non_h_adduct"]
    if record.generation_type == "dimer":
        score -= scoring["penalty_dimer"]
    return clip(score, scoring["min_score"], scoring["max_score"])
