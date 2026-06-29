from __future__ import annotations

from dataclasses import dataclass

from .formula import add_formula, exact_mass, parse_formula


@dataclass(frozen=True)
class RulePackCandidate:
    counts: dict[str, int]
    ion_mode: str
    charge: int
    generation_type: str
    path: list[str]


def _has_element(counts: dict[str, int], element: str) -> bool:
    return counts.get(element, 0) > 0


def _compound_id(row: dict) -> str:
    return str(row.get("compound_id", "")).strip()


def _enabled_for_compound(row: dict, pack_cfg: dict) -> bool:
    compound_ids = pack_cfg.get("compound_ids")
    if compound_ids:
        return _compound_id(row) in {str(cid) for cid in compound_ids}
    return True


def _with_ion_modes(counts: dict[str, int], generation_type: str, path: list[str]) -> list[RulePackCandidate]:
    return [
        RulePackCandidate(dict(counts), "positive", 1, generation_type, path + ["positive ion formula"]),
        RulePackCandidate(dict(counts), "negative", -1, generation_type, path + ["negative ion formula"]),
    ]


def generate_carbon_cluster_formulas(row: dict, parent_counts: dict[str, int], config: dict) -> list[RulePackCandidate]:
    pack_cfg = config.get("rule_packs", {}).get("carbon_cluster", {})
    if not pack_cfg.get("enabled", False):
        return []
    if not _enabled_for_compound(row, pack_cfg) or not _has_element(parent_counts, "C"):
        return []

    min_c = int(pack_cfg.get("min_c", 3))
    max_c = int(pack_cfg.get("max_c", min_c))
    max_h_extra = int(pack_cfg.get("max_h_extra", 2))
    max_o = int(pack_cfg.get("max_o", 0)) if _has_element(parent_counts, "O") else 0
    max_mass = float(pack_cfg.get("max_mass", 220.0))

    records: list[RulePackCandidate] = []
    seen: set[tuple[tuple[str, int], ...]] = set()
    for c_count in range(min_c, max_c + 1):
        max_h = 2 * c_count + max_h_extra
        for o_count in range(0, max_o + 1):
            for h_count in range(0, max_h + 1):
                counts = {"C": c_count}
                if h_count:
                    counts["H"] = h_count
                if o_count:
                    counts["O"] = o_count
                if exact_mass(counts) > max_mass:
                    continue
                key = tuple(sorted(counts.items()))
                if key in seen:
                    continue
                seen.add(key)
                label = f"carbon cluster C{c_count} H0-{max_h}"
                if o_count:
                    label += f" O{o_count}"
                records.extend(_with_ion_modes(counts, "carbon_cluster", [label]))
    return records


def generate_siloxane_fragments(row: dict, parent_counts: dict[str, int], config: dict) -> list[RulePackCandidate]:
    pack_cfg = config.get("rule_packs", {}).get("siloxane_fragment", {})
    if not pack_cfg.get("enabled", False):
        return []
    if not _enabled_for_compound(row, pack_cfg) or not _has_element(parent_counts, "Si"):
        return []

    max_si = int(pack_cfg.get("max_si", 6))
    max_mass = float(pack_cfg.get("max_mass", 360.0))
    records: list[RulePackCandidate] = []
    seen: set[tuple[tuple[str, int], ...]] = set()

    for si_count in range(1, max_si + 1):
        max_c = 2 * si_count + 2
        min_o = max(0, si_count - 2)
        max_o = si_count + 2
        for c_count in range(0, max_c + 1):
            max_h = min(3 * c_count + 2 * si_count + 2, 30)
            for o_count in range(min_o, max_o + 1):
                for h_count in range(0, max_h + 1):
                    counts = {"Si": si_count}
                    if c_count:
                        counts["C"] = c_count
                    if h_count:
                        counts["H"] = h_count
                    if o_count:
                        counts["O"] = o_count
                    if exact_mass(counts) > max_mass:
                        continue
                    key = tuple(sorted(counts.items()))
                    if key in seen:
                        continue
                    seen.add(key)
                    records.extend(
                        _with_ion_modes(
                            counts,
                            "siloxane_fragment",
                            [f"siloxane fragment Si{si_count} C0-{max_c} O{min_o}-{max_o}"],
                        )
                    )
    return records


def generate_external_adduct_variants(
    row: dict,
    base_counts: list[dict[str, int]],
    config: dict,
) -> list[RulePackCandidate]:
    pack_cfg = config.get("rule_packs", {}).get("external_adduct", {})
    if not pack_cfg.get("enabled", False):
        return []
    if not _enabled_for_compound(row, pack_cfg):
        return []

    adducts = [str(adduct) for adduct in pack_cfg.get("adducts", [])]
    max_base_mass = float(pack_cfg.get("max_base_mass", 500.0))
    records: list[RulePackCandidate] = []
    seen: set[tuple[tuple[str, int], ...]] = set()

    for counts in base_counts:
        if exact_mass(counts) > max_base_mass:
            continue
        for adduct in adducts:
            out_counts = add_formula(counts, parse_formula(adduct))
            key = tuple(sorted(out_counts.items()))
            if key in seen:
                continue
            seen.add(key)
            records.append(
                RulePackCandidate(
                    out_counts,
                    "positive",
                    1,
                    "external_adduct",
                    ["external adduct", adduct],
                )
            )
    return records


def generate_rule_pack_candidates(
    row: dict,
    parent_counts: dict[str, int],
    base_counts: list[dict[str, int]],
    config: dict,
) -> list[RulePackCandidate]:
    cfg = config.get("rule_packs", {})
    if not cfg.get("enabled", False):
        return []
    records: list[RulePackCandidate] = []
    records.extend(generate_carbon_cluster_formulas(row, parent_counts, config))
    records.extend(generate_siloxane_fragments(row, parent_counts, config))
    records.extend(generate_external_adduct_variants(row, base_counts, config))
    return records
