# TOF-SIMS Formula Network 算法规则说明

> 更新日期：2026-06-11  
> 适用范围：完成 `fragmentation.py` / `ion_rules.py` 拆分，并加入召回率规则包后的当前 formula network 算法。

## 1. 算法定位

本项目用于生成 TOF-SIMS 分析中的候选分子式网络。它不是完整的离子轰击模拟，不预测峰强，也不直接给出最终化学归属。

当前主流程是：

```text
compound SMILES / 聚合物近似结构
  -> 母体公式和结构来源 base formulas
  -> fragmentation / H-shift / adduct / neutral-loss / oligomer / dimer 扩展
  -> 低分召回规则包
  -> 带路径和分数的 FormulaRecord
  -> 0510 同材料验证，或用于谱图/RF 匹配
```

因此，一个公式命中 network 的含义是：

```text
该公式可以被当前配置中的某条规则解释
```

而不是：

```text
该峰已经被最终确定归属
```

## 2. 主要模块

| 模块 | 职责 |
|---|---|
| `formula.py` | 分子式解析、规范化、精确质量和质量误差 |
| `molecule_io.py` | 读取 compound 表，用 RDKit 加载 SMILES |
| `fragmentation.py` | 可断裂键筛选和结构碎片公式生成 |
| `ion_rules.py` | H-shift、加合、中性损失、二聚体规则 |
| `rule_packs.py` | 面向召回率的补充公式族 |
| `network.py` | 网络生成编排、寡聚扩展、评分、去重和输出 |
| `scoring.py` | 规则型可信度评分 |
| `verify_0510.py` | `data/0510` 人工标注公式覆盖验证 |

## 3. 输入 compound 模型

材料信息来自 `data/compounds.csv`。

必需字段：

```text
compound_id,name,smiles
```

当前算法会使用的可选字段：

```text
formula
group
notes
extend_formula
```

如果 `formula` 有值，优先使用人工给定公式；如果为空，则用 RDKit 从 `smiles` 计算分子式。RDKit 加载分子时会显式加氢。

需要注意：很多聚合物当前用重复单元、短链片段或近似结构表示。这是工程原型阶段的选择，但 SMILES 模型质量会直接影响公式召回率。

## 4. 母体公式规则

每个 compound 首先生成一条母体公式记录：

```text
generation_type = parent
path = M
ion_mode = neutral
score = 1.0
```

母体公式是整个 formula network 的根节点。

## 5. 结构断裂规则

实现位置：`fragmentation.py`

默认配置：

```yaml
fragmentation:
  max_bond_breaks: 2
  min_heavy_atoms_per_fragment: 2
  allow_ring_bond_break: false
  allow_aromatic_bond_break: false
  max_generated_formulas_per_compound: 20000
```

当前可断裂键必须满足：

- 重原子与重原子之间的键。
- 单键。
- 不切 H-X 键。
- 默认不切环内键。
- 默认不切芳香键。

算法会枚举最多 `max_bond_breaks` 根键的断裂组合，并计算断裂后每个 RDKit fragment 的元素计数。

重要限制：

```text
fragment formula 是原子集合公式，不是完整反应机理公式。
```

也就是说，当前不会在 fragmentation 阶段模拟自由基稳定、重排、表面反应或重新补氢。

## 6. H-shift 规则

实现位置：`ion_rules.py`

对 parent、fragment、oligomer base 都尝试 H 数变化：

```yaml
h_shift_range: [-2, -1, 0, 1, 2]
```

例如：

```text
C7H8 -> C7H6, C7H7, C7H8, C7H9, C7H10
```

如果减 H 后 H 数为负，则丢弃。

`shift = 0` 时保留原始 `generation_type`；`shift != 0` 时记录为：

```text
generation_type = h_shift
ion_mode = neutral
```

## 7. 加合规则

实现位置：`ion_rules.py`

正离子加合：

```yaml
common_adducts_positive: ["H", "Na", "K"]
```

负离子加合：

```yaml
common_adducts_negative: ["-H", "Cl", "O", "OH"]
```

规则含义：

- `H`、`Na`、`K`、`Cl`、`O`、`OH`：向候选公式中添加对应元素。
- `-H`：从候选公式中扣除 H。

加合记录使用：

```text
generation_type = adduct
ion_mode = positive 或 negative
charge = +1 或 -1
```

当前加合规则仍是分子式层面的启发式规则，不检查配位几何、官能团位置或电荷稳定性。

## 8. 中性损失规则

实现位置：`ion_rules.py`

当前配置：

```yaml
neutral_losses:
  ["H2", "H2O", "CO", "CO2", "NH3", "CH3", "OH", "HCl", "HF"]
```

算法会从 H-shift 后的候选公式中扣除这些中性损失；如果元素数不够扣除，则丢弃。

中性损失记录使用：

```text
generation_type = neutral_loss
ion_mode = neutral
```

重要限制：当前中性损失只做分子式扣减，不检查真实结构中是否存在对应官能团或局部反应路径。

## 9. 寡聚扩展

实现位置：`network.py`

如果 `data/compounds.csv` 中存在 `extend_formula`，则对 parent 和 fragment base 做重复单元扩展。

配置：

```yaml
oligomer:
  max_extend: 12
  max_mass: 2000
  penalty_per_extend: 0.08
```

规则：

```text
base + n * extend_formula, n = 1..max_extend
```

超过 `max_mass` 的候选会被跳过。

母体扩展记录使用：

```text
generation_type = oligomer
```

fragment 扩展后仍保留 fragment 相关路径，但会按扩展次数扣分。

## 10. 二聚体规则

实现位置：`ion_rules.py`

如果启用：

```yaml
dimers: true
```

算法会生成：

```text
2M + H
2M + Na
2M - H
2M + Cl
```

二聚体记录使用：

```text
generation_type = dimer
```

并有额外扣分。

## 11. 召回率规则包

实现位置：`rule_packs.py`

这些规则包来自对 0510 人工标注缺口的分析。它们的目标是提升公式召回率，同时通过低分和明确的 `generation_type` 保持可解释性。

### 11.1 `carbon_cluster`

启用材料：

```text
COC, EVA, PET, POMC, POMH
```

生成公式族：

```text
C_nH_m
C_nH_mO_x
```

当前配置：

```yaml
carbon_cluster:
  min_c: 3
  max_c: 14
  max_h_extra: 2
  max_o: 3
  max_mass: 220.0
```

如果母体不含 O，则只生成烃类碳簇；如果母体含 O，则额外生成最高到 `O3` 的氧化碳簇。

典型覆盖公式：

```text
C3H5, C4H, C5H7, C9H7, C4HO, C9H9O3
```

这类公式在聚合物 TOF-SIMS 中常见，但保守的 RDKit 断键规则很难覆盖。

### 11.2 `siloxane_fragment`

启用材料：

```text
PDMS
```

当前配置：

```yaml
siloxane_fragment:
  max_si: 6
  max_mass: 360.0
```

该规则生成受 Si 数、C/O/H 范围和质量上限约束的 Si/C/H/O 公式族。

典型覆盖公式：

```text
C3H9Si
C5H15OSi2
O2Si
HO2Si
C7H21O2Si3
```

这是当前 PDMS 召回率提升的主要来源。

### 11.3 `external_adduct`

启用材料：

```text
POMC, POMH, EVA
```

当前配置：

```yaml
external_adduct:
  adducts: ["Na", "K", "Cs", "Na2O", "HNa2O"]
  max_base_mass: 500.0
```

该规则从已有 base formula 派生外部加合候选，主要用于金属离子或外源离子相关的人工标注公式。

## 12. 评分规则

实现位置：`scoring.py`

评分是启发式可信度评分，基本思想是：

```text
结构路径越直接，分数越高；
规则越宽泛，分数越低。
```

基础分：

| generation_type | 基础分 |
|---|---:|
| parent | 1.00 |
| fragment | 0.75 |
| carbon_cluster | 0.22 |
| external_adduct | 0.25 |
| siloxane_fragment | 0.28 |

扣分项：

| 特征 | 扣分 |
|---|---:|
| 每断一根键 | -0.15 |
| 每 H-shift 一步 | -0.05 |
| 每个 neutral loss | -0.10 |
| 非 H 加合 | -0.12 |
| dimer | -0.20 |
| oligomer 每扩展一次 | -0.08 |

最终分数限制在：

```text
0.0 <= score <= 1.0
```

因为召回率规则包的基础分较低，它们可以提升覆盖率，但不会在排序上压过 parent、fragment 或强结构路径。

## 13. 去重规则

实现位置：`network.py`

候选记录按以下 key 去重：

```text
(formula, ion_mode, generation_type)
```

重复时：

- 保留分数更高的记录。
- 如果分数没有更高，则可能追加部分 path 信息。

同一公式仍可以因为不同 `generation_type` 或不同 `ion_mode` 保留多条记录。

例如：

```text
C3H5 / carbon_cluster / positive
C3H5 / fragment / neutral
C3H5 / adduct / positive
```

## 14. 0510 验证方法

实现位置：`verify_0510.py`

0510 验证比较的是：

```text
人工标注公式
vs
同材料 compound 的 network formula 集合
```

重要说明：这不是全库 m/z 匹配。它不会让 PET 谱图去匹配所有 compound network，而是只检查 PET 人工公式是否存在于 PET network 中。

验证流程：

```text
人工标注公式
  -> 公式规范化
  -> 默认过滤重原子数 <= 2 的原子/双原子离子
  -> 选择同材料 network
  -> 判断公式集合覆盖率
```

当前输出：

```text
outputs/summary/0510_verification.md
outputs/summary/0510_verification.json
outputs/summary/0510_matched_formulas.csv
outputs/summary/0510_unmatched_formulas.csv
outputs/summary/0510_rule_contribution.csv
```

加入规则包后的总体结果：

| 指标 | 数值 |
|---|---:|
| 评价标注数 | 1199 |
| 命中标注数 | 1050 |
| 总体命中率 | 87.6% |
| 强度覆盖率 | 96.2% |

材料级结果：

| Material | Evaluated | Matched | Hit rate | Intensity coverage |
|---|---:|---:|---:|---:|
| EVA | 117 | 113 | 96.6% | 96.0% |
| POMC | 108 | 102 | 94.4% | 98.5% |
| COC | 129 | 115 | 89.1% | 95.2% |
| POMH | 105 | 93 | 88.6% | 94.6% |
| PET | 552 | 483 | 87.5% | 96.5% |
| PDMS | 188 | 144 | 76.6% | 94.6% |

规则贡献：

| generation_type | matched |
|---|---:|
| carbon_cluster | 437 |
| adduct | 251 |
| neutral_loss | 243 |
| siloxane_fragment | 96 |
| fragment | 23 |

## 15. 当前限制

- 公式覆盖率不等于最终化学归属准确率。
- 召回率规则包有意保持宽泛，因此必须低分处理。
- 0510 验证当前主要衡量同材料公式集合覆盖率，下一步应加入 polarity / `ion_mode` 一致性统计。
- 常规 `match-spectrum` 仍需要做样品限制和离子模式过滤；否则更大的 network 会增加 mass-only 假阳性。
- 中性损失和外部加合仍然是公式层面的启发式规则，尚未检查完整结构上下文。

## 16. 建议下一步

下一步算法评估建议拆成两项指标：

```text
formula coverage:
  annotation formula exists in same-material network

polarity-consistent coverage:
  annotation formula exists in same-material network with compatible ion_mode
```

这样可以区分：

1. 网络是否能生成人工标注公式。
2. 网络是否能用与正/负谱一致的离子模式生成该公式。

在这一步完成前，不建议继续大幅扩大规则包范围。
