# AI生成标注输出（RF_output）与 formula network 对比筛选报告

生成日期：2026-06-16

> 术语说明：`RF_output` 是历史文件夹命名，本文将其理解为实验室提供的 AI 生成标注输出，不代表 Random Forest。

## 对比口径

- AI生成输出侧使用每个材料 `第1轮/盲分析.json` 中的 `final_proposal`，按“材料 + 归一化分子式 + 极性”聚合。
- network 侧使用 `outputs/networks/*.csv`，严格匹配同一材料、同一分子式、同一离子模式。
- 额外统计每个公式在全部 network 材料中出现的数量，用来识别 `C`、`CH`、`C2H3` 等通用碎片。
- AI生成公式中的 Unicode 下标、正负电荷和同位素质量数会先清洗，例如 `C₂F₅⁺` 归一为 `C2F5`。

## network 筛选 AI生成前十峰算法

给实验室人员查看的筛选版前十峰不是简单 AI生成原始 rank，也不是只看 network 是否命中，而是使用以下综合分数：

- 结构支持分：同材料同极性命中给最高权重；同材料只命中分子式但极性未覆盖给中等权重。
- 特异性分：同一公式/极性在越少材料 network 中出现，分数越高；跨材料普遍出现的通用碎片会降权。
- AI生成证据分：保留 AI生成输出中的 `s` 分数、原始 `rank` 和相对强度作为辅助排序。
- 输出时只保留同材料 network 至少能解释分子式的峰；PAI、PBI、PCTFE 当前没有 network，因此不会产生筛选前十峰。

综合分数可以理解为：`network 结构支持 + 材料特异性 + AI生成置信度 + 原始rank + 峰强`。

### 打分项解释

- 结构支持分：同材料、同分子式、同极性命中 network 时权重最高；如果只命中同材料分子式但极性未覆盖，则保留但降权。
- 材料特异性分：看该公式在多少种材料的 network 中出现。出现材料越少，越像材料特征峰，分数越高；在很多材料中都出现的 `C`、`CH`、`C2H3` 等通用碎片会被降权。严格命中时优先使用 `all_network_compound_count`，极性未命中时使用 `formula_all_network_compound_count`。
- AI生成分数：对应 AI生成/规则流程对该峰公式解释的置信度，反映 ppm、元素合理性、规则奖励、同位素/碎片链等因素。输出表中仍保留历史字段名 `rf_score`。
- AI生成原始 rank：对应该峰在原始谱中的排序重要性。它和峰强相关，但不是同一个信息；rank 表示“是否靠前醒目”，峰强表示“相对贡献有多大”。
- 峰强：使用 `relative_intensity`，即该峰强度占当前材料全部 RF 峰强度的比例。它只作为辅助项，避免低强度但高置信的峰完全压过主峰。

同时使用 AI生成分数和原始 rank 的原因是：AI生成分数描述“公式解释是否可信”，原始 rank 描述“这个峰在谱图中是否重要”。一个高分但很靠后的峰可能是可信弱峰；一个很靠前但低分的峰可能是背景、污染或公式解释不稳。两者结合后，再由 network 结构支持和材料特异性主导排序。

## AI生成输出文件说明

- `盲分析.json`：AI生成/规则流程的峰级完整结果。核心字段是 `peaks`，每条峰包含 `mz`、`intensity`、`pol`、`rank`、候选 `mols`，以及最终采用的 `final_proposal`。本报告的公式级对比主要使用它。
- `LLM工作清单.json`：给 LLM 或人工复核使用的简化峰清单。保留 `mz`、`pol`、`rank`、`intensity`、`final` 和部分 `reasoning`，比 `盲分析.json` 更轻，但信息不如前者完整。
- `substance_candidates.json`：基于目录典型碎片生成的候选物质/碎片类别排名，包含 `candidates`、`matched`、`missing_typicals` 和 `uncovered_formulas`。它适合做提示，不适合直接当纯物质判定。
- `软件标注报告.md`：AI标注软件侧生成的人读报告，主要用于快速查看标注结论和解释，不作为本次程序化匹配的数据源。

## 总体结论

- AI生成输出共得到 13276 个可解析的“公式-极性”组合，其中 366 个被同材料同极性 network 覆盖，整体覆盖率 2.8%；若只看分子式不看极性，同材料覆盖 809 个。
- 排除 PAI、PBI、PCTFE 三个未建 network 的材料后，可评价材料共有 10466 个 AI生成公式-极性组合，严格覆盖 366 个（3.5%），分子式覆盖 809 个（7.7%）。
- 筛选后得到 A 级高置信特征 53 个，B 级可用支持 205 个。A/B 两级更适合作为后续纯物质判别或规则回灌的候选。
- 当前 AI生成输出中有 3 个材料没有对应 network：PAI, PBI, PCTFE。
- 有 647 条 AI生成峰公式未能被当前 formula parser 解析，主要原因通常是 network 元素表未包含金属/污染元素或公式不是标准 Hill 写法。

## A/B/C/D 分级定义

- A_高置信特征：同材料同极性 network 命中，AI生成分数不低于 70，并且相对强度不低于 0.5% 或原始 rank 进入前 100，同时该公式在全部 network 中出现材料数不超过 4。
- B_可用支持：同材料同极性 network 命中，AI生成分数不低于 50，并且该公式在全部 network 中出现材料数不超过 7。它可作为辅助证据，但材料特异性弱于 A 级。
- C_network未覆盖：AI生成输出给出了可解析公式，但同材料同极性 network 没有覆盖。它们是后续规则扩展或背景峰排除的重点检查对象。
- D_泛化或弱证据：同材料同极性 network 有命中，但 AI生成分数、强度/rank 或跨材料特异性不足，不建议单独作为材料判据。

## 按材料汇总

| material | has_network | rf_unique_formula_mode | same_material_mode_matches | same_material_formula_matches | match_rate | formula_match_rate | tier_A_high_confidence | tier_B_support | tier_D_generic_or_weak | tier_C_network_uncovered | top_generation_types |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PEN | True | 848 | 68 | 130 | 0.080 | 0.153 | 6 | 54 | 8 | 780 | adduct; adduct; adduct; adduct; adduct |
| PVDF | True | 897 | 51 | 95 | 0.057 | 0.106 | 11 | 35 | 5 | 846 | adduct; adduct; adduct; adduct; adduct |
| PEEK | True | 1088 | 56 | 132 | 0.051 | 0.121 | 0 | 26 | 30 | 1032 | adduct; adduct; adduct; adduct; adduct |
| ETFE | True | 880 | 39 | 97 | 0.044 | 0.110 | 15 | 22 | 2 | 841 | adduct; adduct; adduct; adduct; adduct |
| Nomex | True | 1006 | 37 | 88 | 0.037 | 0.087 | 2 | 18 | 17 | 969 | adduct; adduct; adduct; adduct; adduct |
| PEI | True | 1075 | 31 | 88 | 0.029 | 0.082 | 1 | 13 | 17 | 1044 | adduct; adduct; adduct; adduct; adduct |
| PFA | True | 797 | 22 | 40 | 0.028 | 0.050 | 7 | 15 | 0 | 775 | adduct; adduct; adduct; adduct; adduct |
| PTFE | True | 958 | 22 | 51 | 0.023 | 0.053 | 4 | 15 | 3 | 936 | adduct; adduct; adduct; adduct; adduct |
| PPS | True | 954 | 15 | 32 | 0.016 | 0.034 | 2 | 2 | 11 | 939 | adduct; adduct; adduct; adduct; adduct |
| PI | True | 1114 | 15 | 35 | 0.013 | 0.031 | 0 | 0 | 15 | 1099 | adduct; adduct; adduct; adduct; adduct |
| FEP | True | 849 | 10 | 21 | 0.012 | 0.025 | 5 | 5 | 0 | 839 | adduct; adduct; adduct; adduct; adduct |
| PAI | False | 1061 | 0 | 0 | 0.000 | 0.000 | 0 | 0 | 0 | 1061 |  |
| PBI | False | 958 | 0 | 0 | 0.000 | 0.000 | 0 | 0 | 0 | 958 |  |
| PCTFE | False | 791 | 0 | 0 | 0.000 | 0.000 | 0 | 0 | 0 | 791 |  |

## 每个材料 AI生成 rank 前十峰的 network 检查

下表使用 `盲分析.json` 中 `rank` 最靠前的 10 个峰。`same_material_mode_match` 是严格的同材料公式+极性命中，`same_material_formula_match` 只看同材料分子式是否存在于 network。

| material | top_order | rank | mz | polarity | rf_formula_raw | normalized_formula | rf_score | same_material_mode_match | same_material_formula_match | all_network_compound_count | all_network_compounds | formula_all_network_compound_count | formula_all_network_compounds | plain_presence_note | generation_types | network_formula_modes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ETFE | 1 | 1 | 19.0009 | - | F⁻ | F | 64 | False | True | 0 |  | 3 | ETFE; PTFE; PVDF | 公式在network中出现但极性未对应 |  | neutral |
| ETFE | 2 | 1 | 77.0238 | + | C₂H₅O₃⁺ | C2H5O3 | 91 | False | False | 0 |  | 5 | EVA; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |  |  |
| ETFE | 3 | 2 | 39.0088 | - | F₂H⁻ | F2H | 76 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| ETFE | 4 | 2 | 75.0076 | + | C₂H₃O₃⁺ | C2H3O3 | 85 | False | False | 0 |  | 5 | EVA; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |  |  |
| ETFE | 5 | 3 | 1.0083 | - | H⁻ | H | 100 | False | False | 0 |  | 8 | EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |  |  |
| ETFE | 6 | 3 | 68.9995 | + | C₃HO₂⁺ | C3HO2 | 57 | False | False | 4 | EVA; PET; POMC; POMH | 5 | EVA; PEN; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| ETFE | 7 | 4 | 30.9992 | + | CF⁺ | CF | 90 | False | True | 0 |  | 5 | ETFE; FEP; PFA; PTFE; PVDF | 公式在network中出现但极性未对应 |  | negative; neutral |
| ETFE | 8 | 4 | 25.0078 | - | C₂H⁻ | C2H | 100 | False | True | 4 | EVA; PEN; PET; PVDF | 7 | COC; ETFE; EVA; PEI; PEN; PET; PVDF | 公式+极性在network中出现 |  | neutral |
| ETFE | 9 | 5 | 95.0129 | + | C₅H₃O₂⁺ | C5H3O2 | 100 | False | False | 4 | EVA; PET; POMC; POMH | 6 | EVA; PEEK; PEEK20%GFR; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| ETFE | 10 | 5 | 48.0001 | - | CHFO⁻ | CHFO | 86 | True | True | 3 | ETFE; PTFE; PVDF | 3 | ETFE; PTFE; PVDF | 公式+极性在network中出现 | adduct | negative |
| FEP | 1 | 1 | 19.0040 | - | F⁻ | F | 100 | False | False | 0 |  | 3 | ETFE; PTFE; PVDF | 公式在network中出现但极性未对应 |  |  |
| FEP | 2 | 1 | 68.9944 | + | C₃HO₂⁺ | C3HO2 | 100 | False | False | 4 | EVA; PET; POMC; POMH | 5 | EVA; PEN; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| FEP | 3 | 2 | 130.9908 | + | C₃F₅⁺ | C3F5 | 66 | False | True | 0 |  | 3 | FEP; PFA; PTFE | 公式在network中出现但极性未对应 |  | neutral |
| FEP | 4 | 2 | 69.0002 | - | CF₃⁻ | CF3 | 100 | True | True | 3 | FEP; PFA; PTFE | 4 | ETFE; FEP; PFA; PTFE | 公式+极性在network中出现 | adduct | negative; neutral |
| FEP | 5 | 3 | 92.9970 | + | C₅HO₂⁺ | C5HO2 | 100 | False | False | 4 | EVA; PET; POMC; POMH | 6 | EVA; PEEK; PEEK20%GFR; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| FEP | 6 | 3 | 38.0024 | - | F₂⁻ | F2 | 100 | False | False | 0 |  | 3 | ETFE; PTFE; PVDF | 公式在network中出现但极性未对应 |  |  |
| FEP | 7 | 4 | 30.9991 | + | CF⁺ | CF | 91 | False | True | 0 |  | 5 | ETFE; FEP; PFA; PTFE; PVDF | 公式在network中出现但极性未对应 |  | neutral |
| FEP | 8 | 4 | 118.9991 | - | C₂F₅⁻ | C2F5 | 100 | False | False | 1 | PTFE | 1 | PTFE | 公式+极性在network中出现 |  |  |
| FEP | 9 | 5 | 99.9957 | + | CHF₃NO⁺ | CHF3NO | 51 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| FEP | 10 | 5 | 43.0034 | - | C₂F⁻ | C2F | 92 | False | False | 0 |  | 2 | ETFE; PVDF | 公式在network中出现但极性未对应 |  |  |
| Nomex | 1 | 1 | 1.0091 | - | H⁻ | H | 15 | False | True | 0 |  | 8 | EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |  | neutral |
| Nomex | 2 | 1 | 132.9044 | + | Cs⁺ | Cs | 90 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| Nomex | 3 | 2 | 26.0064 | - | CN⁻ | CN | 60 | False | True | 0 |  | 1 | Nomex | 公式在network中出现但极性未对应 |  | neutral |
| Nomex | 4 | 2 | 41.0383 | + | C₃H₅⁺ | C3H5 | 100 | False | False | 6 | COC; EVA; PEI; PET; POMC; POMH | 7 | COC; ETFE; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| Nomex | 5 | 3 | 42.0002 | - | CNO⁻ | CNO | 100 | True | True | 1 | Nomex | 1 | Nomex | 公式+极性在network中出现 | adduct | negative; neutral |
| Nomex | 6 | 3 | 22.9892 | + | Na⁺ | Na | 89 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| Nomex | 7 | 4 | 79.9559 | - | NaCaOH⁻ | CaHNaO | 31 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| Nomex | 8 | 4 | 39.0222 | + | C₃H₃⁺ | C3H3 | 100 | False | False | 5 | COC; EVA; PET; POMC; POMH | 7 | COC; ETFE; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| Nomex | 9 | 5 | 25.0080 | - | C₂H⁻ | C2H | 100 | False | False | 4 | EVA; PEN; PET; PVDF | 7 | COC; ETFE; EVA; PEI; PEN; PET; PVDF | 公式+极性在network中出现 |  |  |
| Nomex | 10 | 5 | 43.0548 | + | C₃H₇⁺ | C3H7 | 100 | False | False | 6 | COC; EVA; PEI; PET; POMC; POMH | 6 | COC; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| PAI | 1 | 1 | 132.9089 | + | Cs⁺ | Cs | 93 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PAI | 2 | 1 | 1.0069 | - | H⁻ | H | 15 | False | False | 0 |  | 8 | EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |  |  |
| PAI | 3 | 2 | 26.0134 | - | CN⁻ | CN | 18 | False | False | 0 |  | 1 | Nomex | 公式在network中出现但极性未对应 |  |  |
| PAI | 4 | 2 | 41.0386 | + | C₃H₅⁺ | C3H5 | 100 | False | False | 6 | COC; EVA; PEI; PET; POMC; POMH | 7 | COC; ETFE; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| PAI | 5 | 3 | 25.0158 | - | C₂H⁻ | C2H | 100 | False | False | 4 | EVA; PEN; PET; PVDF | 7 | COC; ETFE; EVA; PEI; PEN; PET; PVDF | 公式+极性在network中出现 |  |  |
| PAI | 6 | 3 | 29.0390 | + | C₂H₅⁺ | C2H5 | 100 | False | False | 6 | COC; ETFE; EVA; PEN; PET; PVDF | 9 | COC; ETFE; EVA; PEI; PEN; PET; POMC; POMH; PVDF | 公式+极性在network中出现 |  |  |
| PAI | 7 | 4 | 15.9982 | - | O⁻ | O | 15 | False | False | 0 |  | 6 | EVA; Nomex; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |  |  |
| PAI | 8 | 4 | 27.0227 | + | C₂H₃⁺ | C2H3 | 100 | False | False | 4 | EVA; PEN; PET; PVDF | 9 | COC; ETFE; EVA; PEI; PEN; PET; POMC; POMH; PVDF | 公式+极性在network中出现 |  |  |
| PAI | 9 | 5 | 42.0153 | - | C₂H₂O⁻ | C2H2O | 63 | False | False | 4 | EVA; PEN; PET; PVDF | 6 | EVA; PEN; PET; POMC; POMH; PVDF | 公式+极性在network中出现 |  |  |
| PAI | 10 | 5 | 22.9906 | + | Na⁺ | Na | 98 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PBI | 1 | 1 | 1.0090 | - | H⁻ | H | 100 | False | False | 0 |  | 8 | EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |  |  |
| PBI | 2 | 1 | 38.9704 | + | K⁺ | K | 15 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PBI | 3 | 2 | 22.9939 | + | Na⁺ | Na | 15 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PBI | 4 | 2 | 25.0096 | - | C₂H⁻ | C2H | 100 | False | False | 4 | EVA; PEN; PET; PVDF | 7 | COC; ETFE; EVA; PEI; PEN; PET; PVDF | 公式+极性在network中出现 |  |  |
| PBI | 5 | 3 | 132.9196 | + | Cs⁺ | Cs | 67 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PBI | 6 | 3 | 26.0060 | - | CN⁻ | CN | 70 | False | False | 0 |  | 1 | Nomex | 公式在network中出现但极性未对应 |  |  |
| PBI | 7 | 4 | 13.0084 | - | CH⁻ | CH | 100 | False | False | 0 |  | 12 | COC; ETFE; EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH; PTFE; PVDF | 公式在network中出现但极性未对应 |  |  |
| PBI | 8 | 4 | 41.0402 | + | C₃H₅⁺ | C3H5 | 100 | False | False | 6 | COC; EVA; PEI; PET; POMC; POMH | 7 | COC; ETFE; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| PBI | 9 | 5 | 15.9952 | - | O⁻ | O | 84 | False | False | 0 |  | 6 | EVA; Nomex; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |  |  |
| PBI | 10 | 5 | 55.0568 | + | C₄H₇⁺ | C4H7 | 100 | False | False | 5 | COC; EVA; PET; POMC; POMH | 5 | COC; EVA; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| PCTFE | 1 | 1 | 19.0008 | - | F⁻ | F | 64 | False | False | 0 |  | 3 | ETFE; PTFE; PVDF | 公式在network中出现但极性未对应 |  |  |
| PCTFE | 2 | 1 | 84.9709 | + | CHCaO₂⁺ | CHCaO2 | 39 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PCTFE | 3 | 2 | 34.9714 | - | Cl⁻ | Cl | 85 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PCTFE | 4 | 2 | 41.0411 | + | C₃H₅⁺ | C3H5 | 100 | False | False | 6 | COC; EVA; PEI; PET; POMC; POMH | 7 | COC; ETFE; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| PCTFE | 5 | 3 | 1.0088 | - | H⁻ | H | 15 | False | False | 0 |  | 8 | EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |  |  |
| PCTFE | 6 | 3 | 30.9991 | + | CF⁺ | CF | 95 | False | False | 0 |  | 5 | ETFE; FEP; PFA; PTFE; PVDF | 公式在network中出现但极性未对应 |  |  |
| PCTFE | 7 | 4 | 36.9667 | - | ³⁷Cl⁻ | Cl | 85 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PCTFE | 8 | 4 | 68.9975 | + | C₃HO₂⁺ | C3HO2 | 97 | False | False | 4 | EVA; PET; POMC; POMH | 5 | EVA; PEN; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| PCTFE | 9 | 5 | 69.9349 | - | Cl₂⁻ | Cl2 | 85 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PCTFE | 10 | 5 | 130.9894 | + | C₅H₄ClO₂⁺ | C5H4ClO2 | 46 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PEEK | 1 | 1 | 1.0083 | - | H⁻ | H | 57 | False | True | 0 |  | 8 | EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |  | neutral |
| PEEK | 2 | 1 | 132.9052 | + | Cs⁺ | Cs | 89 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PEEK | 3 | 2 | 25.0085 | - | C₂H⁻ | C2H | 100 | False | False | 4 | EVA; PEN; PET; PVDF | 7 | COC; ETFE; EVA; PEI; PEN; PET; PVDF | 公式+极性在network中出现 |  |  |
| PEEK | 4 | 2 | 41.0385 | + | C₃H₅⁺ | C3H5 | 100 | False | False | 6 | COC; EVA; PEI; PET; POMC; POMH | 7 | COC; ETFE; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| PEEK | 5 | 3 | 49.0087 | - | C₄H⁻ | C4H | 100 | False | False | 5 | COC; EVA; PET; POMC; POMH | 5 | COC; EVA; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| PEEK | 6 | 3 | 22.9895 | + | Na⁺ | Na | 97 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PEEK | 7 | 4 | 13.0076 | - | CH⁻ | CH | 100 | False | True | 0 |  | 12 | COC; ETFE; EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH; PTFE; PVDF | 公式在network中出现但极性未对应 |  | neutral |
| PEEK | 8 | 4 | 55.0546 | + | C₄H₇⁺ | C4H7 | 100 | False | False | 5 | COC; EVA; PET; POMC; POMH | 5 | COC; EVA; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| PEEK | 9 | 5 | 73.0081 | - | C₆H⁻ | C6H | 100 | True | True | 12 | COC; EVA; Nomex; PEEK; PEEK20%GFR; PEI; PET; PI; POMC; POMH; PPS; PPS40%GFR | 13 | COC; EVA; Nomex; PEEK; PEEK20%GFR; PEI; PET; PI; POMC; POMH; PPS; PPS40%GFR | 公式+极性在network中出现 | adduct | negative; neutral |
| PEEK | 10 | 5 | 43.0549 | + | C₃H₇⁺ | C3H7 | 100 | False | False | 6 | COC; EVA; PEI; PET; POMC; POMH | 6 | COC; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| PEI | 1 | 1 | 1.0084 | - | H⁻ | H | 15 | False | False | 0 |  | 8 | EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |  |  |
| PEI | 2 | 1 | 41.0396 | + | C₃H₅⁺ | C3H5 | 100 | True | True | 6 | COC; EVA; PEI; PET; POMC; POMH | 7 | COC; ETFE; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 | adduct | negative; neutral; positive |
| PEI | 3 | 2 | 25.0086 | - | C₂H⁻ | C2H | 100 | False | True | 4 | EVA; PEN; PET; PVDF | 7 | COC; ETFE; EVA; PEI; PEN; PET; PVDF | 公式+极性在network中出现 |  | neutral |
| PEI | 4 | 2 | 55.0557 | + | C₄H₇⁺ | C4H7 | 100 | False | False | 5 | COC; EVA; PET; POMC; POMH | 5 | COC; EVA; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| PEI | 5 | 3 | 26.0052 | - | CN⁻ | CN | 70 | False | False | 0 |  | 1 | Nomex | 公式在network中出现但极性未对应 |  |  |
| PEI | 6 | 3 | 43.0554 | + | C₃H₇⁺ | C3H7 | 100 | True | True | 6 | COC; EVA; PEI; PET; POMC; POMH | 6 | COC; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 | adduct | negative; neutral; positive |
| PEI | 7 | 4 | 42.0010 | - | CNO⁻ | CNO | 64 | False | False | 1 | Nomex | 1 | Nomex | 公式+极性在network中出现 |  |  |
| PEI | 8 | 4 | 29.0388 | + | C₂H₅⁺ | C2H5 | 100 | False | True | 6 | COC; ETFE; EVA; PEN; PET; PVDF | 9 | COC; ETFE; EVA; PEI; PEN; PET; POMC; POMH; PVDF | 公式+极性在network中出现 |  | neutral |
| PEI | 9 | 5 | 13.0072 | - | CH⁻ | CH | 91 | False | False | 0 |  | 12 | COC; ETFE; EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH; PTFE; PVDF | 公式在network中出现但极性未对应 |  |  |
| PEI | 10 | 5 | 27.0225 | + | C₂H₃⁺ | C2H3 | 100 | False | True | 4 | EVA; PEN; PET; PVDF | 9 | COC; ETFE; EVA; PEI; PEN; PET; POMC; POMH; PVDF | 公式+极性在network中出现 |  | neutral |
| PEN | 1 | 1 | 1.0085 | - | H⁻ | H | 15 | False | True | 0 |  | 8 | EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |  | neutral |
| PEN | 2 | 1 | 132.9038 | + | Cs⁺ | Cs | 89 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PEN | 3 | 2 | 25.0090 | - | C₂H⁻ | C2H | 100 | True | True | 4 | EVA; PEN; PET; PVDF | 7 | COC; ETFE; EVA; PEI; PEN; PET; PVDF | 公式+极性在network中出现 | adduct | negative; neutral |
| PEN | 4 | 2 | 126.0440 | + | C₁₀H₆⁺ | C10H6 | 84 | True | True | 6 | COC; EVA; PEN; PET; POMC; POMH | 6 | COC; EVA; PEN; PET; POMC; POMH | 公式+极性在network中出现 | adduct | negative; neutral; positive |
| PEN | 5 | 3 | 49.0093 | - | C₄H⁻ | C4H | 100 | False | False | 5 | COC; EVA; PET; POMC; POMH | 5 | COC; EVA; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| PEN | 6 | 3 | 154.0411 | + | C₁₁H₆O⁺ | C11H6O | 83 | True | True | 5 | EVA; PEN; PET; POMC; POMH | 8 | EVA; PEEK; PEEK20%GFR; PEN; PET; PI; POMC; POMH | 公式+极性在network中出现 | adduct | negative; neutral; positive |
| PEN | 7 | 4 | 15.9956 | - | O⁻ | O | 100 | False | True | 0 |  | 6 | EVA; Nomex; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |  | neutral |
| PEN | 8 | 4 | 127.0511 | + | C₁₀H₇⁺ | C10H7 | 85 | True | True | 6 | COC; EVA; PEN; PET; POMC; POMH | 6 | COC; EVA; PEN; PET; POMC; POMH | 公式+极性在network中出现 | adduct | negative; neutral; positive |
| PEN | 9 | 5 | 24.0004 | - | C₂⁻ | C2 | 100 | False | True | 0 |  | 4 | EVA; PEN; PET; PVDF | 公式在network中出现但极性未对应 |  | neutral |
| PEN | 10 | 5 | 41.0387 | + | C₃H₅⁺ | C3H5 | 100 | False | False | 6 | COC; EVA; PEI; PET; POMC; POMH | 7 | COC; ETFE; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| PFA | 1 | 1 | 18.9994 | - | F⁻ | F | 100 | False | False | 0 |  | 3 | ETFE; PTFE; PVDF | 公式在network中出现但极性未对应 |  |  |
| PFA | 2 | 1 | 130.9942 | + | C₄H₃O₅⁺ | C4H3O5 | 64 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PFA | 3 | 2 | 184.9913 | - | C₅F₅NO⁻ | C5F5NO | 100 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PFA | 4 | 2 | 68.9948 | + | C₃HO₂⁺ | C3HO2 | 90 | False | False | 4 | EVA; PET; POMC; POMH | 5 | EVA; PEN; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| PFA | 5 | 3 | 92.9988 | + | C₅HO₂⁺ | C5HO2 | 84 | False | False | 4 | EVA; PET; POMC; POMH | 6 | EVA; PEEK; PEEK20%GFR; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| PFA | 6 | 3 | 37.9977 | - | F₂⁻ | F2 | 100 | False | False | 0 |  | 3 | ETFE; PTFE; PVDF | 公式在network中出现但极性未对应 |  |  |
| PFA | 7 | 4 | 30.9983 | + | CF⁺ | CF | 100 | False | True | 0 |  | 5 | ETFE; FEP; PFA; PTFE; PVDF | 公式在network中出现但极性未对应 |  | neutral |
| PFA | 8 | 4 | 118.9927 | - | C₂F₅⁻ | C2F5 | 100 | False | False | 1 | PTFE | 1 | PTFE | 公式+极性在network中出现 |  |  |
| PFA | 9 | 5 | 99.9969 | + | CHF₃NO⁺ | CHF3NO | 45 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PFA | 10 | 5 | 68.9957 | - | CF₃⁻ | CF3 | 100 | True | True | 3 | FEP; PFA; PTFE | 4 | ETFE; FEP; PFA; PTFE | 公式+极性在network中出现 | adduct | negative; neutral |
| PI | 1 | 1 | 132.9096 | + | Cs⁺ | Cs | 84 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PI | 2 | 1 | 26.0059 | - | CN⁻ | CN | 67 | False | False | 0 |  | 1 | Nomex | 公式在network中出现但极性未对应 |  |  |
| PI | 3 | 2 | 1.0084 | - | H⁻ | H | 15 | False | False | 0 |  | 8 | EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |  |  |
| PI | 4 | 2 | 291.8141 | + | C₄H₂Cl₆O₂⁺ | C4H2Cl6O2 | 50 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PI | 5 | 3 | 42.0008 | - | CNO⁻ | CNO | 81 | False | False | 1 | Nomex | 1 | Nomex | 公式+极性在network中出现 |  |  |
| PI | 6 | 3 | 307.8088 | + | C₃H₇Br₃N₂⁺ | C3H7Br3N2 | 32 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PI | 7 | 4 | 25.0081 | - | C₂H⁻ | C2H | 100 | False | False | 4 | EVA; PEN; PET; PVDF | 7 | COC; ETFE; EVA; PEI; PEN; PET; PVDF | 公式+极性在network中出现 |  |  |
| PI | 8 | 4 | 41.0388 | + | C₃H₅⁺ | C3H5 | 100 | False | False | 6 | COC; EVA; PEI; PET; POMC; POMH | 7 | COC; ETFE; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| PI | 9 | 5 | 50.0044 | - | C₃N⁻ | C3N | 100 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PI | 10 | 5 | 43.0553 | + | C₃H₇⁺ | C3H7 | 100 | False | False | 6 | COC; EVA; PEI; PET; POMC; POMH | 6 | COC; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| PPS | 1 | 1 | 132.9057 | + | Cs⁺ | Cs | 89 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PPS | 2 | 1 | 1.0085 | - | H⁻ | H | 100 | False | False | 0 |  | 8 | EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |  |  |
| PPS | 3 | 2 | 139.9794 | - | H₁₂S₄⁻ | H12S4 | 100 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PPS | 4 | 2 | 38.9634 | + | K⁺ | K | 100 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PPS | 5 | 3 | 25.0085 | - | C₂H⁻ | C2H | 100 | False | False | 4 | EVA; PEN; PET; PVDF | 7 | COC; ETFE; EVA; PEI; PEN; PET; PVDF | 公式+极性在network中出现 |  |  |
| PPS | 6 | 3 | 22.9894 | + | Na⁺ | Na | 95 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PPS | 7 | 4 | 56.9808 | - | C₂HS⁻ | C2HS | 100 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PPS | 8 | 4 | 300.7691 | + | I₂OP⁺ | I2OP | 30 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PPS | 9 | 5 | 49.0086 | - | C₄H⁻ | C4H | 100 | False | False | 5 | COC; EVA; PET; POMC; POMH | 5 | COC; EVA; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| PPS | 10 | 5 | 41.0385 | + | C₃H₅⁺ | C3H5 | 100 | False | False | 6 | COC; EVA; PEI; PET; POMC; POMH | 7 | COC; ETFE; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| PTFE | 1 | 1 | 19.0010 | - | F⁻ | F | 15 | False | True | 0 |  | 3 | ETFE; PTFE; PVDF | 公式在network中出现但极性未对应 |  | neutral |
| PTFE | 2 | 1 | 69.0023 | + | C₃HO₂⁺ | C3HO2 | 100 | False | False | 4 | EVA; PET; POMC; POMH | 5 | EVA; PEN; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| PTFE | 3 | 2 | 31.0009 | + | H₃Si⁺ | H3Si | 32 | False | False | 1 | PDMS | 1 | PDMS | 公式+极性在network中出现 |  |  |
| PTFE | 4 | 2 | 1.0086 | - | H⁻ | H | 100 | False | False | 0 |  | 8 | EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |  |  |
| PTFE | 5 | 3 | 130.9965 | + | C₅H₄ClO₂⁺ | C5H4ClO2 | 67 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PTFE | 6 | 3 | 37.9970 | - | F₂⁻ | F2 | 73 | False | True | 0 |  | 3 | ETFE; PTFE; PVDF | 公式在network中出现但极性未对应 |  | neutral |
| PTFE | 7 | 4 | 92.9976 | + | C₅HO₂⁺ | C5HO2 | 100 | False | False | 4 | EVA; PET; POMC; POMH | 6 | EVA; PEEK; PEEK20%GFR; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| PTFE | 8 | 4 | 68.9953 | - | CF₃⁻ | CF3 | 100 | True | True | 3 | FEP; PFA; PTFE | 4 | ETFE; FEP; PFA; PTFE | 公式+极性在network中出现 | adduct | negative; neutral |
| PTFE | 9 | 5 | 132.9069 | + | Cs⁺ | Cs | 86 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PTFE | 10 | 5 | 42.9985 | - | C₂F⁻ | C2F | 86 | False | False | 0 |  | 2 | ETFE; PVDF | 公式在network中出现但极性未对应 |  |  |
| PVDF | 1 | 1 | 19.0007 | - | F⁻ | F | 100 | False | True | 0 |  | 3 | ETFE; PTFE; PVDF | 公式在network中出现但极性未对应 |  | neutral |
| PVDF | 2 | 1 | 113.0019 | + | C₈HO⁺ | C8HO | 66 | False | False | 4 | EVA; PET; POMC; POMH | 5 | EVA; Nomex; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| PVDF | 3 | 2 | 39.0088 | - | F₂H⁻ | F2H | 91 | False | False | 0 |  | 0 |  | network未出现 |  |  |
| PVDF | 4 | 2 | 133.0066 | + | C₁₁H⁺ | C11H | 78 | False | False | 5 | COC; EVA; PET; POMC; POMH | 5 | COC; EVA; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| PVDF | 5 | 3 | 1.0084 | - | H⁻ | H | 15 | False | False | 0 |  | 8 | EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |  |  |
| PVDF | 6 | 3 | 68.9990 | + | C₃HO₂⁺ | C3HO2 | 75 | False | False | 4 | EVA; PET; POMC; POMH | 5 | EVA; PEN; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| PVDF | 7 | 4 | 95.0113 | + | C₅H₃O₂⁺ | C5H3O2 | 99 | False | False | 4 | EVA; PET; POMC; POMH | 6 | EVA; PEEK; PEEK20%GFR; PET; POMC; POMH | 公式+极性在network中出现 |  |  |
| PVDF | 8 | 4 | 25.0085 | - | C₂H⁻ | C2H | 100 | True | True | 4 | EVA; PEN; PET; PVDF | 7 | COC; ETFE; EVA; PEI; PEN; PET; PVDF | 公式+极性在network中出现 | adduct | negative; neutral |
| PVDF | 9 | 5 | 77.0208 | + | C₂H₅O₃⁺ | C2H5O3 | 86 | False | False | 0 |  | 5 | EVA; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |  |  |
| PVDF | 10 | 5 | 34.9712 | - | Cl⁻ | Cl | 100 | False | False | 0 |  | 0 |  | network未出现 |  |  |

## AI生成原始前十峰的朴素 network 归属

这一节不引入任何评分机制，只回答：每个材料 AI生成原始 rank 前十峰的公式是否出现在全部 network 中；如果出现，出现在哪些材料中。`all_network_compounds` 使用“公式+极性”口径，`formula_all_network_compounds` 只看公式、不看极性。

| material | top_order | rank | mz | polarity | rf_formula_raw | normalized_formula | rf_score | all_network_compound_count | all_network_compounds | formula_all_network_compound_count | formula_all_network_compounds | plain_presence_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ETFE | 1 | 1 | 19.0009 | - | F⁻ | F | 64 | 0 |  | 3 | ETFE; PTFE; PVDF | 公式在network中出现但极性未对应 |
| ETFE | 2 | 1 | 77.0238 | + | C₂H₅O₃⁺ | C2H5O3 | 91 | 0 |  | 5 | EVA; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |
| ETFE | 3 | 2 | 39.0088 | - | F₂H⁻ | F2H | 76 | 0 |  | 0 |  | network未出现 |
| ETFE | 4 | 2 | 75.0076 | + | C₂H₃O₃⁺ | C2H3O3 | 85 | 0 |  | 5 | EVA; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |
| ETFE | 5 | 3 | 1.0083 | - | H⁻ | H | 100 | 0 |  | 8 | EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |
| ETFE | 6 | 3 | 68.9995 | + | C₃HO₂⁺ | C3HO2 | 57 | 4 | EVA; PET; POMC; POMH | 5 | EVA; PEN; PET; POMC; POMH | 公式+极性在network中出现 |
| ETFE | 7 | 4 | 30.9992 | + | CF⁺ | CF | 90 | 0 |  | 5 | ETFE; FEP; PFA; PTFE; PVDF | 公式在network中出现但极性未对应 |
| ETFE | 8 | 4 | 25.0078 | - | C₂H⁻ | C2H | 100 | 4 | EVA; PEN; PET; PVDF | 7 | COC; ETFE; EVA; PEI; PEN; PET; PVDF | 公式+极性在network中出现 |
| ETFE | 9 | 5 | 95.0129 | + | C₅H₃O₂⁺ | C5H3O2 | 100 | 4 | EVA; PET; POMC; POMH | 6 | EVA; PEEK; PEEK20%GFR; PET; POMC; POMH | 公式+极性在network中出现 |
| ETFE | 10 | 5 | 48.0001 | - | CHFO⁻ | CHFO | 86 | 3 | ETFE; PTFE; PVDF | 3 | ETFE; PTFE; PVDF | 公式+极性在network中出现 |
| FEP | 1 | 1 | 19.0040 | - | F⁻ | F | 100 | 0 |  | 3 | ETFE; PTFE; PVDF | 公式在network中出现但极性未对应 |
| FEP | 2 | 1 | 68.9944 | + | C₃HO₂⁺ | C3HO2 | 100 | 4 | EVA; PET; POMC; POMH | 5 | EVA; PEN; PET; POMC; POMH | 公式+极性在network中出现 |
| FEP | 3 | 2 | 130.9908 | + | C₃F₅⁺ | C3F5 | 66 | 0 |  | 3 | FEP; PFA; PTFE | 公式在network中出现但极性未对应 |
| FEP | 4 | 2 | 69.0002 | - | CF₃⁻ | CF3 | 100 | 3 | FEP; PFA; PTFE | 4 | ETFE; FEP; PFA; PTFE | 公式+极性在network中出现 |
| FEP | 5 | 3 | 92.9970 | + | C₅HO₂⁺ | C5HO2 | 100 | 4 | EVA; PET; POMC; POMH | 6 | EVA; PEEK; PEEK20%GFR; PET; POMC; POMH | 公式+极性在network中出现 |
| FEP | 6 | 3 | 38.0024 | - | F₂⁻ | F2 | 100 | 0 |  | 3 | ETFE; PTFE; PVDF | 公式在network中出现但极性未对应 |
| FEP | 7 | 4 | 30.9991 | + | CF⁺ | CF | 91 | 0 |  | 5 | ETFE; FEP; PFA; PTFE; PVDF | 公式在network中出现但极性未对应 |
| FEP | 8 | 4 | 118.9991 | - | C₂F₅⁻ | C2F5 | 100 | 1 | PTFE | 1 | PTFE | 公式+极性在network中出现 |
| FEP | 9 | 5 | 99.9957 | + | CHF₃NO⁺ | CHF3NO | 51 | 0 |  | 0 |  | network未出现 |
| FEP | 10 | 5 | 43.0034 | - | C₂F⁻ | C2F | 92 | 0 |  | 2 | ETFE; PVDF | 公式在network中出现但极性未对应 |
| Nomex | 1 | 1 | 1.0091 | - | H⁻ | H | 15 | 0 |  | 8 | EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |
| Nomex | 2 | 1 | 132.9044 | + | Cs⁺ | Cs | 90 | 0 |  | 0 |  | network未出现 |
| Nomex | 3 | 2 | 26.0064 | - | CN⁻ | CN | 60 | 0 |  | 1 | Nomex | 公式在network中出现但极性未对应 |
| Nomex | 4 | 2 | 41.0383 | + | C₃H₅⁺ | C3H5 | 100 | 6 | COC; EVA; PEI; PET; POMC; POMH | 7 | COC; ETFE; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 |
| Nomex | 5 | 3 | 42.0002 | - | CNO⁻ | CNO | 100 | 1 | Nomex | 1 | Nomex | 公式+极性在network中出现 |
| Nomex | 6 | 3 | 22.9892 | + | Na⁺ | Na | 89 | 0 |  | 0 |  | network未出现 |
| Nomex | 7 | 4 | 79.9559 | - | NaCaOH⁻ | CaHNaO | 31 | 0 |  | 0 |  | network未出现 |
| Nomex | 8 | 4 | 39.0222 | + | C₃H₃⁺ | C3H3 | 100 | 5 | COC; EVA; PET; POMC; POMH | 7 | COC; ETFE; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 |
| Nomex | 9 | 5 | 25.0080 | - | C₂H⁻ | C2H | 100 | 4 | EVA; PEN; PET; PVDF | 7 | COC; ETFE; EVA; PEI; PEN; PET; PVDF | 公式+极性在network中出现 |
| Nomex | 10 | 5 | 43.0548 | + | C₃H₇⁺ | C3H7 | 100 | 6 | COC; EVA; PEI; PET; POMC; POMH | 6 | COC; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 |
| PAI | 1 | 1 | 132.9089 | + | Cs⁺ | Cs | 93 | 0 |  | 0 |  | network未出现 |
| PAI | 2 | 1 | 1.0069 | - | H⁻ | H | 15 | 0 |  | 8 | EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |
| PAI | 3 | 2 | 26.0134 | - | CN⁻ | CN | 18 | 0 |  | 1 | Nomex | 公式在network中出现但极性未对应 |
| PAI | 4 | 2 | 41.0386 | + | C₃H₅⁺ | C3H5 | 100 | 6 | COC; EVA; PEI; PET; POMC; POMH | 7 | COC; ETFE; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 |
| PAI | 5 | 3 | 25.0158 | - | C₂H⁻ | C2H | 100 | 4 | EVA; PEN; PET; PVDF | 7 | COC; ETFE; EVA; PEI; PEN; PET; PVDF | 公式+极性在network中出现 |
| PAI | 6 | 3 | 29.0390 | + | C₂H₅⁺ | C2H5 | 100 | 6 | COC; ETFE; EVA; PEN; PET; PVDF | 9 | COC; ETFE; EVA; PEI; PEN; PET; POMC; POMH; PVDF | 公式+极性在network中出现 |
| PAI | 7 | 4 | 15.9982 | - | O⁻ | O | 15 | 0 |  | 6 | EVA; Nomex; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |
| PAI | 8 | 4 | 27.0227 | + | C₂H₃⁺ | C2H3 | 100 | 4 | EVA; PEN; PET; PVDF | 9 | COC; ETFE; EVA; PEI; PEN; PET; POMC; POMH; PVDF | 公式+极性在network中出现 |
| PAI | 9 | 5 | 42.0153 | - | C₂H₂O⁻ | C2H2O | 63 | 4 | EVA; PEN; PET; PVDF | 6 | EVA; PEN; PET; POMC; POMH; PVDF | 公式+极性在network中出现 |
| PAI | 10 | 5 | 22.9906 | + | Na⁺ | Na | 98 | 0 |  | 0 |  | network未出现 |
| PBI | 1 | 1 | 1.0090 | - | H⁻ | H | 100 | 0 |  | 8 | EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |
| PBI | 2 | 1 | 38.9704 | + | K⁺ | K | 15 | 0 |  | 0 |  | network未出现 |
| PBI | 3 | 2 | 22.9939 | + | Na⁺ | Na | 15 | 0 |  | 0 |  | network未出现 |
| PBI | 4 | 2 | 25.0096 | - | C₂H⁻ | C2H | 100 | 4 | EVA; PEN; PET; PVDF | 7 | COC; ETFE; EVA; PEI; PEN; PET; PVDF | 公式+极性在network中出现 |
| PBI | 5 | 3 | 132.9196 | + | Cs⁺ | Cs | 67 | 0 |  | 0 |  | network未出现 |
| PBI | 6 | 3 | 26.0060 | - | CN⁻ | CN | 70 | 0 |  | 1 | Nomex | 公式在network中出现但极性未对应 |
| PBI | 7 | 4 | 13.0084 | - | CH⁻ | CH | 100 | 0 |  | 12 | COC; ETFE; EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH; PTFE; PVDF | 公式在network中出现但极性未对应 |
| PBI | 8 | 4 | 41.0402 | + | C₃H₅⁺ | C3H5 | 100 | 6 | COC; EVA; PEI; PET; POMC; POMH | 7 | COC; ETFE; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 |
| PBI | 9 | 5 | 15.9952 | - | O⁻ | O | 84 | 0 |  | 6 | EVA; Nomex; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |
| PBI | 10 | 5 | 55.0568 | + | C₄H₇⁺ | C4H7 | 100 | 5 | COC; EVA; PET; POMC; POMH | 5 | COC; EVA; PET; POMC; POMH | 公式+极性在network中出现 |
| PCTFE | 1 | 1 | 19.0008 | - | F⁻ | F | 64 | 0 |  | 3 | ETFE; PTFE; PVDF | 公式在network中出现但极性未对应 |
| PCTFE | 2 | 1 | 84.9709 | + | CHCaO₂⁺ | CHCaO2 | 39 | 0 |  | 0 |  | network未出现 |
| PCTFE | 3 | 2 | 34.9714 | - | Cl⁻ | Cl | 85 | 0 |  | 0 |  | network未出现 |
| PCTFE | 4 | 2 | 41.0411 | + | C₃H₅⁺ | C3H5 | 100 | 6 | COC; EVA; PEI; PET; POMC; POMH | 7 | COC; ETFE; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 |
| PCTFE | 5 | 3 | 1.0088 | - | H⁻ | H | 15 | 0 |  | 8 | EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |
| PCTFE | 6 | 3 | 30.9991 | + | CF⁺ | CF | 95 | 0 |  | 5 | ETFE; FEP; PFA; PTFE; PVDF | 公式在network中出现但极性未对应 |
| PCTFE | 7 | 4 | 36.9667 | - | ³⁷Cl⁻ | Cl | 85 | 0 |  | 0 |  | network未出现 |
| PCTFE | 8 | 4 | 68.9975 | + | C₃HO₂⁺ | C3HO2 | 97 | 4 | EVA; PET; POMC; POMH | 5 | EVA; PEN; PET; POMC; POMH | 公式+极性在network中出现 |
| PCTFE | 9 | 5 | 69.9349 | - | Cl₂⁻ | Cl2 | 85 | 0 |  | 0 |  | network未出现 |
| PCTFE | 10 | 5 | 130.9894 | + | C₅H₄ClO₂⁺ | C5H4ClO2 | 46 | 0 |  | 0 |  | network未出现 |
| PEEK | 1 | 1 | 1.0083 | - | H⁻ | H | 57 | 0 |  | 8 | EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |
| PEEK | 2 | 1 | 132.9052 | + | Cs⁺ | Cs | 89 | 0 |  | 0 |  | network未出现 |
| PEEK | 3 | 2 | 25.0085 | - | C₂H⁻ | C2H | 100 | 4 | EVA; PEN; PET; PVDF | 7 | COC; ETFE; EVA; PEI; PEN; PET; PVDF | 公式+极性在network中出现 |
| PEEK | 4 | 2 | 41.0385 | + | C₃H₅⁺ | C3H5 | 100 | 6 | COC; EVA; PEI; PET; POMC; POMH | 7 | COC; ETFE; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 |
| PEEK | 5 | 3 | 49.0087 | - | C₄H⁻ | C4H | 100 | 5 | COC; EVA; PET; POMC; POMH | 5 | COC; EVA; PET; POMC; POMH | 公式+极性在network中出现 |
| PEEK | 6 | 3 | 22.9895 | + | Na⁺ | Na | 97 | 0 |  | 0 |  | network未出现 |
| PEEK | 7 | 4 | 13.0076 | - | CH⁻ | CH | 100 | 0 |  | 12 | COC; ETFE; EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH; PTFE; PVDF | 公式在network中出现但极性未对应 |
| PEEK | 8 | 4 | 55.0546 | + | C₄H₇⁺ | C4H7 | 100 | 5 | COC; EVA; PET; POMC; POMH | 5 | COC; EVA; PET; POMC; POMH | 公式+极性在network中出现 |
| PEEK | 9 | 5 | 73.0081 | - | C₆H⁻ | C6H | 100 | 12 | COC; EVA; Nomex; PEEK; PEEK20%GFR; PEI; PET; PI; POMC; POMH; PPS; PPS40%GFR | 13 | COC; EVA; Nomex; PEEK; PEEK20%GFR; PEI; PET; PI; POMC; POMH; PPS; PPS40%GFR | 公式+极性在network中出现 |
| PEEK | 10 | 5 | 43.0549 | + | C₃H₇⁺ | C3H7 | 100 | 6 | COC; EVA; PEI; PET; POMC; POMH | 6 | COC; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 |
| PEI | 1 | 1 | 1.0084 | - | H⁻ | H | 15 | 0 |  | 8 | EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |
| PEI | 2 | 1 | 41.0396 | + | C₃H₅⁺ | C3H5 | 100 | 6 | COC; EVA; PEI; PET; POMC; POMH | 7 | COC; ETFE; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 |
| PEI | 3 | 2 | 25.0086 | - | C₂H⁻ | C2H | 100 | 4 | EVA; PEN; PET; PVDF | 7 | COC; ETFE; EVA; PEI; PEN; PET; PVDF | 公式+极性在network中出现 |
| PEI | 4 | 2 | 55.0557 | + | C₄H₇⁺ | C4H7 | 100 | 5 | COC; EVA; PET; POMC; POMH | 5 | COC; EVA; PET; POMC; POMH | 公式+极性在network中出现 |
| PEI | 5 | 3 | 26.0052 | - | CN⁻ | CN | 70 | 0 |  | 1 | Nomex | 公式在network中出现但极性未对应 |
| PEI | 6 | 3 | 43.0554 | + | C₃H₇⁺ | C3H7 | 100 | 6 | COC; EVA; PEI; PET; POMC; POMH | 6 | COC; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 |
| PEI | 7 | 4 | 42.0010 | - | CNO⁻ | CNO | 64 | 1 | Nomex | 1 | Nomex | 公式+极性在network中出现 |
| PEI | 8 | 4 | 29.0388 | + | C₂H₅⁺ | C2H5 | 100 | 6 | COC; ETFE; EVA; PEN; PET; PVDF | 9 | COC; ETFE; EVA; PEI; PEN; PET; POMC; POMH; PVDF | 公式+极性在network中出现 |
| PEI | 9 | 5 | 13.0072 | - | CH⁻ | CH | 91 | 0 |  | 12 | COC; ETFE; EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH; PTFE; PVDF | 公式在network中出现但极性未对应 |
| PEI | 10 | 5 | 27.0225 | + | C₂H₃⁺ | C2H3 | 100 | 4 | EVA; PEN; PET; PVDF | 9 | COC; ETFE; EVA; PEI; PEN; PET; POMC; POMH; PVDF | 公式+极性在network中出现 |
| PEN | 1 | 1 | 1.0085 | - | H⁻ | H | 15 | 0 |  | 8 | EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |
| PEN | 2 | 1 | 132.9038 | + | Cs⁺ | Cs | 89 | 0 |  | 0 |  | network未出现 |
| PEN | 3 | 2 | 25.0090 | - | C₂H⁻ | C2H | 100 | 4 | EVA; PEN; PET; PVDF | 7 | COC; ETFE; EVA; PEI; PEN; PET; PVDF | 公式+极性在network中出现 |
| PEN | 4 | 2 | 126.0440 | + | C₁₀H₆⁺ | C10H6 | 84 | 6 | COC; EVA; PEN; PET; POMC; POMH | 6 | COC; EVA; PEN; PET; POMC; POMH | 公式+极性在network中出现 |
| PEN | 5 | 3 | 49.0093 | - | C₄H⁻ | C4H | 100 | 5 | COC; EVA; PET; POMC; POMH | 5 | COC; EVA; PET; POMC; POMH | 公式+极性在network中出现 |
| PEN | 6 | 3 | 154.0411 | + | C₁₁H₆O⁺ | C11H6O | 83 | 5 | EVA; PEN; PET; POMC; POMH | 8 | EVA; PEEK; PEEK20%GFR; PEN; PET; PI; POMC; POMH | 公式+极性在network中出现 |
| PEN | 7 | 4 | 15.9956 | - | O⁻ | O | 100 | 0 |  | 6 | EVA; Nomex; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |
| PEN | 8 | 4 | 127.0511 | + | C₁₀H₇⁺ | C10H7 | 85 | 6 | COC; EVA; PEN; PET; POMC; POMH | 6 | COC; EVA; PEN; PET; POMC; POMH | 公式+极性在network中出现 |
| PEN | 9 | 5 | 24.0004 | - | C₂⁻ | C2 | 100 | 0 |  | 4 | EVA; PEN; PET; PVDF | 公式在network中出现但极性未对应 |
| PEN | 10 | 5 | 41.0387 | + | C₃H₅⁺ | C3H5 | 100 | 6 | COC; EVA; PEI; PET; POMC; POMH | 7 | COC; ETFE; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 |
| PFA | 1 | 1 | 18.9994 | - | F⁻ | F | 100 | 0 |  | 3 | ETFE; PTFE; PVDF | 公式在network中出现但极性未对应 |
| PFA | 2 | 1 | 130.9942 | + | C₄H₃O₅⁺ | C4H3O5 | 64 | 0 |  | 0 |  | network未出现 |
| PFA | 3 | 2 | 184.9913 | - | C₅F₅NO⁻ | C5F5NO | 100 | 0 |  | 0 |  | network未出现 |
| PFA | 4 | 2 | 68.9948 | + | C₃HO₂⁺ | C3HO2 | 90 | 4 | EVA; PET; POMC; POMH | 5 | EVA; PEN; PET; POMC; POMH | 公式+极性在network中出现 |
| PFA | 5 | 3 | 92.9988 | + | C₅HO₂⁺ | C5HO2 | 84 | 4 | EVA; PET; POMC; POMH | 6 | EVA; PEEK; PEEK20%GFR; PET; POMC; POMH | 公式+极性在network中出现 |
| PFA | 6 | 3 | 37.9977 | - | F₂⁻ | F2 | 100 | 0 |  | 3 | ETFE; PTFE; PVDF | 公式在network中出现但极性未对应 |
| PFA | 7 | 4 | 30.9983 | + | CF⁺ | CF | 100 | 0 |  | 5 | ETFE; FEP; PFA; PTFE; PVDF | 公式在network中出现但极性未对应 |
| PFA | 8 | 4 | 118.9927 | - | C₂F₅⁻ | C2F5 | 100 | 1 | PTFE | 1 | PTFE | 公式+极性在network中出现 |
| PFA | 9 | 5 | 99.9969 | + | CHF₃NO⁺ | CHF3NO | 45 | 0 |  | 0 |  | network未出现 |
| PFA | 10 | 5 | 68.9957 | - | CF₃⁻ | CF3 | 100 | 3 | FEP; PFA; PTFE | 4 | ETFE; FEP; PFA; PTFE | 公式+极性在network中出现 |
| PI | 1 | 1 | 132.9096 | + | Cs⁺ | Cs | 84 | 0 |  | 0 |  | network未出现 |
| PI | 2 | 1 | 26.0059 | - | CN⁻ | CN | 67 | 0 |  | 1 | Nomex | 公式在network中出现但极性未对应 |
| PI | 3 | 2 | 1.0084 | - | H⁻ | H | 15 | 0 |  | 8 | EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |
| PI | 4 | 2 | 291.8141 | + | C₄H₂Cl₆O₂⁺ | C4H2Cl6O2 | 50 | 0 |  | 0 |  | network未出现 |
| PI | 5 | 3 | 42.0008 | - | CNO⁻ | CNO | 81 | 1 | Nomex | 1 | Nomex | 公式+极性在network中出现 |
| PI | 6 | 3 | 307.8088 | + | C₃H₇Br₃N₂⁺ | C3H7Br3N2 | 32 | 0 |  | 0 |  | network未出现 |
| PI | 7 | 4 | 25.0081 | - | C₂H⁻ | C2H | 100 | 4 | EVA; PEN; PET; PVDF | 7 | COC; ETFE; EVA; PEI; PEN; PET; PVDF | 公式+极性在network中出现 |
| PI | 8 | 4 | 41.0388 | + | C₃H₅⁺ | C3H5 | 100 | 6 | COC; EVA; PEI; PET; POMC; POMH | 7 | COC; ETFE; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 |
| PI | 9 | 5 | 50.0044 | - | C₃N⁻ | C3N | 100 | 0 |  | 0 |  | network未出现 |
| PI | 10 | 5 | 43.0553 | + | C₃H₇⁺ | C3H7 | 100 | 6 | COC; EVA; PEI; PET; POMC; POMH | 6 | COC; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 |
| PPS | 1 | 1 | 132.9057 | + | Cs⁺ | Cs | 89 | 0 |  | 0 |  | network未出现 |
| PPS | 2 | 1 | 1.0085 | - | H⁻ | H | 100 | 0 |  | 8 | EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |
| PPS | 3 | 2 | 139.9794 | - | H₁₂S₄⁻ | H12S4 | 100 | 0 |  | 0 |  | network未出现 |
| PPS | 4 | 2 | 38.9634 | + | K⁺ | K | 100 | 0 |  | 0 |  | network未出现 |
| PPS | 5 | 3 | 25.0085 | - | C₂H⁻ | C2H | 100 | 4 | EVA; PEN; PET; PVDF | 7 | COC; ETFE; EVA; PEI; PEN; PET; PVDF | 公式+极性在network中出现 |
| PPS | 6 | 3 | 22.9894 | + | Na⁺ | Na | 95 | 0 |  | 0 |  | network未出现 |
| PPS | 7 | 4 | 56.9808 | - | C₂HS⁻ | C2HS | 100 | 0 |  | 0 |  | network未出现 |
| PPS | 8 | 4 | 300.7691 | + | I₂OP⁺ | I2OP | 30 | 0 |  | 0 |  | network未出现 |
| PPS | 9 | 5 | 49.0086 | - | C₄H⁻ | C4H | 100 | 5 | COC; EVA; PET; POMC; POMH | 5 | COC; EVA; PET; POMC; POMH | 公式+极性在network中出现 |
| PPS | 10 | 5 | 41.0385 | + | C₃H₅⁺ | C3H5 | 100 | 6 | COC; EVA; PEI; PET; POMC; POMH | 7 | COC; ETFE; EVA; PEI; PET; POMC; POMH | 公式+极性在network中出现 |
| PTFE | 1 | 1 | 19.0010 | - | F⁻ | F | 15 | 0 |  | 3 | ETFE; PTFE; PVDF | 公式在network中出现但极性未对应 |
| PTFE | 2 | 1 | 69.0023 | + | C₃HO₂⁺ | C3HO2 | 100 | 4 | EVA; PET; POMC; POMH | 5 | EVA; PEN; PET; POMC; POMH | 公式+极性在network中出现 |
| PTFE | 3 | 2 | 31.0009 | + | H₃Si⁺ | H3Si | 32 | 1 | PDMS | 1 | PDMS | 公式+极性在network中出现 |
| PTFE | 4 | 2 | 1.0086 | - | H⁻ | H | 100 | 0 |  | 8 | EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |
| PTFE | 5 | 3 | 130.9965 | + | C₅H₄ClO₂⁺ | C5H4ClO2 | 67 | 0 |  | 0 |  | network未出现 |
| PTFE | 6 | 3 | 37.9970 | - | F₂⁻ | F2 | 73 | 0 |  | 3 | ETFE; PTFE; PVDF | 公式在network中出现但极性未对应 |
| PTFE | 7 | 4 | 92.9976 | + | C₅HO₂⁺ | C5HO2 | 100 | 4 | EVA; PET; POMC; POMH | 6 | EVA; PEEK; PEEK20%GFR; PET; POMC; POMH | 公式+极性在network中出现 |
| PTFE | 8 | 4 | 68.9953 | - | CF₃⁻ | CF3 | 100 | 3 | FEP; PFA; PTFE | 4 | ETFE; FEP; PFA; PTFE | 公式+极性在network中出现 |
| PTFE | 9 | 5 | 132.9069 | + | Cs⁺ | Cs | 86 | 0 |  | 0 |  | network未出现 |
| PTFE | 10 | 5 | 42.9985 | - | C₂F⁻ | C2F | 86 | 0 |  | 2 | ETFE; PVDF | 公式在network中出现但极性未对应 |
| PVDF | 1 | 1 | 19.0007 | - | F⁻ | F | 100 | 0 |  | 3 | ETFE; PTFE; PVDF | 公式在network中出现但极性未对应 |
| PVDF | 2 | 1 | 113.0019 | + | C₈HO⁺ | C8HO | 66 | 4 | EVA; PET; POMC; POMH | 5 | EVA; Nomex; PET; POMC; POMH | 公式+极性在network中出现 |
| PVDF | 3 | 2 | 39.0088 | - | F₂H⁻ | F2H | 91 | 0 |  | 0 |  | network未出现 |
| PVDF | 4 | 2 | 133.0066 | + | C₁₁H⁺ | C11H | 78 | 5 | COC; EVA; PET; POMC; POMH | 5 | COC; EVA; PET; POMC; POMH | 公式+极性在network中出现 |
| PVDF | 5 | 3 | 1.0084 | - | H⁻ | H | 15 | 0 |  | 8 | EVA; Nomex; PEEK; PEEK20%GFR; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |
| PVDF | 6 | 3 | 68.9990 | + | C₃HO₂⁺ | C3HO2 | 75 | 4 | EVA; PET; POMC; POMH | 5 | EVA; PEN; PET; POMC; POMH | 公式+极性在network中出现 |
| PVDF | 7 | 4 | 95.0113 | + | C₅H₃O₂⁺ | C5H3O2 | 99 | 4 | EVA; PET; POMC; POMH | 6 | EVA; PEEK; PEEK20%GFR; PET; POMC; POMH | 公式+极性在network中出现 |
| PVDF | 8 | 4 | 25.0085 | - | C₂H⁻ | C2H | 100 | 4 | EVA; PEN; PET; PVDF | 7 | COC; ETFE; EVA; PEI; PEN; PET; PVDF | 公式+极性在network中出现 |
| PVDF | 9 | 5 | 77.0208 | + | C₂H₅O₃⁺ | C2H5O3 | 86 | 0 |  | 5 | EVA; PEN; PET; POMC; POMH | 公式在network中出现但极性未对应 |
| PVDF | 10 | 5 | 34.9712 | - | Cl⁻ | Cl | 100 | 0 |  | 0 |  | network未出现 |

## network 筛选后的 RF 前十峰

这一节是建议给实验室人员优先查看的结果。它已经排除了同材料 network 完全无法解释的 RF 峰，并把严格命中和极性缺口分开标记。

### 筛选数量汇总

| material | has_network | rf_peak_rows | network_supported_peak_rows | strict_mode_supported_peak_rows | screened_top10_rows | top10_strict_mode_rows | top10_formula_only_rows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ETFE | True | 896 | 105 | 44 | 10 | 10 | 0 |
| FEP | True | 870 | 25 | 12 | 10 | 10 | 0 |
| Nomex | True | 1014 | 90 | 38 | 10 | 10 | 0 |
| PAI | False | 1067 | 0 | 0 | 0 | 0 | 0 |
| PBI | False | 963 | 0 | 0 | 0 | 0 | 0 |
| PCTFE | False | 796 | 0 | 0 | 0 | 0 | 0 |
| PEEK | True | 1142 | 137 | 58 | 10 | 10 | 0 |
| PEI | True | 1089 | 92 | 33 | 10 | 10 | 0 |
| PEN | True | 884 | 146 | 82 | 10 | 10 | 0 |
| PFA | True | 833 | 47 | 24 | 10 | 10 | 0 |
| PI | True | 1136 | 35 | 15 | 10 | 10 | 0 |
| PPS | True | 973 | 33 | 16 | 10 | 9 | 1 |
| PTFE | True | 967 | 52 | 23 | 10 | 10 | 0 |
| PVDF | True | 909 | 100 | 55 | 10 | 10 | 0 |

### ETFE

| network_screen_rank | network_screen_score | support_class | rank | mz | polarity | rf_formula_raw | normalized_formula | rf_score | relative_intensity | generation_types | network_formula_modes | specificity_compound_count | interpretation_cn |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 103.9030 | strict_specific | 19 | 78.9980 | - | C₂HF₂O⁻ | C2HF2O | 100 | 0.0051 | adduct | negative | 1 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 2 | 102.3080 | strict_specific | 15 | 59.0300 | + | C₃H₄F⁺ | C3H4F | 87 | 0.0066 | adduct | negative; neutral; positive | 1 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 3 | 101.3710 | strict_specific | 56 | 61.9963 | - | C₂F₂⁻ | C2F2 | 100 | 0.0009 | adduct | negative; neutral | 1 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 4 | 100.4060 | strict_specific | 26 | 92.9956 | - | C₃F₃⁻ | C3F3 | 100 | 0.0032 | adduct | negative; neutral | 2 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 5 | 100.3480 | strict_specific | 27 | 97.9973 | - | C₂HF₃O⁻ | C2HF3O | 100 | 0.0030 | adduct | negative | 2 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 6 | 99.5130 | strict_specific | 36 | 109.9986 | - | C₃HF₃O⁻ | C3HF3O | 100 | 0.0016 | adduct | negative | 2 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 7 | 99.0080 | strict_specific | 46 | 80.9953 | - | C₂F₃⁻ | C2F3 | 100 | 0.0012 | adduct | negative; neutral | 2 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 8 | 98.9460 | strict_specific | 48 | 128.9942 | - | C₃HF₄O⁻ | C3HF4O | 100 | 0.0012 | adduct | negative | 2 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 9 | 98.1900 | strict_specific | 60 | 111.0042 | - | C₃H₂F₃O⁻ | C3H2F3O | 100 | 0.0007 | adduct | negative | 2 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 10 | 97.5080 | strict_specific | 74 | 99.0044 | - | C₂H₂F₃O⁻ | C2H2F3O | 100 | 0.0004 | adduct | negative | 2 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |

### FEP

| network_screen_rank | network_screen_score | support_class | rank | mz | polarity | rf_formula_raw | normalized_formula | rf_score | relative_intensity | generation_types | network_formula_modes | specificity_compound_count | interpretation_cn |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 100.7630 | strict_specific | 2 | 69.0002 | - | CF₃⁻ | CF3 | 100 | 0.0403 | adduct | negative; neutral | 3 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 2 | 95.1630 | strict_specific | 50 | 204.9806 | - | C₃HClF₇⁻ | C3HClF7 | 100 | 0.0005 | adduct | negative | 3 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 3 | 95.0740 | strict_specific | 53 | 84.9957 | - | CF₃O⁻ | CF3O | 100 | 0.0004 | adduct | negative | 3 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 4 | 94.2090 | strict_specific | 72 | 170.0001 | - | C₃HF₇⁻ | C3HF7 | 100 | 0.0003 | adduct | negative; neutral; positive | 3 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 5 | 92.7360 | strict_specific | 55 | 70.0020 | - | ¹³CF₃⁻ | CF3 | 85 | 0.0004 | adduct | negative; neutral | 3 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 6 | 91.7540 | strict_specific | 63 | 99.9946 | - | C₂F₄⁻ | C2F4 | 100 | 0.0003 | adduct | negative; neutral | 4 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 7 | 90.3480 | strict_common | 39 | 50.0016 | - | CF₂⁻ | CF2 | 100 | 0.0010 | adduct | negative; neutral | 5 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 8 | 89.5940 | strict_specific | 243 | 165.9903 | - | C₃F₆O⁻ | C3F6O | 100 | 0.0000 | adduct | negative | 3 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 9 | 88.6800 | strict_common | 10 | 67.0019 | - | CHF₂O⁻ | CHF2O | 73 | 0.0054 | adduct | negative | 5 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 10 | 87.5710 | strict_common | 42 | 51.0028 | + | CHF₂⁺ | CHF2 | 77 | 0.0020 | adduct | negative; neutral; positive | 5 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |

### Nomex

| network_screen_rank | network_screen_score | support_class | rank | mz | polarity | rf_formula_raw | normalized_formula | rf_score | relative_intensity | generation_types | network_formula_modes | specificity_compound_count | interpretation_cn |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 106.6730 | strict_specific | 3 | 42.0002 | - | CNO⁻ | CNO | 100 | 0.0492 | adduct | negative; neutral | 1 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 2 | 99.8510 | strict_specific | 37 | 90.0269 | - | C₆H₄N⁻ | C6H4N | 82 | 0.0020 | adduct | negative; neutral; positive | 1 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 3 | 95.8230 | strict_specific | 42 | 92.0500 | + | C₆H₆N⁺ | C6H6N | 56 | 0.0019 | adduct | negative; neutral; positive | 1 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 4 | 95.2120 | strict_specific | 132 | 92.0422 | - | C₆H₆N⁻ | C6H6N | 75 | 0.0003 | adduct | negative; neutral; positive | 1 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 5 | 94.5730 | strict_specific | 50 | 90.0386 | + | C₆H₄N⁺ | C6H4N | 50 | 0.0016 | adduct | negative; neutral; positive | 1 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 6 | 94.4830 | strict_specific | 209 | 44.0120 | - | CH₂NO⁻ | CH2NO | 84 | 0.0002 | adduct | negative; neutral; positive | 1 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 7 | 94.1390 | strict_specific | 58 | 93.0575 | + | C₆H₇N⁺ | C6H7N | 49 | 0.0014 | adduct | neutral; positive | 1 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 8 | 93.7620 | strict_specific | 188 | 57.9988 | - | CNO₂⁻ | CNO2 | 76 | 0.0002 | adduct | negative | 1 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 9 | 93.3280 | strict_specific | 108 | 44.0146 | + | CH₂NO⁺ | CH2NO | 55 | 0.0007 | adduct | negative; neutral; positive | 1 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 10 | 92.4320 | strict_specific | 129 | 94.0612 | + | C₆H₈N⁺ | C6H8N | 53 | 0.0006 | adduct | neutral; positive | 1 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |

### PEEK

| network_screen_rank | network_screen_score | support_class | rank | mz | polarity | rf_formula_raw | normalized_formula | rf_score | relative_intensity | generation_types | network_formula_modes | specificity_compound_count | interpretation_cn |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 90.3050 | strict_specific | 156 | 289.0847 | + | C₁₉H₁₃O₃⁺ | C19H13O3 | 63 | 0.0004 | adduct | negative; neutral; positive | 2 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 2 | 89.5000 | strict_specific | 172 | 289.0831 | - | C₁₉H₁₃O₃⁻ | C19H13O3 | 63 | 0.0002 | adduct | negative; neutral; positive | 2 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 3 | 88.8240 | strict_specific | 218 | 305.0777 | - | C₁₉H₁₃O₄⁻ | C19H13O4 | 67 | 0.0001 | adduct | negative; neutral; positive | 2 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 4 | 87.7240 | strict_common | 22 | 121.0311 | + | C₇H₅O₂⁺ | C7H5O2 | 90 | 0.0037 | adduct | negative; neutral; positive | 6 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 5 | 86.8960 | strict_specific | 416 | 305.0827 | + | C₁₉H₁₃O₄⁺ | C19H13O4 | 83 | 0.0001 | adduct | negative; neutral; positive | 2 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 6 | 85.5600 | strict_common | 34 | 105.0340 | + | C₇H₅O⁺ | C7H5O | 100 | 0.0022 | adduct | negative; neutral; positive | 7 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 7 | 85.4320 | strict_specific | 461 | 317.0781 | + | C₂₀H₁₃O₄⁺ | C20H13O4 | 80 | 0.0001 | adduct | negative; neutral; positive | 2 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 8 | 85.2880 | strict_common | 5 | 73.0081 | - | C₆H⁻ | C6H | 100 | 0.0142 | adduct | negative; neutral | 12 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 9 | 85.2350 | strict_common | 127 | 29.0015 | + | CHO⁺ | CHO | 100 | 0.0006 | adduct | negative; neutral; positive | 6 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 10 | 85.1980 | strict_common | 32 | 104.0272 | + | C₇H₄O⁺ | C7H4O | 97 | 0.0023 | adduct | negative; neutral; positive | 7 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |

### PEI

| network_screen_rank | network_screen_score | support_class | rank | mz | polarity | rf_formula_raw | normalized_formula | rf_score | relative_intensity | generation_types | network_formula_modes | specificity_compound_count | interpretation_cn |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 98.1680 | strict_specific | 43 | 139.0502 | + | C₉H₈Na⁺ | C9H8Na | 72 | 0.0019 | adduct | positive | 1 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 2 | 91.8970 | strict_common | 1 | 41.0396 | + | C₃H₅⁺ | C3H5 | 100 | 0.0302 | adduct | negative; neutral; positive | 6 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 3 | 91.1470 | strict_common | 3 | 43.0554 | + | C₃H₇⁺ | C3H7 | 100 | 0.0156 | adduct | negative; neutral; positive | 6 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 4 | 89.3780 | strict_common | 72 | 133.0688 | - | C₉H₉O⁻ | C9H9O | 100 | 0.0007 | adduct | negative; neutral; positive | 5 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 5 | 89.0580 | strict_common | 26 | 42.0440 | + | C₃H₆⁺ | C3H6 | 100 | 0.0034 | adduct | negative; neutral; positive | 6 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 6 | 87.8140 | strict_common | 119 | 57.0359 | - | C₃H₅O⁻ | C3H5O | 100 | 0.0003 | adduct | negative | 5 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 7 | 87.3820 | strict_common | 53 | 39.0235 | - | C₃H₃⁻ | C3H3 | 100 | 0.0011 | adduct | negative; neutral | 6 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 8 | 86.6610 | strict_common | 52 | 117.0609 | + | C₉H₉⁺ | C9H9 | 93 | 0.0015 | adduct | negative; neutral; positive | 6 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 9 | 84.9560 | strict_common | 244 | 135.0842 | + | C₉H₁₁O⁺ | C9H11O | 100 | 0.0002 | adduct | negative; neutral; positive | 5 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 10 | 84.8230 | strict_common | 136 | 119.0892 | + | C₉H₁₁⁺ | C9H11 | 100 | 0.0004 | adduct | negative; neutral; positive | 6 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |

### PEN

| network_screen_rank | network_screen_score | support_class | rank | mz | polarity | rf_formula_raw | normalized_formula | rf_score | relative_intensity | generation_types | network_formula_modes | specificity_compound_count | interpretation_cn |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 98.9390 | strict_specific | 94 | 243.0674 | + | C₁₄H₁₁O₄⁺ | C14H11O4 | 88 | 0.0010 | adduct | negative; neutral; positive | 1 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 2 | 98.7420 | strict_specific | 2 | 25.0090 | - | C₂H⁻ | C2H | 100 | 0.0872 | adduct | negative; neutral | 4 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 3 | 98.6120 | strict_specific | 16 | 41.0038 | - | C₂HO⁻ | C2HO | 100 | 0.0071 | adduct | negative; neutral | 3 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 4 | 96.9800 | strict_specific | 37 | 43.0182 | + | C₂H₃O⁺ | C2H3O | 100 | 0.0023 | adduct | negative; neutral; positive | 3 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 5 | 96.0590 | strict_specific | 9 | 27.0227 | + | C₂H₃⁺ | C2H3 | 100 | 0.0083 | adduct | negative; neutral; positive | 4 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 6 | 93.4400 | strict_specific | 291 | 244.0702 | + | ¹³CC₁₃H₁₁O₄⁺ | C14H11O4 | 88 | 0.0002 | adduct | negative; neutral; positive | 1 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 7 | 93.3130 | strict_specific | 173 | 289.0774 | + | C₁₅H₁₃O₆⁺ | C15H13O6 | 67 | 0.0004 | adduct | negative; neutral; positive | 1 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 8 | 92.8260 | strict_common | 13 | 155.0485 | + | C₁₁H₇O⁺ | C11H7O | 100 | 0.0063 | adduct | negative; neutral; positive | 5 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 9 | 91.8150 | strict_specific | 77 | 31.0195 | - | CH₃O⁻ | CH3O | 100 | 0.0005 | adduct | negative; neutral; positive | 4 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 10 | 91.8110 | strict_specific | 37 | 26.0117 | - | ¹³CCH⁻ | C2H | 85 | 0.0021 | adduct | negative; neutral | 4 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |

### PFA

| network_screen_rank | network_screen_score | support_class | rank | mz | polarity | rf_formula_raw | normalized_formula | rf_score | relative_intensity | generation_types | network_formula_modes | specificity_compound_count | interpretation_cn |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 100.3430 | strict_specific | 5 | 68.9957 | - | CF₃⁻ | CF3 | 100 | 0.0289 | adduct | negative; neutral | 3 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 2 | 96.5930 | strict_specific | 26 | 84.9904 | - | CF₃O⁻ | CF3O | 100 | 0.0013 | adduct | negative | 3 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 3 | 95.8450 | strict_specific | 98 | 254.9856 | - | C₄HF₁₀O⁻ | C4HF10O | 100 | 0.0001 | adduct | negative | 2 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 4 | 95.7490 | strict_specific | 40 | 85.9956 | - | CHF₃O⁻ | CHF3O | 100 | 0.0007 | adduct | negative | 3 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 5 | 94.6110 | strict_specific | 60 | 219.0020 | - | C₄H₃F₈O⁻ | C4H3F8O | 100 | 0.0003 | adduct | negative | 3 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 6 | 93.0260 | strict_specific | 39 | 116.9926 | - | C₂HF₄O⁻ | C2HF4O | 100 | 0.0008 | adduct | negative | 4 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 7 | 92.6670 | strict_specific | 108 | 165.9863 | - | C₃F₆O⁻ | C3F6O | 100 | 0.0001 | adduct | negative | 3 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 8 | 92.3980 | strict_specific | 59 | 69.9979 | - | ¹³CF₃⁻ | CF3 | 85 | 0.0003 | adduct | negative; neutral | 3 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 9 | 92.1840 | strict_common | 13 | 66.9978 | - | CHF₂O⁻ | CHF2O | 100 | 0.0034 | adduct | negative | 5 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 10 | 91.7150 | strict_specific | 61 | 99.9923 | - | C₂F₄⁻ | C2F4 | 100 | 0.0003 | adduct | negative; neutral | 4 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |

### PI

| network_screen_rank | network_screen_score | support_class | rank | mz | polarity | rf_formula_raw | normalized_formula | rf_score | relative_intensity | generation_types | network_formula_modes | specificity_compound_count | interpretation_cn |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 84.8180 | strict_common | 9 | 73.0079 | - | C₆H⁻ | C6H | 100 | 0.0099 | adduct | negative; neutral | 12 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 2 | 82.9780 | strict_common | 26 | 89.0074 | - | C₆HO⁻ | C6HO | 100 | 0.0024 | adduct | negative; neutral | 8 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 3 | 82.9350 | strict_common | 21 | 77.0379 | + | C₆H₅⁺ | C6H5 | 100 | 0.0021 | adduct | negative; neutral; positive | 13 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 4 | 82.2790 | strict_common | 32 | 75.0226 | + | C₆H₃⁺ | C6H3 | 100 | 0.0014 | adduct | negative; neutral; positive | 12 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 5 | 81.8990 | strict_common | 41 | 79.0536 | + | C₆H₇⁺ | C6H7 | 100 | 0.0011 | adduct | positive | 13 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 6 | 81.7590 | strict_common | 49 | 75.0237 | - | C₆H₃⁻ | C6H3 | 100 | 0.0011 | adduct | negative; neutral; positive | 13 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 7 | 80.3330 | strict_common | 56 | 76.0285 | + | C₆H₄⁺ | C6H4 | 94 | 0.0008 | adduct | negative; neutral; positive | 13 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 8 | 80.0240 | strict_common | 63 | 78.0432 | + | C₆H₆⁺ | C6H6 | 94 | 0.0006 | adduct | neutral; positive | 13 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 9 | 79.9590 | strict_common | 94 | 91.0205 | - | C₆H₃O⁻ | C6H3O | 100 | 0.0004 | adduct | negative; neutral; positive | 12 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 10 | 76.5130 | strict_common | 216 | 93.0343 | - | C₆H₅O⁻ | C6H5O | 100 | 0.0001 | adduct | negative; neutral; positive | 12 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |

### PPS

| network_screen_rank | network_screen_score | support_class | rank | mz | polarity | rf_formula_raw | normalized_formula | rf_score | relative_intensity | generation_types | network_formula_modes | specificity_compound_count | interpretation_cn |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 100.9620 | strict_specific | 16 | 140.9790 | - | C₆H₅S₂⁻ | C6H5S2 | 97 | 0.0067 | adduct | negative; neutral; positive | 2 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 2 | 96.9650 | strict_specific | 61 | 138.9658 | - | C₆H₃S₂⁻ | C6H3S2 | 87 | 0.0015 | adduct | negative; neutral | 2 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 3 | 95.1170 | strict_specific | 156 | 142.9945 | - | C₆H₇S₂⁻ | C6H7S2 | 96 | 0.0004 | adduct | negative; neutral; positive | 2 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 4 | 85.4460 | strict_common | 9 | 73.0079 | - | C₆H⁻ | C6H | 100 | 0.0177 | adduct | negative; neutral | 12 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 5 | 84.9600 | strict_specific | 342 | 125.0013 | - | C₆H₅OS⁻ | C6H5OS | 61 | 0.0001 | adduct | negative | 2 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 6 | 82.7760 | strict_common | 16 | 77.0373 | + | C₆H₅⁺ | C6H5 | 100 | 0.0016 | adduct | negative; neutral; positive | 13 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 7 | 82.2950 | strict_common | 21 | 75.0216 | + | C₆H₃⁺ | C6H3 | 100 | 0.0011 | adduct | negative; neutral; positive | 12 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 8 | 81.9830 | formula_only_mode_gap | 10 | 104.9789 | - | C₆HS⁻ | C6HS | 97 | 0.0156 |  | neutral | 2 | 同材料存在该分子式，但当前极性未覆盖，提示 ion rule 或极性分配缺口。 |
| 9 | 80.6370 | strict_common | 96 | 75.0233 | - | C₆H₃⁻ | C6H3 | 100 | 0.0010 | adduct | negative; neutral; positive | 13 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |
| 10 | 80.6310 | strict_common | 61 | 78.0441 | + | C₆H₆⁺ | C6H6 | 100 | 0.0005 | adduct | neutral; positive | 13 | 同材料同极性命中，但跨材料较常见，作为辅助证据。 |

### PTFE

| network_screen_rank | network_screen_score | support_class | rank | mz | polarity | rf_formula_raw | normalized_formula | rf_score | relative_intensity | generation_types | network_formula_modes | specificity_compound_count | interpretation_cn |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 99.7020 | strict_specific | 27 | 80.9933 | - | C₂F₃⁻ | C2F3 | 100 | 0.0016 | adduct | negative; neutral | 2 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 2 | 99.4110 | strict_specific | 4 | 68.9953 | - | CF₃⁻ | CF3 | 100 | 0.0120 | adduct | negative; neutral | 3 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 3 | 98.2700 | strict_specific | 130 | 132.9954 | - | C₃H₂F₅⁻ | C3H2F5 | 100 | 0.0001 | adduct | negative; neutral; positive | 1 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 4 | 95.1610 | strict_specific | 10 | 48.0001 | - | CHFO⁻ | CHFO | 80 | 0.0042 | adduct | negative | 3 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 5 | 94.4990 | strict_specific | 30 | 49.0068 | - | CH₂FO⁻ | CH2FO | 85 | 0.0016 | adduct | negative | 3 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 6 | 94.3730 | strict_specific | 295 | 250.9799 | - | C₅H₄F₉O⁻ | C5H4F9O | 100 | 0.0000 | adduct | negative | 1 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 7 | 94.2900 | strict_specific | 299 | 381.9844 | - | C₈HF₁₅⁻ | C8HF15 | 100 | 0.0000 | adduct | negative; neutral; positive | 1 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 8 | 93.3870 | strict_specific | 342 | 149.9927 | - | C₃H₃F₅O⁻ | C3H3F5O | 100 | 0.0000 | adduct | negative | 1 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 9 | 93.1640 | strict_specific | 220 | 81.9964 | - | C₂HF₃⁻ | C2HF3 | 100 | 0.0000 | adduct | negative; neutral; positive | 2 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 10 | 93.0590 | strict_specific | 112 | 69.9989 | - | CHF₃⁻ | CHF3 | 100 | 0.0002 | adduct | negative; neutral; positive | 3 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |

### PVDF

| network_screen_rank | network_screen_score | support_class | rank | mz | polarity | rf_formula_raw | normalized_formula | rf_score | relative_intensity | generation_types | network_formula_modes | specificity_compound_count | interpretation_cn |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 102.1050 | strict_specific | 31 | 61.0079 | - | C₂H₂FO⁻ | C2H2FO | 97 | 0.0018 | adduct | negative | 1 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 2 | 99.3440 | strict_specific | 36 | 92.9962 | - | C₃F₃⁻ | C3F3 | 100 | 0.0014 | adduct | negative; neutral | 2 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 3 | 98.9810 | strict_specific | 43 | 109.9980 | - | C₃HF₃O⁻ | C3HF3O | 100 | 0.0011 | adduct | negative | 2 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 4 | 98.5280 | strict_specific | 53 | 111.0071 | - | C₃H₂F₃O⁻ | C3H2F3O | 100 | 0.0009 | adduct | negative | 2 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 5 | 98.5070 | strict_specific | 8 | 48.0011 | - | CHFO⁻ | CHFO | 98 | 0.0074 | adduct | negative | 3 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 6 | 97.9260 | strict_specific | 66 | 128.9978 | - | C₃HF₄O⁻ | C3HF4O | 100 | 0.0006 | adduct | negative | 2 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 7 | 97.2100 | strict_specific | 128 | 47.0278 | + | C₂H₄F⁺ | C2H4F | 82 | 0.0009 | adduct | negative; neutral; positive | 1 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 8 | 97.1550 | strict_specific | 67 | 80.0054 | - | C₂H₂F₂O⁻ | C2H2F2O | 95 | 0.0006 | adduct | negative | 2 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 9 | 96.5110 | strict_specific | 106 | 63.0050 | - | C₂HF₂⁻ | C2HF2 | 100 | 0.0003 | adduct | negative; neutral | 2 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |
| 10 | 96.3500 | strict_specific | 4 | 25.0085 | - | C₂H⁻ | C2H | 100 | 0.0099 | adduct | negative; neutral | 4 | 同材料同极性命中，且跨材料较少，优先作为材料相关峰。 |

## A/B 级筛选公式

### ETFE

| screening_tier | normalized_formula | polarity | best_rf_score | relative_intensity | best_rank | generation_types | all_network_compound_count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A_高置信特征 | C2HF2O | - | 100 | 0.0051 | 19 | adduct | 1 |
| A_高置信特征 | C3F3 | - | 100 | 0.0033 | 26 | adduct | 2 |
| A_高置信特征 | C2HF3O | - | 100 | 0.0030 | 27 | adduct | 2 |
| A_高置信特征 | C2HF4O | - | 100 | 0.0029 | 29 | adduct | 4 |
| A_高置信特征 | C3HF3O | - | 100 | 0.0016 | 36 | adduct | 2 |
| A_高置信特征 | CF | - | 100 | 0.0014 | 40 | adduct | 3 |
| A_高置信特征 | C2F3 | - | 100 | 0.0012 | 46 | adduct | 2 |
| A_高置信特征 | C3HF4O | - | 100 | 0.0012 | 48 | adduct | 2 |
| A_高置信特征 | C2F2 | - | 100 | 0.0009 | 56 | adduct | 1 |
| A_高置信特征 | C3H2F3O | - | 100 | 0.0007 | 60 | adduct | 2 |
| A_高置信特征 | C2H2F3O | - | 100 | 0.0004 | 74 | adduct | 2 |
| A_高置信特征 | C2HF2 | - | 100 | 0.0003 | 86 | adduct | 2 |
| A_高置信特征 | C3H4F | + | 89 | 0.0068 | 15 | adduct | 1 |
| A_高置信特征 | CHFO | - | 86 | 0.0087 | 5 | adduct | 3 |
| A_高置信特征 | CH2F | + | 86 | 0.0043 | 24 | adduct | 3 |
| B_可用支持 | CHF2O | - | 100 | 0.0074 | 9 | adduct | 5 |
| B_可用支持 | C2H5 | + | 100 | 0.0025 | 56 | adduct | 6 |
| B_可用支持 | CF2 | - | 100 | 0.0003 | 97 | adduct | 5 |
| B_可用支持 | C2H2F4O | - | 100 | 0.0002 | 111 | adduct | 4 |
| B_可用支持 | C3H2F4O | - | 100 | 0.0001 | 135 | adduct | 2 |

### FEP

| screening_tier | normalized_formula | polarity | best_rf_score | relative_intensity | best_rank | generation_types | all_network_compound_count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A_高置信特征 | CF3 | - | 100 | 0.0408 | 2 | adduct | 3 |
| A_高置信特征 | C3HClF7 | - | 100 | 0.0005 | 50 | adduct | 3 |
| A_高置信特征 | CF3O | - | 100 | 0.0004 | 53 | adduct | 3 |
| A_高置信特征 | C2F4 | - | 100 | 0.0003 | 63 | adduct | 4 |
| A_高置信特征 | C3HF7 | - | 100 | 0.0003 | 72 | adduct | 3 |
| B_可用支持 | CF2 | - | 100 | 0.0010 | 39 | adduct | 5 |
| B_可用支持 | C3F6O | - | 100 | 0.0000 | 243 | adduct | 3 |
| B_可用支持 | C2HF4 | - | 85 | 0.0000 | 311 | adduct | 4 |
| B_可用支持 | CHF2 | + | 77 | 0.0020 | 42 | adduct | 5 |
| B_可用支持 | CHF2O | - | 73 | 0.0054 | 10 | adduct | 5 |

### Nomex

| screening_tier | normalized_formula | polarity | best_rf_score | relative_intensity | best_rank | generation_types | all_network_compound_count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A_高置信特征 | CNO | - | 100 | 0.0492 | 3 | adduct | 1 |
| A_高置信特征 | C6H4N | - | 82 | 0.0020 | 37 | adduct | 1 |
| B_可用支持 | CHO | + | 96 | 0.0005 | 141 | adduct | 6 |
| B_可用支持 | C7H3O | - | 90 | 0.0003 | 138 | adduct | 7 |
| B_可用支持 | CH2NO | - | 84 | 0.0002 | 209 | adduct | 1 |
| B_可用支持 | C8H5O2 | - | 82 | 0.0026 | 30 | adduct | 5 |
| B_可用支持 | C7H5O | - | 81 | 0.0003 | 134 | adduct | 7 |
| B_可用支持 | CNO2 | - | 76 | 0.0002 | 188 | adduct | 1 |
| B_可用支持 | C6H6N | - | 75 | 0.0003 | 132 | adduct | 1 |
| B_可用支持 | C6H7ClN | - | 70 | 0.0001 | 259 | adduct | 1 |
| B_可用支持 | C7H4O | - | 59 | 0.0004 | 109 | adduct | 7 |
| B_可用支持 | C6H6N | + | 56 | 0.0019 | 42 | adduct | 1 |
| B_可用支持 | C7H5O | + | 55 | 0.0057 | 14 | adduct | 7 |
| B_可用支持 | CH2NO | + | 55 | 0.0007 | 108 | adduct | 1 |
| B_可用支持 | C7H6O | - | 55 | 0.0004 | 110 | adduct | 6 |
| B_可用支持 | C7HO | - | 55 | 0.0004 | 121 | adduct | 7 |
| B_可用支持 | C6H8N | + | 53 | 0.0006 | 129 | adduct | 1 |
| B_可用支持 | C6H4N | + | 50 | 0.0016 | 50 | adduct | 1 |
| B_可用支持 | CClO | - | 50 | 0.0005 | 97 | adduct | 6 |
| B_可用支持 | CH4NO | + | 50 | 0.0000 | 541 | adduct | 1 |

### PAI

无 A/B 级公式。

### PBI

无 A/B 级公式。

### PCTFE

无 A/B 级公式。

### PEEK

| screening_tier | normalized_formula | polarity | best_rf_score | relative_intensity | best_rank | generation_types | all_network_compound_count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B_可用支持 | C7H5O | + | 100 | 0.0022 | 34 | adduct | 7 |
| B_可用支持 | CHO | + | 100 | 0.0006 | 127 | adduct | 6 |
| B_可用支持 | C7H3O | + | 100 | 0.0005 | 140 | adduct | 7 |
| B_可用支持 | C7H3O2 | + | 100 | 0.0003 | 186 | adduct | 6 |
| B_可用支持 | C7H5O | - | 100 | 0.0002 | 191 | adduct | 7 |
| B_可用支持 | C7H4O | + | 97 | 0.0023 | 32 | adduct | 7 |
| B_可用支持 | C13H9O3 | - | 92 | 0.0010 | 77 | adduct | 7 |
| B_可用支持 | C7H7O | + | 91 | 0.0005 | 151 | adduct | 7 |
| B_可用支持 | C7H6O | + | 91 | 0.0002 | 224 | adduct | 7 |
| B_可用支持 | C7H5O2 | + | 90 | 0.0037 | 22 | adduct | 6 |
| B_可用支持 | C7H3O | - | 85 | 0.0002 | 177 | adduct | 7 |
| B_可用支持 | C7H4O2 | + | 84 | 0.0002 | 294 | adduct | 6 |
| B_可用支持 | C7H3O2 | - | 84 | 0.0001 | 259 | adduct | 7 |
| B_可用支持 | C6H5O2 | + | 83 | 0.0002 | 223 | adduct | 6 |
| B_可用支持 | C19H13O4 | + | 83 | 0.0001 | 416 | adduct | 2 |
| B_可用支持 | C20H13O4 | + | 80 | 0.0001 | 461 | adduct | 2 |
| B_可用支持 | C13H9O2 | - | 73 | 0.0008 | 76 | adduct | 7 |
| B_可用支持 | CO2 | - | 71 | 0.0004 | 114 | adduct | 6 |
| B_可用支持 | C12H7O3 | - | 68 | 0.0001 | 248 | adduct | 7 |
| B_可用支持 | C19H13O4 | - | 67 | 0.0001 | 218 | adduct | 2 |

### PEI

| screening_tier | normalized_formula | polarity | best_rf_score | relative_intensity | best_rank | generation_types | all_network_compound_count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A_高置信特征 | C9H8Na | + | 72 | 0.0019 | 43 | adduct | 1 |
| B_可用支持 | C3H5 | + | 100 | 0.0302 | 1 | adduct | 6 |
| B_可用支持 | C3H7 | + | 100 | 0.0163 | 3 | adduct | 6 |
| B_可用支持 | C3H6 | + | 100 | 0.0034 | 26 | adduct | 6 |
| B_可用支持 | C3H3 | - | 100 | 0.0011 | 53 | adduct | 6 |
| B_可用支持 | C9H9O | - | 100 | 0.0008 | 72 | adduct | 5 |
| B_可用支持 | C9H11 | + | 100 | 0.0004 | 136 | adduct | 6 |
| B_可用支持 | C3H5O | - | 100 | 0.0003 | 119 | adduct | 5 |
| B_可用支持 | C9H11O | + | 100 | 0.0002 | 244 | adduct | 5 |
| B_可用支持 | C9H13 | + | 100 | 0.0001 | 327 | adduct | 6 |
| B_可用支持 | C9H10 | + | 94 | 0.0003 | 198 | adduct | 6 |
| B_可用支持 | C9H9 | + | 93 | 0.0015 | 52 | adduct | 6 |
| B_可用支持 | C9H12O | + | 70 | 0.0000 | 551 | adduct | 5 |
| B_可用支持 | C8H6O3 | + | 52 | 0.0008 | 87 | adduct | 5 |

### PEN

| screening_tier | normalized_formula | polarity | best_rf_score | relative_intensity | best_rank | generation_types | all_network_compound_count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A_高置信特征 | C2H | - | 100 | 0.0894 | 2 | adduct | 4 |
| A_高置信特征 | C2H3 | + | 100 | 0.0083 | 9 | adduct | 4 |
| A_高置信特征 | C2HO | - | 100 | 0.0073 | 16 | adduct | 3 |
| A_高置信特征 | C2H3O | + | 100 | 0.0023 | 37 | adduct | 3 |
| A_高置信特征 | CH3O | - | 100 | 0.0005 | 77 | adduct | 4 |
| A_高置信特征 | C14H11O4 | + | 88 | 0.0012 | 94 | adduct | 1 |
| B_可用支持 | C11H7O | + | 100 | 0.0072 | 13 | adduct | 5 |
| B_可用支持 | C2H5 | + | 100 | 0.0065 | 12 | adduct | 6 |
| B_可用支持 | C2H5O | + | 100 | 0.0017 | 57 | adduct | 5 |
| B_可用支持 | C3HO2 | - | 100 | 0.0013 | 48 | adduct | 5 |
| B_可用支持 | C10H9 | + | 100 | 0.0013 | 88 | adduct | 6 |
| B_可用支持 | CHO | + | 100 | 0.0012 | 84 | adduct | 6 |
| B_可用支持 | C10H7 | - | 100 | 0.0010 | 55 | adduct | 6 |
| B_可用支持 | C10H7O | - | 100 | 0.0004 | 84 | adduct | 5 |
| B_可用支持 | C3H3O2 | - | 100 | 0.0003 | 89 | adduct | 5 |
| B_可用支持 | C2H3 | - | 100 | 0.0002 | 128 | adduct | 6 |
| B_可用支持 | C2H3O2 | + | 100 | 0.0001 | 370 | adduct | 3 |
| B_可用支持 | C3H3O2 | + | 100 | 0.0001 | 378 | adduct | 5 |
| B_可用支持 | C2HO2 | - | 100 | 0.0000 | 237 | adduct | 3 |
| B_可用支持 | CH3O2 | + | 100 | 0.0000 | 519 | adduct | 3 |

### PFA

| screening_tier | normalized_formula | polarity | best_rf_score | relative_intensity | best_rank | generation_types | all_network_compound_count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A_高置信特征 | CF3 | - | 100 | 0.0292 | 5 | adduct | 3 |
| A_高置信特征 | CF3O | - | 100 | 0.0013 | 26 | adduct | 3 |
| A_高置信特征 | C2HF4O | - | 100 | 0.0008 | 39 | adduct | 4 |
| A_高置信特征 | CHF3O | - | 100 | 0.0007 | 40 | adduct | 3 |
| A_高置信特征 | C4H3F8O | - | 100 | 0.0003 | 60 | adduct | 3 |
| A_高置信特征 | C2F4 | - | 100 | 0.0003 | 61 | adduct | 4 |
| A_高置信特征 | C4HF10O | - | 100 | 0.0001 | 98 | adduct | 2 |
| B_可用支持 | CHF2O | - | 100 | 0.0034 | 13 | adduct | 5 |
| B_可用支持 | CF2 | - | 100 | 0.0009 | 36 | adduct | 5 |
| B_可用支持 | C3F6O | - | 100 | 0.0001 | 108 | adduct | 3 |
| B_可用支持 | C3F6 | - | 100 | 0.0000 | 176 | adduct | 3 |
| B_可用支持 | C7HF14O | - | 100 | 0.0000 | 207 | adduct | 3 |
| B_可用支持 | C2F4O | - | 100 | 0.0000 | 210 | adduct | 4 |
| B_可用支持 | C2HF4 | - | 100 | 0.0000 | 225 | adduct | 4 |
| B_可用支持 | C4HF9 | - | 100 | 0.0000 | 226 | adduct | 3 |
| B_可用支持 | C4F8O | - | 100 | 0.0000 | 252 | adduct | 3 |
| B_可用支持 | C3HF6 | - | 100 | 0.0000 | 254 | adduct | 3 |
| B_可用支持 | C4F8 | - | 100 | 0.0000 | 271 | adduct | 3 |
| B_可用支持 | C9F19 | - | 100 | 0.0000 | 285 | adduct | 3 |
| B_可用支持 | CF2O | - | 80 | 0.0000 | 255 | adduct | 5 |

### PI

无 A/B 级公式。

### PPS

| screening_tier | normalized_formula | polarity | best_rf_score | relative_intensity | best_rank | generation_types | all_network_compound_count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A_高置信特征 | C6H5S2 | - | 97 | 0.0067 | 16 | adduct | 2 |
| A_高置信特征 | C6H3S2 | - | 87 | 0.0015 | 61 | adduct | 2 |
| B_可用支持 | C6H7S2 | - | 96 | 0.0004 | 156 | adduct | 2 |
| B_可用支持 | C6H5OS | - | 61 | 0.0001 | 342 | adduct | 2 |

### PTFE

| screening_tier | normalized_formula | polarity | best_rf_score | relative_intensity | best_rank | generation_types | all_network_compound_count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A_高置信特征 | CF3 | - | 100 | 0.0120 | 4 | adduct | 3 |
| A_高置信特征 | C2F3 | - | 100 | 0.0016 | 27 | adduct | 2 |
| A_高置信特征 | CH2FO | - | 85 | 0.0016 | 30 | adduct | 3 |
| A_高置信特征 | CHFO | - | 80 | 0.0042 | 10 | adduct | 3 |
| B_可用支持 | CHF2O | - | 100 | 0.0040 | 11 | adduct | 5 |
| B_可用支持 | CHF3 | - | 100 | 0.0002 | 112 | adduct | 3 |
| B_可用支持 | C3H2F5 | - | 100 | 0.0001 | 130 | adduct | 1 |
| B_可用支持 | C2HF3 | - | 100 | 0.0000 | 220 | adduct | 2 |
| B_可用支持 | C5H4F9O | - | 100 | 0.0000 | 295 | adduct | 1 |
| B_可用支持 | C8HF15 | - | 100 | 0.0000 | 299 | adduct | 1 |
| B_可用支持 | C3H3F5O | - | 100 | 0.0000 | 342 | adduct | 1 |
| B_可用支持 | C9HF17 | - | 100 | 0.0000 | 361 | adduct | 1 |
| B_可用支持 | C7HF15O | - | 100 | 0.0000 | 362 | adduct | 1 |
| B_可用支持 | C6F13O | - | 100 | 0.0000 | 450 | adduct | 3 |
| B_可用支持 | CH2F | + | 85 | 0.0003 | 167 | adduct | 3 |
| B_可用支持 | CFO | - | 83 | 0.0001 | 197 | adduct | 3 |
| B_可用支持 | CHF3O | - | 68 | 0.0008 | 43 | adduct | 3 |
| B_可用支持 | CHF | + | 63 | 0.0010 | 74 | adduct | 3 |
| B_可用支持 | CHF2 | + | 54 | 0.0013 | 56 | adduct | 5 |

### PVDF

| screening_tier | normalized_formula | polarity | best_rf_score | relative_intensity | best_rank | generation_types | all_network_compound_count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A_高置信特征 | C2H | - | 100 | 0.0102 | 4 | adduct | 4 |
| A_高置信特征 | C2H3 | + | 100 | 0.0061 | 20 | adduct | 4 |
| A_高置信特征 | C3F3 | - | 100 | 0.0014 | 36 | adduct | 2 |
| A_高置信特征 | C3HF3O | - | 100 | 0.0011 | 43 | adduct | 2 |
| A_高置信特征 | CF | - | 100 | 0.0009 | 48 | adduct | 3 |
| A_高置信特征 | C3H2F3O | - | 100 | 0.0009 | 53 | adduct | 2 |
| A_高置信特征 | C3HF4O | - | 100 | 0.0006 | 66 | adduct | 2 |
| A_高置信特征 | CHFO | - | 98 | 0.0074 | 8 | adduct | 3 |
| A_高置信特征 | C2H2FO | - | 97 | 0.0018 | 31 | adduct | 1 |
| A_高置信特征 | C2H2F2O | - | 95 | 0.0006 | 67 | adduct | 2 |
| A_高置信特征 | CH2F | + | 88 | 0.0040 | 36 | adduct | 3 |
| B_可用支持 | CHF2O | - | 100 | 0.0055 | 13 | adduct | 5 |
| B_可用支持 | C2H5 | + | 100 | 0.0031 | 47 | adduct | 6 |
| B_可用支持 | C2HF2 | - | 100 | 0.0003 | 106 | adduct | 2 |
| B_可用支持 | C5H2F6 | - | 100 | 0.0001 | 149 | adduct | 2 |
| B_可用支持 | C3H3F4O | - | 100 | 0.0001 | 150 | adduct | 2 |
| B_可用支持 | CF2 | - | 100 | 0.0001 | 151 | adduct | 5 |
| B_可用支持 | C2H3F2O | - | 100 | 0.0001 | 171 | adduct | 2 |
| B_可用支持 | C3H2F4O | - | 100 | 0.0001 | 183 | adduct | 2 |
| B_可用支持 | C3H3F3O | - | 100 | 0.0001 | 240 | adduct | 2 |

## AI生成候选物质排名的提示

AI生成输出中的 `substance_candidates.json` 是基于目录典型碎片的候选物质排序，适合作为人工复核线索，但不能直接等同于纯物质归属。下面列出每个材料排名前三的候选标签：

| material | candidate_rank | label | match_score | matched_count | missing_typical_count |
| --- | --- | --- | --- | --- | --- |
| ETFE | 1 | EVA乙烯-醋酸乙烯 | 1.000 | 4 | 0 |
| ETFE | 2 | 含氟碎片 | 0.750 | 3 | 1 |
| ETFE | 3 | 聚乙烯/聚丙烯碎片 | 0.667 | 4 | 2 |
| FEP | 1 | 含氟碎片 | 1.000 | 4 | 0 |
| FEP | 2 | EVA乙烯-醋酸乙烯 | 1.000 | 4 | 0 |
| FEP | 3 | PTFE聚四氟乙烯 | 0.857 | 6 | 1 |
| Nomex | 1 | 含氮碎片 | 1.000 | 6 | 0 |
| Nomex | 2 | 碳簇阴离子 | 1.000 | 5 | 0 |
| Nomex | 3 | EVA乙烯-醋酸乙烯 | 1.000 | 4 | 0 |
| PAI | 1 | 含氯碎片 | 1.000 | 3 | 0 |
| PAI | 2 | 无机基准碎片 | 0.833 | 5 | 1 |
| PAI | 3 | 含氯污染 | 0.750 | 3 | 1 |
| PBI | 1 | 聚乙烯/聚丙烯碎片 | 1.000 | 6 | 0 |
| PBI | 2 | 含氮碎片 | 0.833 | 5 | 1 |
| PBI | 3 | 碱金属离子 | 0.800 | 4 | 1 |
| PCTFE | 1 | 含氮碎片 | 1.000 | 6 | 0 |
| PCTFE | 2 | 聚乙烯/聚丙烯碎片 | 0.833 | 5 | 1 |
| PCTFE | 3 | PVC含氯聚合物 | 0.800 | 4 | 1 |
| PEEK | 1 | 聚乙烯/聚丙烯碎片 | 0.833 | 5 | 1 |
| PEEK | 2 | 碳簇阴离子 | 0.800 | 4 | 1 |
| PEEK | 3 | PVC含氯聚合物 | 0.800 | 4 | 1 |
| PEI | 1 | 聚乙烯/聚丙烯碎片 | 1.000 | 6 | 0 |
| PEI | 2 | 碳簇阴离子 | 1.000 | 5 | 0 |
| PEI | 3 | PVC含氯聚合物 | 0.800 | 4 | 1 |
| PEN | 1 | 聚乙烯/聚丙烯碎片 | 1.000 | 6 | 0 |
| PEN | 2 | 碳簇阴离子 | 1.000 | 5 | 0 |
| PEN | 3 | 含氯碎片 | 1.000 | 3 | 0 |
| PFA | 1 | 含氮碎片 | 1.000 | 6 | 0 |
| PFA | 2 | 含氟碎片 | 1.000 | 4 | 0 |
| PFA | 3 | EVA乙烯-醋酸乙烯 | 1.000 | 4 | 0 |
| PI | 1 | 聚乙烯/聚丙烯碎片 | 1.000 | 6 | 0 |
| PI | 2 | 含氮碎片 | 1.000 | 6 | 0 |
| PI | 3 | 碳簇阴离子 | 1.000 | 5 | 0 |
| PPS | 1 | 含氮碎片 | 1.000 | 6 | 0 |
| PPS | 2 | 聚乙烯/聚丙烯碎片 | 0.833 | 5 | 1 |
| PPS | 3 | 含硫碎片 | 0.800 | 4 | 1 |
| PTFE | 1 | EVA乙烯-醋酸乙烯 | 1.000 | 4 | 0 |
| PTFE | 2 | ABS苯乙烯三元共聚 | 0.800 | 4 | 1 |
| PTFE | 3 | 含氟碎片 | 0.750 | 3 | 1 |
| PVDF | 1 | 含氮碎片 | 1.000 | 6 | 0 |
| PVDF | 2 | 含氟碎片 | 1.000 | 4 | 0 |
| PVDF | 3 | 聚乙烯/聚丙烯碎片 | 0.833 | 5 | 1 |

## 主要观察

- 含氟材料之间存在大量共享的 `CFx`、`CxFy` 碎片，network 能覆盖不少 RF 公式，但跨材料出现次数较高的公式需要降权。
- PEEK、PPS、PEI、PEN、PI、Nomex 这类芳香/含杂原子聚合物中，碳氢簇和小分子含氧/含氮碎片较多，RF 目录候选容易出现 PE/PP、PVC、ABS 等泛化标签；应优先看同材料 network 命中且跨材料数量较低的公式。
- PAI、PBI、PCTFE 当前没有 network，AI生成输出中出现的有效公式暂时只能作为新增材料建库线索，不能做同材料规则覆盖评价。
- AI生成高分但 network 未覆盖的公式值得分两类处理：如果是合理的材料特征碎片，可以回灌到 rule pack；如果是金属、盐、环境污染或基底峰，应保留为排除/背景标签。
- AI生成候选物质排名目前更像“碎片类别提示”，不是可靠的纯物质判别结果；例如多种材料会被排到 EVA、PE/PP、PVC 或含氮/含氟碎片标签下，因此需要 network 约束和跨材料泛化降权。

## 建议

1. 先把 PAI、PBI、PCTFE 加入 `compounds.csv` 并重建 network，否则这三类材料无法进入同一套筛选口径。
2. 对 A/B 级公式做人工确认后，可按材料类型扩展 rule pack，尤其是含氟聚合物的 `CxFy` 系列与芳香聚合物的特征含杂原子碎片。
3. 对跨材料数量很高的公式建立“泛化碎片降权表”，后续 scoring 不宜把它们作为强材料证据。
4. 对无法解析的 RF 公式扩展一个独立的背景/污染元素表，不建议直接扩大 core formula parser 的元素范围，避免 network 生成空间失控。

## 输出文件

- `outputs/summary/rf_network_comparison/rf_peak_formulas.csv`：RF 峰级公式清洗结果。
- `outputs/summary/rf_network_comparison/rf_network_formula_comparison.csv`：公式-极性级 network 对比明细。
- `outputs/summary/rf_network_comparison/rf_network_summary_by_material.csv`：按材料汇总。
- `outputs/summary/rf_network_comparison/rf_network_screened_formulas.csv`：A/B 级筛选公式。
- `outputs/summary/rf_network_comparison/rf_top10_peaks_network_check.csv`：每个材料 RF rank 前十峰的 network 覆盖检查。
- `outputs/summary/rf_network_comparison/rf_top10_plain_network_presence.csv`：不引入评分的 RF 原始前十峰全 network 归属表。
- `outputs/summary/rf_network_comparison/rf_top10_plain_network_presence_excel.tsv`：朴素归属表的 Excel 友好版本。
- `outputs/summary/rf_network_comparison/rf_network_screened_top10_peaks.csv`：综合 network 支持、材料特异性和 RF 证据后的每材料前十峰。
- `outputs/summary/rf_network_comparison/rf_network_screened_top10_summary.csv`：筛选版前十峰的材料级数量汇总。
- `outputs/summary/rf_network_comparison/rf_network_screened_top10_peaks_excel.tsv`：给 Windows Excel 打开的 UTF-16 制表符版本，优先用于人工查看。
- `outputs/summary/rf_network_comparison/rf_network_screened_top10_summary_excel.tsv`：筛选汇总的 Excel 友好版本。
- `outputs/summary/rf_network_comparison/rf_substance_candidates.csv`：RF 候选物质汇总。
