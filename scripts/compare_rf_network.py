from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tofsims_formula_network.formula import normalize_formula_string


SUBSCRIPT_DIGITS = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
SUPERSCRIPT_DIGITS = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")
CHARGE_RE = re.compile(r"[\+\-⁺⁻]+$")


def write_table(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False, encoding="utf-8-sig")


def write_excel(df: pd.DataFrame, path: Path, sheet_name: str = "Sheet1") -> None:
    if importlib.util.find_spec("openpyxl") is None:
        return
    try:
        df.to_excel(path, index=False, sheet_name=sheet_name)
    except Exception as exc:
        print(f"skipped Excel export {path}: {exc}")


def write_excel_tsv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False, sep="\t", encoding="utf-16")


def clean_rf_formula(raw: str) -> str:
    formula = str(raw or "").strip()
    if not formula:
        return ""
    formula = formula.translate(SUBSCRIPT_DIGITS)
    formula = formula.translate(SUPERSCRIPT_DIGITS)
    formula = formula.replace(" ", "")
    formula = CHARGE_RE.sub("", formula)
    formula = re.sub(r"(?<![A-Za-z0-9])\d+(?=[A-Z])", "", formula)
    return formula


def safe_normalize_rf_formula(raw: str) -> str | None:
    cleaned = clean_rf_formula(raw)
    if not cleaned:
        return None
    try:
        return normalize_formula_string(cleaned)
    except Exception:
        return None


def polarity_to_ion_mode(pol: str) -> str:
    return {"+": "positive", "-": "negative"}.get(str(pol), "")


def load_rf_peaks(rf_root: Path) -> pd.DataFrame:
    rows: list[dict] = []
    for path in sorted(rf_root.glob("*/第1轮/盲分析.json")):
        material = path.parts[-3]
        payload = json.loads(path.read_text(encoding="utf-8"))
        for peak in payload.get("peaks", []):
            final = peak.get("final_proposal") or {}
            raw_formula = final.get("f", "")
            cleaned_formula = clean_rf_formula(raw_formula)
            normalized_formula = safe_normalize_rf_formula(raw_formula)
            rows.append(
                {
                    "material": material,
                    "peak_index": peak.get("i"),
                    "mz": peak.get("mz"),
                    "intensity": peak.get("intensity"),
                    "polarity": peak.get("pol"),
                    "ion_mode": polarity_to_ion_mode(peak.get("pol")),
                    "rank": peak.get("rank"),
                    "rf_formula_raw": raw_formula,
                    "rf_formula_clean": cleaned_formula,
                    "normalized_formula": normalized_formula,
                    "rf_exact_mz": final.get("mz"),
                    "rf_ppm": final.get("ppm"),
                    "rf_score": final.get("s"),
                    "rf_source": final.get("source"),
                }
            )
    return pd.DataFrame(rows)


def load_networks(network_dir: Path) -> pd.DataFrame:
    frames = []
    for path in sorted(network_dir.glob("*.csv")):
        df = pd.read_csv(path)
        df["network_file"] = path.name
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out["normalized_formula"] = out["formula"].map(lambda value: normalize_formula_string(str(value)))
    return out


def load_substance_candidates(rf_root: Path) -> pd.DataFrame:
    rows: list[dict] = []
    for path in sorted(rf_root.glob("*/第1轮/substance_candidates.json")):
        material = path.parts[-3]
        payload = json.loads(path.read_text(encoding="utf-8"))
        for index, candidate in enumerate(payload.get("candidates", []), start=1):
            rows.append(
                {
                    "material": material,
                    "candidate_rank": index,
                    "label": candidate.get("label"),
                    "match_score": candidate.get("match_score"),
                    "matched_count": len(candidate.get("matched") or []),
                    "missing_typical_count": len(candidate.get("missing_typicals") or []),
                    "matched_formulas": "; ".join(
                        item.get("matched_slim_formula", "") for item in (candidate.get("matched") or [])
                    ),
                }
            )
    return pd.DataFrame(rows)


def aggregate_rf_formulas(peaks: pd.DataFrame) -> pd.DataFrame:
    valid = peaks[peaks["normalized_formula"].notna()].copy()
    if valid.empty:
        return pd.DataFrame()

    def top_raw(values: pd.Series) -> str:
        counter = Counter(str(v) for v in values if str(v))
        return counter.most_common(1)[0][0] if counter else ""

    grouped = (
        valid.groupby(["material", "normalized_formula", "ion_mode", "polarity"], dropna=False)
        .agg(
            rf_formula_raw=("rf_formula_raw", top_raw),
            peak_count=("peak_index", "count"),
            best_rf_score=("rf_score", "max"),
            best_rank=("rank", "min"),
            max_intensity=("intensity", "max"),
            total_intensity=("intensity", "sum"),
            mz_min=("mz", "min"),
            mz_max=("mz", "max"),
            median_abs_ppm=("rf_ppm", lambda values: float(pd.Series(values).dropna().abs().median()) if len(pd.Series(values).dropna()) else math.nan),
        )
        .reset_index()
    )

    totals = valid.groupby("material")["intensity"].sum().rename("material_total_intensity")
    grouped = grouped.merge(totals, on="material", how="left")
    grouped["relative_intensity"] = grouped["total_intensity"] / grouped["material_total_intensity"]
    return grouped


def build_network_index(networks: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if networks.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    same_cols = ["source_compound_id", "normalized_formula", "ion_mode"]
    same_index = (
        networks.groupby(same_cols, dropna=False)
        .agg(
            network_best_score=("score", "max"),
            generation_types=("generation_type", lambda values: "; ".join(sorted(set(map(str, values))))),
            paths=("path", lambda values: " | ".join(list(dict.fromkeys(map(str, values)))[:3])),
            exact_mass=("exact_mass", "median"),
        )
        .reset_index()
        .rename(columns={"source_compound_id": "material"})
    )

    all_index = (
        networks.groupby(["normalized_formula", "ion_mode"], dropna=False)
        .agg(
            all_network_compound_count=("source_compound_id", lambda values: len(set(map(str, values)))),
            all_network_compounds=("source_compound_id", lambda values: "; ".join(sorted(set(map(str, values)))[:12])),
        )
        .reset_index()
    )
    formula_index = (
        networks.groupby(["source_compound_id", "normalized_formula"], dropna=False)
        .agg(
            network_formula_modes=("ion_mode", lambda values: "; ".join(sorted(set(map(str, values))))),
            network_formula_best_score=("score", "max"),
        )
        .reset_index()
        .rename(columns={"source_compound_id": "material"})
    )
    return same_index, all_index, formula_index


def compare_rf_to_network(rf_formulas: pd.DataFrame, networks: pd.DataFrame) -> pd.DataFrame:
    same_index, all_index, formula_index = build_network_index(networks)
    compared = rf_formulas.merge(same_index, on=["material", "normalized_formula", "ion_mode"], how="left")
    compared = compared.merge(formula_index, on=["material", "normalized_formula"], how="left")
    compared = compared.merge(all_index, on=["normalized_formula", "ion_mode"], how="left")
    compared["same_material_mode_match"] = compared["network_best_score"].notna()
    compared["same_material_formula_match"] = compared["network_formula_best_score"].notna()
    compared["all_network_compound_count"] = compared["all_network_compound_count"].fillna(0).astype(int)
    compared["is_generic_formula"] = compared["all_network_compound_count"] >= 8
    compared["screening_tier"] = compared.apply(assign_screening_tier, axis=1)
    return compared.sort_values(
        ["material", "screening_tier", "same_material_mode_match", "best_rf_score", "relative_intensity"],
        ascending=[True, True, False, False, False],
    )


def check_top10_rf_peaks(peaks: pd.DataFrame, networks: pd.DataFrame) -> pd.DataFrame:
    same_index, all_index, formula_index = build_network_index(networks)
    formula_all_index = (
        networks.groupby("normalized_formula", dropna=False)
        .agg(
            formula_all_network_compound_count=("source_compound_id", lambda values: len(set(map(str, values)))),
            formula_all_network_compounds=("source_compound_id", lambda values: "; ".join(sorted(set(map(str, values)))[:12])),
        )
        .reset_index()
    )
    rows = []
    for material, group in peaks.sort_values(["material", "rank", "intensity"], ascending=[True, True, False]).groupby("material"):
        top = group.head(10).copy()
        top["top_order"] = range(1, len(top) + 1)
        rows.append(top)
    if not rows:
        return pd.DataFrame()

    top_peaks = pd.concat(rows, ignore_index=True)
    checked = top_peaks.merge(
        same_index,
        on=["material", "normalized_formula", "ion_mode"],
        how="left",
    )
    checked = checked.merge(
        formula_index,
        on=["material", "normalized_formula"],
        how="left",
    )
    checked = checked.merge(
        all_index,
        on=["normalized_formula", "ion_mode"],
        how="left",
    )
    checked = checked.merge(
        formula_all_index,
        on="normalized_formula",
        how="left",
    )
    checked["same_material_mode_match"] = checked["network_best_score"].notna()
    checked["same_material_formula_match"] = checked["network_formula_best_score"].notna()
    checked["all_network_compound_count"] = checked["all_network_compound_count"].fillna(0).astype(int)
    checked["formula_all_network_compound_count"] = checked["formula_all_network_compound_count"].fillna(0).astype(int)
    checked["plain_presence_note"] = checked.apply(plain_presence_note, axis=1)
    show_cols = [
        "material",
        "top_order",
        "peak_index",
        "rank",
        "mz",
        "intensity",
        "polarity",
        "rf_formula_raw",
        "normalized_formula",
        "rf_score",
        "rf_ppm",
        "same_material_mode_match",
        "same_material_formula_match",
        "all_network_compound_count",
        "all_network_compounds",
        "formula_all_network_compound_count",
        "formula_all_network_compounds",
        "plain_presence_note",
        "generation_types",
        "network_formula_modes",
    ]
    return checked[[col for col in show_cols if col in checked.columns]]


def plain_presence_note(row: pd.Series) -> str:
    if pd.isna(row.get("normalized_formula")):
        return "RF公式无法解析"
    if int(row.get("all_network_compound_count") or 0) > 0:
        return "公式+极性在network中出现"
    if int(row.get("formula_all_network_compound_count") or 0) > 0:
        return "公式在network中出现但极性未对应"
    return "network未出现"


def screen_rf_peaks_with_network(peaks: pd.DataFrame, networks: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    same_index, all_index, formula_index = build_network_index(networks)
    formula_all_index = (
        networks.groupby("normalized_formula", dropna=False)
        .agg(
            formula_all_network_compound_count=("source_compound_id", lambda values: len(set(map(str, values)))),
            formula_all_network_compounds=("source_compound_id", lambda values: "; ".join(sorted(set(map(str, values)))[:12])),
        )
        .reset_index()
    )
    network_materials = set(networks["source_compound_id"].astype(str)) if not networks.empty else set()

    valid = peaks[peaks["normalized_formula"].notna()].copy()
    totals = valid.groupby("material")["intensity"].sum().rename("material_total_intensity")
    valid = valid.merge(totals, on="material", how="left")
    valid["relative_intensity"] = valid["intensity"] / valid["material_total_intensity"]

    checked = valid.merge(same_index, on=["material", "normalized_formula", "ion_mode"], how="left")
    checked = checked.merge(formula_index, on=["material", "normalized_formula"], how="left")
    checked = checked.merge(all_index, on=["normalized_formula", "ion_mode"], how="left")
    checked = checked.merge(formula_all_index, on="normalized_formula", how="left")
    checked["has_network"] = checked["material"].isin(network_materials)
    checked["same_material_mode_match"] = checked["network_best_score"].notna()
    checked["same_material_formula_match"] = checked["network_formula_best_score"].notna()
    checked["all_network_compound_count"] = checked["all_network_compound_count"].fillna(0).astype(int)
    checked["formula_all_network_compound_count"] = checked["formula_all_network_compound_count"].fillna(0).astype(int)

    screened = checked[checked["has_network"] & checked["same_material_formula_match"]].copy()
    if screened.empty:
        return screened, pd.DataFrame()

    screened["support_class"] = screened.apply(assign_peak_support_class, axis=1)
    screened["network_screen_score"] = screened.apply(score_screened_peak, axis=1)
    screened["interpretation_cn"] = screened.apply(interpret_screened_peak, axis=1)
    screened["specificity_compound_count"] = screened.apply(
        lambda row: int(row["all_network_compound_count"])
        if row["same_material_mode_match"] and int(row["all_network_compound_count"]) > 0
        else int(row["formula_all_network_compound_count"]),
        axis=1,
    )

    screened = screened.sort_values(
        ["material", "network_screen_score", "same_material_mode_match", "rf_score", "relative_intensity", "rank"],
        ascending=[True, False, False, False, False, True],
    )
    top10 = screened.groupby("material", group_keys=False).head(10).copy()
    top10["network_screen_rank"] = top10.groupby("material").cumcount() + 1

    summary_rows = []
    for material, group in checked.groupby("material"):
        supported = screened[screened["material"] == material]
        top = top10[top10["material"] == material]
        summary_rows.append(
            {
                "material": material,
                "has_network": material in network_materials,
                "rf_peak_rows": len(group),
                "network_supported_peak_rows": len(supported),
                "strict_mode_supported_peak_rows": int(supported["same_material_mode_match"].sum()) if not supported.empty else 0,
                "screened_top10_rows": len(top),
                "top10_strict_mode_rows": int(top["same_material_mode_match"].sum()) if not top.empty else 0,
                "top10_formula_only_rows": int((~top["same_material_mode_match"]).sum()) if not top.empty else 0,
            }
        )

    show_cols = [
        "material",
        "network_screen_rank",
        "network_screen_score",
        "support_class",
        "interpretation_cn",
        "peak_index",
        "rank",
        "mz",
        "intensity",
        "relative_intensity",
        "polarity",
        "rf_formula_raw",
        "normalized_formula",
        "rf_score",
        "rf_ppm",
        "same_material_mode_match",
        "same_material_formula_match",
        "generation_types",
        "network_formula_modes",
        "specificity_compound_count",
        "all_network_compounds",
        "formula_all_network_compounds",
    ]
    return top10[[col for col in show_cols if col in top10.columns]], pd.DataFrame(summary_rows)


def assign_peak_support_class(row: pd.Series) -> str:
    if row.get("same_material_mode_match", False):
        count = int(row.get("all_network_compound_count") or 0)
        return "strict_specific" if count and count <= 4 else "strict_common"
    return "formula_only_mode_gap"


def score_screened_peak(row: pd.Series) -> float:
    strict = bool(row.get("same_material_mode_match", False))
    mode_count = int(row.get("all_network_compound_count") or 0)
    formula_count = int(row.get("formula_all_network_compound_count") or 0)
    specificity_count = mode_count if strict and mode_count else formula_count
    specificity_bonus = max(0.0, (8 - min(max(specificity_count, 1), 8)) / 7) * 20
    support_bonus = 55 if strict else 35
    rf_bonus = min(max(float(row.get("rf_score") or 0), 0), 100) / 100 * 15
    rank = max(float(row.get("rank") or 9999), 1)
    rank_bonus = max(0.0, 1 - min(rank, 500) / 500) * 10
    rel = max(float(row.get("relative_intensity") or 0), 0)
    intensity_bonus = min(math.log10(rel * 10000 + 1) / 4, 1) * 10
    return round(support_bonus + specificity_bonus + rf_bonus + rank_bonus + intensity_bonus, 3)


def interpret_screened_peak(row: pd.Series) -> str:
    if row.get("same_material_mode_match", False):
        count = int(row.get("all_network_compound_count") or 0)
        if count and count <= 4:
            return "同材料同极性命中，且跨材料较少，优先作为材料相关峰。"
        return "同材料同极性命中，但跨材料较常见，作为辅助证据。"
    return "同材料存在该分子式，但当前极性未覆盖，提示 ion rule 或极性分配缺口。"


def assign_screening_tier(row: pd.Series) -> str:
    if not row.get("same_material_mode_match", False):
        return "C_network未覆盖"
    score = float(row.get("best_rf_score") or 0)
    rel = float(row.get("relative_intensity") or 0)
    compound_count = int(row.get("all_network_compound_count") or 0)
    if score >= 70 and (rel >= 0.005 or int(row.get("best_rank") or 999999) <= 100) and compound_count <= 4:
        return "A_高置信特征"
    if score >= 50 and compound_count <= 7:
        return "B_可用支持"
    return "D_泛化或弱证据"


def summarize_by_material(compared: pd.DataFrame, networks: pd.DataFrame) -> pd.DataFrame:
    network_materials = set(networks["source_compound_id"].astype(str)) if not networks.empty else set()
    rows = []
    for material, group in compared.groupby("material"):
        has_network = material in network_materials
        total = len(group)
        matched = int(group["same_material_mode_match"].sum())
        formula_matched = int(group["same_material_formula_match"].sum())
        high = int((group["screening_tier"] == "A_高置信特征").sum())
        support = int((group["screening_tier"] == "B_可用支持").sum())
        generic = int((group["screening_tier"] == "D_泛化或弱证据").sum())
        uncovered = int((group["screening_tier"] == "C_network未覆盖").sum())
        rows.append(
            {
                "material": material,
                "has_network": has_network,
                "rf_unique_formula_mode": total,
                "same_material_mode_matches": matched,
                "same_material_formula_matches": formula_matched,
                "match_rate": matched / total if total else 0,
                "formula_match_rate": formula_matched / total if total else 0,
                "tier_A_high_confidence": high,
                "tier_B_support": support,
                "tier_D_generic_or_weak": generic,
                "tier_C_network_uncovered": uncovered,
                "top_generation_types": "; ".join(group[group["same_material_mode_match"]]["generation_types"].dropna().astype(str).head(5)),
            }
        )
    return pd.DataFrame(rows).sort_values(["has_network", "match_rate", "material"], ascending=[False, False, True])


def markdown_table(df: pd.DataFrame, floatfmt: str = ".3f") -> str:
    if df.empty:
        return "无数据。"
    clean = df.copy()
    headers = [str(col) for col in clean.columns]
    rows = []
    for _, row in clean.iterrows():
        rendered = []
        for value in row.tolist():
            if pd.isna(value):
                rendered.append("")
            elif isinstance(value, float):
                rendered.append(format(value, floatfmt))
            else:
                rendered.append(str(value).replace("\n", " "))
        rows.append(rendered)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def write_report(
    report_path: Path,
    compared: pd.DataFrame,
    summary: pd.DataFrame,
    candidates: pd.DataFrame,
    invalid_peaks: pd.DataFrame,
    top10_peaks: pd.DataFrame,
    screened_top10_peaks: pd.DataFrame,
    screened_top10_summary: pd.DataFrame,
) -> None:
    matched_materials = summary[summary["has_network"]]
    missing_materials = summary[~summary["has_network"]]["material"].tolist()
    total_rf = int(summary["rf_unique_formula_mode"].sum())
    total_match = int(summary["same_material_mode_matches"].sum())
    total_formula_match = int(summary["same_material_formula_matches"].sum())
    total_high = int(summary["tier_A_high_confidence"].sum())
    total_support = int(summary["tier_B_support"].sum())
    networked_summary = summary[summary["has_network"]]
    networked_rf = int(networked_summary["rf_unique_formula_mode"].sum())
    networked_match = int(networked_summary["same_material_mode_matches"].sum())
    networked_formula_match = int(networked_summary["same_material_formula_matches"].sum())

    lines = [
        "# AI生成标注输出（RF_output）与 formula network 对比筛选报告",
        "",
        "生成日期：2026-06-16",
        "",
        "> 术语说明：`RF_output` 是历史文件夹命名，本文将其理解为实验室提供的 AI 生成标注输出，不代表 Random Forest。",
        "",
        "## 对比口径",
        "",
        "- AI生成输出侧使用每个材料 `第1轮/盲分析.json` 中的 `final_proposal`，按“材料 + 归一化分子式 + 极性”聚合。",
        "- network 侧使用 `outputs/networks/*.csv`，严格匹配同一材料、同一分子式、同一离子模式。",
        "- 额外统计每个公式在全部 network 材料中出现的数量，用来识别 `C`、`CH`、`C2H3` 等通用碎片。",
        "- AI生成公式中的 Unicode 下标、正负电荷和同位素质量数会先清洗，例如 `C₂F₅⁺` 归一为 `C2F5`。",
        "",
        "## network 筛选 AI生成前十峰算法",
        "",
        "给实验室人员查看的筛选版前十峰不是简单 AI生成原始 rank，也不是只看 network 是否命中，而是使用以下综合分数：",
        "",
        "- 结构支持分：同材料同极性命中给最高权重；同材料只命中分子式但极性未覆盖给中等权重。",
        "- 特异性分：同一公式/极性在越少材料 network 中出现，分数越高；跨材料普遍出现的通用碎片会降权。",
        "- AI生成证据分：保留 AI生成输出中的 `s` 分数、原始 `rank` 和相对强度作为辅助排序。",
        "- 输出时只保留同材料 network 至少能解释分子式的峰；PAI、PBI、PCTFE 当前没有 network，因此不会产生筛选前十峰。",
        "",
        "综合分数可以理解为：`network 结构支持 + 材料特异性 + AI生成置信度 + 原始rank + 峰强`。",
        "",
        "### 打分项解释",
        "",
        "- 结构支持分：同材料、同分子式、同极性命中 network 时权重最高；如果只命中同材料分子式但极性未覆盖，则保留但降权。",
        "- 材料特异性分：看该公式在多少种材料的 network 中出现。出现材料越少，越像材料特征峰，分数越高；在很多材料中都出现的 `C`、`CH`、`C2H3` 等通用碎片会被降权。严格命中时优先使用 `all_network_compound_count`，极性未命中时使用 `formula_all_network_compound_count`。",
        "- AI生成分数：对应 AI生成/规则流程对该峰公式解释的置信度，反映 ppm、元素合理性、规则奖励、同位素/碎片链等因素。输出表中仍保留历史字段名 `rf_score`。",
        "- AI生成原始 rank：对应该峰在原始谱中的排序重要性。它和峰强相关，但不是同一个信息；rank 表示“是否靠前醒目”，峰强表示“相对贡献有多大”。",
        "- 峰强：使用 `relative_intensity`，即该峰强度占当前材料全部 RF 峰强度的比例。它只作为辅助项，避免低强度但高置信的峰完全压过主峰。",
        "",
        "同时使用 AI生成分数和原始 rank 的原因是：AI生成分数描述“公式解释是否可信”，原始 rank 描述“这个峰在谱图中是否重要”。一个高分但很靠后的峰可能是可信弱峰；一个很靠前但低分的峰可能是背景、污染或公式解释不稳。两者结合后，再由 network 结构支持和材料特异性主导排序。",
        "",
        "## AI生成输出文件说明",
        "",
        "- `盲分析.json`：AI生成/规则流程的峰级完整结果。核心字段是 `peaks`，每条峰包含 `mz`、`intensity`、`pol`、`rank`、候选 `mols`，以及最终采用的 `final_proposal`。本报告的公式级对比主要使用它。",
        "- `LLM工作清单.json`：给 LLM 或人工复核使用的简化峰清单。保留 `mz`、`pol`、`rank`、`intensity`、`final` 和部分 `reasoning`，比 `盲分析.json` 更轻，但信息不如前者完整。",
        "- `substance_candidates.json`：基于目录典型碎片生成的候选物质/碎片类别排名，包含 `candidates`、`matched`、`missing_typicals` 和 `uncovered_formulas`。它适合做提示，不适合直接当纯物质判定。",
        "- `软件标注报告.md`：AI标注软件侧生成的人读报告，主要用于快速查看标注结论和解释，不作为本次程序化匹配的数据源。",
        "",
        "## 总体结论",
        "",
        f"- AI生成输出共得到 {total_rf} 个可解析的“公式-极性”组合，其中 {total_match} 个被同材料同极性 network 覆盖，整体覆盖率 {total_match / total_rf:.1%}；若只看分子式不看极性，同材料覆盖 {total_formula_match} 个。",
        f"- 排除 PAI、PBI、PCTFE 三个未建 network 的材料后，可评价材料共有 {networked_rf} 个 AI生成公式-极性组合，严格覆盖 {networked_match} 个（{networked_match / networked_rf:.1%}），分子式覆盖 {networked_formula_match} 个（{networked_formula_match / networked_rf:.1%}）。",
        f"- 筛选后得到 A 级高置信特征 {total_high} 个，B 级可用支持 {total_support} 个。A/B 两级更适合作为后续纯物质判别或规则回灌的候选。",
        f"- 当前 AI生成输出中有 {len(missing_materials)} 个材料没有对应 network：{', '.join(missing_materials) if missing_materials else '无'}。",
        f"- 有 {len(invalid_peaks)} 条 AI生成峰公式未能被当前 formula parser 解析，主要原因通常是 network 元素表未包含金属/污染元素或公式不是标准 Hill 写法。",
        "",
        "## A/B/C/D 分级定义",
        "",
        "- A_高置信特征：同材料同极性 network 命中，AI生成分数不低于 70，并且相对强度不低于 0.5% 或原始 rank 进入前 100，同时该公式在全部 network 中出现材料数不超过 4。",
        "- B_可用支持：同材料同极性 network 命中，AI生成分数不低于 50，并且该公式在全部 network 中出现材料数不超过 7。它可作为辅助证据，但材料特异性弱于 A 级。",
        "- C_network未覆盖：AI生成输出给出了可解析公式，但同材料同极性 network 没有覆盖。它们是后续规则扩展或背景峰排除的重点检查对象。",
        "- D_泛化或弱证据：同材料同极性 network 有命中，但 AI生成分数、强度/rank 或跨材料特异性不足，不建议单独作为材料判据。",
        "",
        "## 按材料汇总",
        "",
        markdown_table(summary, floatfmt=".3f"),
        "",
        "## 每个材料 AI生成 rank 前十峰的 network 检查",
        "",
        "下表使用 `盲分析.json` 中 `rank` 最靠前的 10 个峰。`same_material_mode_match` 是严格的同材料公式+极性命中，`same_material_formula_match` 只看同材料分子式是否存在于 network。",
        "",
        markdown_table(
            top10_peaks[
                [
                    "material",
                    "top_order",
                    "rank",
                    "mz",
                    "polarity",
                    "rf_formula_raw",
                    "normalized_formula",
                    "rf_score",
                    "same_material_mode_match",
                    "same_material_formula_match",
                    "all_network_compound_count",
                    "all_network_compounds",
                    "formula_all_network_compound_count",
                    "formula_all_network_compounds",
                    "plain_presence_note",
                    "generation_types",
                    "network_formula_modes",
                ]
            ],
            floatfmt=".4f",
        ),
        "",
        "## AI生成原始前十峰的朴素 network 归属",
        "",
        "这一节不引入任何评分机制，只回答：每个材料 AI生成原始 rank 前十峰的公式是否出现在全部 network 中；如果出现，出现在哪些材料中。`all_network_compounds` 使用“公式+极性”口径，`formula_all_network_compounds` 只看公式、不看极性。",
        "",
        markdown_table(
            top10_peaks[
                [
                    "material",
                    "top_order",
                    "rank",
                    "mz",
                    "polarity",
                    "rf_formula_raw",
                    "normalized_formula",
                    "rf_score",
                    "all_network_compound_count",
                    "all_network_compounds",
                    "formula_all_network_compound_count",
                    "formula_all_network_compounds",
                    "plain_presence_note",
                ]
            ],
            floatfmt=".4f",
        ),
        "",
        "## network 筛选后的 RF 前十峰",
        "",
        "这一节是建议给实验室人员优先查看的结果。它已经排除了同材料 network 完全无法解释的 RF 峰，并把严格命中和极性缺口分开标记。",
        "",
        "### 筛选数量汇总",
        "",
        markdown_table(screened_top10_summary, floatfmt=".3f"),
        "",
    ]
    for material in sorted(screened_top10_peaks["material"].unique()) if not screened_top10_peaks.empty else []:
        sub = screened_top10_peaks[screened_top10_peaks["material"] == material]
        show = sub[
            [
                "network_screen_rank",
                "network_screen_score",
                "support_class",
                "rank",
                "mz",
                "polarity",
                "rf_formula_raw",
                "normalized_formula",
                "rf_score",
                "relative_intensity",
                "generation_types",
                "network_formula_modes",
                "specificity_compound_count",
                "interpretation_cn",
            ]
        ]
        lines.extend([f"### {material}", "", markdown_table(show, floatfmt=".4f"), ""])

    lines.extend(
        [
        "## A/B 级筛选公式",
        "",
        ]
    )

    for material in sorted(compared["material"].unique()):
        sub = compared[(compared["material"] == material) & (compared["screening_tier"].isin(["A_高置信特征", "B_可用支持"]))]
        lines.extend([f"### {material}", ""])
        if sub.empty:
            lines.extend(["无 A/B 级公式。", ""])
        else:
            show = sub[
                [
                    "screening_tier",
                    "normalized_formula",
                    "polarity",
                    "best_rf_score",
                    "relative_intensity",
                    "best_rank",
                    "generation_types",
                    "all_network_compound_count",
                ]
            ].head(20)
            lines.extend([markdown_table(show, floatfmt=".4f"), ""])

    lines.extend(
        [
            "## AI生成候选物质排名的提示",
            "",
            "AI生成输出中的 `substance_candidates.json` 是基于目录典型碎片的候选物质排序，适合作为人工复核线索，但不能直接等同于纯物质归属。下面列出每个材料排名前三的候选标签：",
            "",
        ]
    )
    top_candidates = candidates[candidates["candidate_rank"] <= 3].copy()
    if top_candidates.empty:
        lines.extend(["无候选物质数据。", ""])
    else:
        lines.extend(
            [
                top_candidates[
                    ["material", "candidate_rank", "label", "match_score", "matched_count", "missing_typical_count"]
                ].pipe(markdown_table, floatfmt=".3f"),
                "",
            ]
        )

    lines.extend(
        [
            "## 主要观察",
            "",
            "- 含氟材料之间存在大量共享的 `CFx`、`CxFy` 碎片，network 能覆盖不少 RF 公式，但跨材料出现次数较高的公式需要降权。",
            "- PEEK、PPS、PEI、PEN、PI、Nomex 这类芳香/含杂原子聚合物中，碳氢簇和小分子含氧/含氮碎片较多，RF 目录候选容易出现 PE/PP、PVC、ABS 等泛化标签；应优先看同材料 network 命中且跨材料数量较低的公式。",
            "- PAI、PBI、PCTFE 当前没有 network，AI生成输出中出现的有效公式暂时只能作为新增材料建库线索，不能做同材料规则覆盖评价。",
            "- AI生成高分但 network 未覆盖的公式值得分两类处理：如果是合理的材料特征碎片，可以回灌到 rule pack；如果是金属、盐、环境污染或基底峰，应保留为排除/背景标签。",
            "- AI生成候选物质排名目前更像“碎片类别提示”，不是可靠的纯物质判别结果；例如多种材料会被排到 EVA、PE/PP、PVC 或含氮/含氟碎片标签下，因此需要 network 约束和跨材料泛化降权。",
            "",
            "## 建议",
            "",
            "1. 先把 PAI、PBI、PCTFE 加入 `compounds.csv` 并重建 network，否则这三类材料无法进入同一套筛选口径。",
            "2. 对 A/B 级公式做人工确认后，可按材料类型扩展 rule pack，尤其是含氟聚合物的 `CxFy` 系列与芳香聚合物的特征含杂原子碎片。",
            "3. 对跨材料数量很高的公式建立“泛化碎片降权表”，后续 scoring 不宜把它们作为强材料证据。",
            "4. 对无法解析的 RF 公式扩展一个独立的背景/污染元素表，不建议直接扩大 core formula parser 的元素范围，避免 network 生成空间失控。",
            "",
            "## 输出文件",
            "",
            "- `outputs/summary/rf_network_comparison/rf_peak_formulas.csv`：RF 峰级公式清洗结果。",
            "- `outputs/summary/rf_network_comparison/rf_network_formula_comparison.csv`：公式-极性级 network 对比明细。",
            "- `outputs/summary/rf_network_comparison/rf_network_summary_by_material.csv`：按材料汇总。",
            "- `outputs/summary/rf_network_comparison/rf_network_screened_formulas.csv`：A/B 级筛选公式。",
            "- `outputs/summary/rf_network_comparison/rf_top10_peaks_network_check.csv`：每个材料 RF rank 前十峰的 network 覆盖检查。",
            "- `outputs/summary/rf_network_comparison/rf_top10_plain_network_presence.csv`：不引入评分的 RF 原始前十峰全 network 归属表。",
            "- `outputs/summary/rf_network_comparison/rf_top10_plain_network_presence_excel.tsv`：朴素归属表的 Excel 友好版本。",
            "- `outputs/summary/rf_network_comparison/rf_network_screened_top10_peaks.csv`：综合 network 支持、材料特异性和 RF 证据后的每材料前十峰。",
            "- `outputs/summary/rf_network_comparison/rf_network_screened_top10_summary.csv`：筛选版前十峰的材料级数量汇总。",
            "- `outputs/summary/rf_network_comparison/rf_network_screened_top10_peaks_excel.tsv`：给 Windows Excel 打开的 UTF-16 制表符版本，优先用于人工查看。",
            "- `outputs/summary/rf_network_comparison/rf_network_screened_top10_summary_excel.tsv`：筛选汇总的 Excel 友好版本。",
            "- `outputs/summary/rf_network_comparison/rf_substance_candidates.csv`：RF 候选物质汇总。",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rf-root", default="RF_output")
    parser.add_argument("--network-dir", default="outputs/networks")
    parser.add_argument("--output-dir", default="outputs/summary/rf_network_comparison")
    args = parser.parse_args()

    rf_root = Path(args.rf_root)
    network_dir = Path(args.network_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    peaks = load_rf_peaks(rf_root)
    networks = load_networks(network_dir)
    candidates = load_substance_candidates(rf_root)
    rf_formulas = aggregate_rf_formulas(peaks)
    compared = compare_rf_to_network(rf_formulas, networks)
    top10_peaks = check_top10_rf_peaks(peaks, networks)
    screened_top10_peaks, screened_top10_summary = screen_rf_peaks_with_network(peaks, networks)
    summary = summarize_by_material(compared, networks)
    invalid_peaks = peaks[(peaks["rf_formula_raw"].astype(str) != "") & peaks["normalized_formula"].isna()].copy()
    screened = compared[compared["screening_tier"].isin(["A_高置信特征", "B_可用支持"])].copy()

    write_table(peaks, output_dir / "rf_peak_formulas.csv")
    write_table(compared, output_dir / "rf_network_formula_comparison.csv")
    write_table(summary, output_dir / "rf_network_summary_by_material.csv")
    write_table(screened, output_dir / "rf_network_screened_formulas.csv")
    write_table(candidates, output_dir / "rf_substance_candidates.csv")
    write_table(invalid_peaks, output_dir / "rf_invalid_peak_formulas.csv")
    write_table(top10_peaks, output_dir / "rf_top10_peaks_network_check.csv")
    write_table(top10_peaks, output_dir / "rf_top10_plain_network_presence.csv")
    write_excel_tsv(top10_peaks, output_dir / "rf_top10_plain_network_presence_excel.tsv")
    write_table(screened_top10_peaks, output_dir / "rf_network_screened_top10_peaks.csv")
    write_table(screened_top10_summary, output_dir / "rf_network_screened_top10_summary.csv")
    write_excel(screened_top10_peaks, output_dir / "rf_network_screened_top10_peaks.xlsx", sheet_name="screened_top10")
    write_excel(screened_top10_summary, output_dir / "rf_network_screened_top10_summary.xlsx", sheet_name="summary")
    write_excel_tsv(screened_top10_peaks, output_dir / "rf_network_screened_top10_peaks_excel.tsv")
    write_excel_tsv(screened_top10_summary, output_dir / "rf_network_screened_top10_summary_excel.tsv")
    write_report(
        output_dir / "RF_output_network_comparison_report_2026-06-16.md",
        compared,
        summary,
        candidates,
        invalid_peaks,
        top10_peaks,
        screened_top10_peaks,
        screened_top10_summary,
    )

    print(f"RF peaks: {len(peaks)}")
    print(f"RF formula-mode rows: {len(rf_formulas)}")
    print(f"Same-material matches: {int(compared['same_material_mode_match'].sum())}")
    print(f"Report: {output_dir / 'RF_output_network_comparison_report_2026-06-16.md'}")


if __name__ == "__main__":
    main()
