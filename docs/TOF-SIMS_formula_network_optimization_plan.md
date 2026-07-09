# TOF-SIMS Formula Network 优化方案

## 1. 当前状态概述

当前项目已经完成第一版工程原型：

- 可以解析真实 `data/` 下的 TOF-SIMS txt/TXT 谱图，并输出 `outputs/parsed_spectra/`。
- 可以从 `data/compounds.csv` 中的 SMILES 生成候选分子式网络，并输出 `outputs/networks/`。
- 可以执行 m/z 质量匹配，生成 `outputs/matches/spectrum_mass_matches.csv`。
- 可以为每个谱图生成 Markdown 报告。
- 现有 `unittest` 测试可以通过。

但从当前结果看，项目的主要瓶颈已经不是“能不能跑通”，而是“候选是否可信、是否可解释、是否能真正校准 AI 生成标注输出”。历史文件夹和字段中仍可能保留 `RF` / `rf_` 命名，但这里不再将其理解为 Random Forest。

## 2. 核心不足

### 2.1 全库 m/z 匹配导致假阳性过多

当前 `match_spectrum_by_mass` 会将每个谱图峰与所有 compounds 的所有网络公式直接按质量容差匹配。这样会导致：

- PET 谱图可以匹配到 COC、POMC 等其他材料的母体公式。
- 单个谱图产生数千条匹配记录，人工判读成本高。
- 高分候选不一定来自当前样品对应材料。

这是当前结果可信度的最大风险。

### 2.2 AI 生成候选校准链路尚未真正闭环

当前 `rf_formula_matches.csv` 只有表头，说明流程主要依赖 m/z 匹配，而不是实施方案中设计的：

```text
AI生成候选分子式 ∩ 结构网络生成分子式 = 更可信候选
```

如果后续目标是校准 AI 生成标注输出，必须把候选接入、规范化、评分融合和报告展示做成主链路。

### 2.3 正负离子模式没有参与筛选

网络记录中已有 `ion_mode` 和 `charge`，但匹配阶段没有根据谱图文件名中的 `+`/`-` 或 spectrum_id 中的 `pos/neg` 做过滤。结果中 neutral、positive、negative 候选混在一起，进一步放大候选数量。

### 2.4 化学规则偏宽，低可信公式较多

中性损失目前主要按分子式扣减，不检查官能团或结构上下文。部分小质量公式，如 `H`，也可能作为候选进入质量匹配。这类结果在工程原型阶段可以存在，但不能在最终报告中和高可信候选同等展示。

### 2.5 报告缺少判读所需的聚合指标

当前报告主要展示 Top matched rows。还缺少：

- 按 compound 聚合的解释峰数、解释强度、最高分。
- 未解释高强峰。
- AI 生成候选支持与仅 m/z 支持候选的区分。
- 候选爆炸风险提示。
- 各规则类型的命中统计。

### 2.6 模块边界不够清晰

实施方案中设计了 `fragmentation.py` 和 `ion_rules.py`，但当前主要逻辑集中在 `network.py`。短期可运行，但后续扩展碎片规则、离子规则、规则测试和权重校准会变得困难。

## 3. 优化目标

本优化阶段的目标不是增加更多复杂化学机制，而是让现有原型变成一个更可靠的标准品校准工具。

优先级如下：

1. 降低假阳性候选数量。
2. 让 AI 生成候选校准成为主流程。
3. 让正负离子模式、样品来源和网络来源参与过滤。
4. 提升报告的人工判读价值。
5. 建立规则命中统计，为后续权重校准提供依据。
6. 保持工程结构可测试、可扩展。

## 4. 推荐优化路线

### 阶段一：匹配范围收窄与模式过滤

这是最高优先级优化。

#### 4.1 建立 spectrum 与 compound 的映射

从谱图路径或 `spectrum_id` 中提取样品名，例如：

```text
PET_pos_PETneg_All_purpose_Positiveneg_1neg_peak_list -> PET
PVDF_neg_PVDFneg_1 -> PVDF
PEEK20%GFR_pos_PEEK20%GFRneg_1 -> PEEK20%GFR
```

新增一个匹配策略：

```text
默认只将某个谱图与同名 compound 的 network 匹配
```

对 GFR 复合材料可允许别名映射：

```text
PEEK20%GFR -> PEEK20%GFR, PEEK
PPS40%GFR  -> PPS40%GFR, PPS
```

后续如需跨材料检索，可通过配置显式打开。

#### 4.2 根据谱图正负模式过滤 ion_mode

建议规则：

| 谱图模式 | 允许匹配的 network ion_mode |
|---|---|
| positive / pos / `+` | positive |
| negative / neg / `-` | negative |
| unknown | positive, negative |

第一版建议默认不匹配 `neutral` 记录到实验 m/z，除非配置中打开：

```yaml
matching:
  allow_neutral_mass_match: false
```

#### 4.3 设置最小候选质量和重原子约束

建议增加匹配过滤：

```yaml
matching:
  min_candidate_mass: 10.0
  min_candidate_heavy_atoms: 1
  exclude_formulas: ["H", "H2"]
```

这样可以减少非常小、解释价值低的公式进入主报告。

#### 验收指标

- 每个谱图的 m/z 匹配候选数从数千条降低到可人工检查的规模。
- PET 谱图默认不再将 COC/POMC 作为 Top compound。
- 报告中明确显示当前使用的是 sample-restricted matching。

### 阶段二：AI 生成候选校准主链路

#### 4.4 标准化 AI 生成候选输入格式

支持以下最小格式：

```csv
spectrum_id,peak_mz,candidate_formula,rf_rank,rf_score
```

其中 `rf_rank` 和 `rf_score` 是历史字段名，可理解为 AI 生成候选的原始排序和置信分数，允许缺失。

如果 AI 生成输出当前只有分子式列表，也应允许：

```csv
spectrum_id,peak_mz,candidate_formula
```

#### 4.5 区分三类匹配结果

报告和 CSV 中新增 `match_type`：

| match_type | 含义 |
|---|---|
| rf_network_formula | AI 生成分子式与结构网络公式一致 |
| mass_only | 仅 m/z 与结构网络质量匹配 |
| rf_only_unexplained | AI 生成输出给出但结构网络无法解释 |

推荐排序优先级：

```text
rf_network_formula > mass_only > rf_only_unexplained
```

#### 4.6 改进最终评分

建议第一版评分：

```text
final_score =
  network_score
  + rf_match_bonus
  + ion_mode_bonus
  + compound_support_bonus
  - mass_error_penalty
  - broad_rule_penalty
```

其中：

- `rf_match_bonus` 只给 AI 生成候选与 network 公式交集。
- `ion_mode_bonus` 只给正负模式一致的候选。
- `compound_support_bonus` 来自同一 compound 在同一谱图中解释的峰数和总强度。
- `broad_rule_penalty` 用于 neutral_loss、dimer、recombination 等低特异性规则。

#### 验收指标

- 有 AI 生成候选输入时，报告优先展示 AI 生成输出与网络共同支持的候选。
- AI 生成输出未被网络解释的候选可以单独列出，供检查规则缺口。
- `rf_formula_matches.csv` 不再只是空表头。

### 阶段三：报告增强

#### 4.7 增加 compound-level support

每个谱图报告增加：

```markdown
## Compound-level support

| compound | explained_peaks | explained_intensity_sum | top_formulas | best_score |
```

这比单条匹配记录更适合判断该材料是否被整体支持。

#### 4.8 增加 unmatched high-intensity peaks

输出当前谱图中强度最高但未被解释的峰：

```markdown
## Unmatched high-intensity peaks

| m/z | intensity | nearest_network_formula | mass_error_da |
```

这部分用于指导下一步规则补充，而不是只看已匹配结果。

#### 4.9 增加规则命中统计

输出：

```text
outputs/summary/rule_performance.csv
```

字段建议：

```csv
rule_type,generated_count,matched_count,matched_intensity_sum,hit_rate
parent,20,12,5400,0.60
fragment,800,85,12000,0.106
neutral_loss,3000,30,900,0.010
```

#### 验收指标

- 每个报告可以回答三个问题：
  1. 这个谱图主要被哪个 compound 解释？
  2. 哪些高强峰仍未解释？
  3. 哪些规则贡献大，哪些规则只制造噪声？

### 阶段四：规则与模块结构整理

#### 4.10 拆分 `fragmentation.py`

将以下逻辑从 `network.py` 拆出：

- 可断裂键筛选。
- 断键组合枚举。
- fragment formula 计算。
- fragment 去重与路径保留。

建议公开接口：

```python
generate_fragments(mol, config) -> list[Fragment]
```

#### 4.11 拆分 `ion_rules.py`

将以下规则拆出：

- H-shift。
- positive/negative adduct。
- neutral loss。
- dimer。
- recombination。

建议公开接口：

```python
apply_ion_rules(base_record, config) -> list[FormulaRecord]
```

#### 4.12 补齐配置开关

`config/default.yaml` 应补齐实施方案中的配置段：

```yaml
ion_modes:
  positive: true
  negative: true

ion_rules:
  parent_ion: true
  h_shift: true
  dimers: true
  parent_fragment_clusters: true
  fragment_recombination: false

matching:
  restrict_to_spectrum_compound: true
  allow_neutral_mass_match: false
  min_candidate_mass: 10.0
  exclude_formulas: ["H", "H2"]
```

第一版建议 `fragment_recombination` 默认关闭，等报告统计证明需要后再打开。

#### 验收指标

- `network.py` 只负责编排，不再承载所有规则细节。
- 每个规则模块都有独立单元测试。
- 所有高风险规则都能通过 YAML 开关控制。

### 阶段五：测试与质量门槛

#### 4.13 增加测试用例

建议新增测试：

- `test_matching_filters.py`
  - positive 谱图只匹配 positive。
  - PET 谱图默认只匹配 PET network。
  - neutral 记录默认不进入 mass match。

- `test_rf_integration.py`
  - RF 分子式乱序如 `H7C7` 可规范化为 `C7H7`。
  - RF 与 network 交集优先级高于 mass_only。
  - 缺失 `rf_rank` 和 `rf_score` 不报错。

- `test_report_summary.py`
  - 报告包含 compound-level support。
  - 报告包含 unmatched high-intensity peaks。
  - summary 输出 rule performance。

- `test_compounds_quality.py`
  - `data/compounds.csv` 中人工 formula 与 RDKit formula 不一致时输出 warning。
  - 无效 SMILES 被跳过并记录。

#### 4.14 固定测试入口

当前 Windows 和 WSL RDKit 环境缺少 `pytest`。建议：

- 在 `requirements.txt` 中保留 `pytest`。
- README 中说明安装依赖或提供 conda 环境命令。
- CI 或本地验收统一使用：

```bash
python -m pytest
```

#### 验收指标

- `pytest` 可直接运行。
- 核心匹配过滤、RF 校准、报告统计都有测试覆盖。
- 真实数据跑完后 summary 指标稳定。

## 5. 建议实施顺序

推荐按以下顺序推进：

1. 新增 spectrum-to-compound 映射和 ion_mode 过滤。
2. 调整 mass matching，默认只匹配同名 compound 且排除 neutral。
3. 接入真实 AI 生成候选输入，补 `match_type`。
4. 增强报告：compound support、unmatched peaks、rule performance。
5. 拆分 `fragmentation.py` 和 `ion_rules.py`。
6. 补齐 YAML 配置和测试。
7. 根据 rule performance 调整默认规则权重。

不要一开始就扩展更多复杂碎片规则。当前更重要的是先把假阳性压下来，并让已有规则的贡献变得可量化。

## 6. 第一轮优化完成标准

第一轮优化建议以以下结果作为完成标准：

- `python -m tofsims_formula_network.cli run-all --config config/default.yaml` 可以完成。
- 每个谱图默认只匹配对应 compound 或显式配置允许的 related compounds。
- 正谱只匹配 positive，负谱只匹配 negative。
- `spectrum_mass_matches.csv` 中候选数显著下降。
- 有 AI 生成候选输入时，`rf_formula_matches.csv` 有实际结果。
- 每个报告包含：
  - Top matched peaks。
  - Compound-level support。
  - Unmatched high-intensity peaks。
  - RF/network/mass-only 匹配分类。
- `outputs/summary/rule_performance.csv` 存在。
- `pytest` 通过。

## 7. 风险与取舍

### 7.1 过度收窄可能漏掉真实跨来源峰

默认只匹配同名 compound 会减少假阳性，但可能漏掉污染物、添加剂或基质峰。建议通过配置解决：

```yaml
matching:
  extra_compounds:
    PET: ["STD001", "PDMS"]
```

即默认严格，必要时显式放宽。

### 7.2 neutral 记录是否参与匹配需要谨慎

TOF-SIMS 实验检测的是离子信号。neutral 记录可保留在 network 中作为中间结构，但不建议默认参与实验 m/z 匹配。

### 7.3 聚合物模型仍然是近似

当前 `compounds.csv` 中很多聚合物用单体、重复单元或近似结构表示。第一轮优化不应试图一次性解决聚合物端基、链长分布和真实重复单元组合问题。建议先在报告中明确 `compound_model` 来源，后续再增加 polymer repeat-unit 规则。

## 8. 后续扩展方向

第一轮优化稳定后，再考虑：

- 聚合物重复单元规则：`end_group + n * repeat_unit`。
- 官能团约束的中性损失。
- 芳香体系特征碎片规则。
- Bi 源或基底相关特异规则。
- 标准品数据驱动的规则权重学习。
- 网络图可视化和交互式筛选界面。
