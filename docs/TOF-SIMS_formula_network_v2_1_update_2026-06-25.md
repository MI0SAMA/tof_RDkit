# TOF-SIMS Formula Network v2.1 更新记录

日期：2026-06-25

## 更新目标

v2.1 的目标是把 v2 从“有 lineage 的最小网络”推进到更接近真实纯物质 TOF-SIMS 评价流程的版本。本次重点不是追求一次性最高召回，而是建立后续可调参、可评估、可和实验人员讨论的稳定框架。

## 数据入口调整

`PEEK20%GFR` 和 `PPS40%GFR` 已从默认 `data/compounds.csv` 中移除。

原因：

- 二者不是纯物质。
- 旧记录使用 PEEK / PPS 的纯物质 SMILES，会把复合材料误当纯物质。
- 当前算法目标是单一纯物质内部的碎片网络，不处理玻纤复合体系。

同时在配置中加入：

```yaml
io:
  excluded_compound_ids: ["PEEK20%GFR", "PPS40%GFR"]
```

即使外部 compounds 文件包含这两个 ID，默认构建也会跳过。

## 生成规则更新

### v2.1 当前主路线

```text
单个 compound
→ parent neutral node
→ RDKit fragmentation
→ fragment neutral node
→ fragment H-shift node
→ ionization
→ H-shift fragment recombination
→ formula summary
```

相比 v2，核心变化是 H-shift 不再只隐含在 protonation/deprotonation 中，而是成为 fragmentation 后的显式中间节点。

### Fragment H-shift

当前默认：

```text
fragment - H
fragment + H
```

配置：

```yaml
network_v2:
  fragment_h_shift:
    enabled: true
    shifts: [-1, 1]
```

H-shift 节点的 `generation_type` 为：

```text
fragment_h_shift
```

边类型为：

```text
h_shift
```

### Ionization

当前 ionization variants：

- `electron_loss`：公式不变，positive
- `electron_gain`：公式不变，negative
- `protonation`：`+H`，positive
- `deprotonation`：`-H`，negative

为避免 H 变化重复叠加，`fragment_h_shift` 节点默认只接：

- `electron_loss`
- `electron_gain`

不再继续接 protonation / deprotonation。

## Recombination 更新

v2 的 recombination 是：

```text
A + B
A + B - H
A + B - H2
```

v2.1 改成基于 H-shift fragment pool 的组合。也就是说，先生成：

```text
F0
F-
F+
```

再进行组合。

当前默认允许：

```text
F- + G- → dehydrogenative_coupling
F0 + G- → single_dehydrogenative_recombination
F+ + G- → h_transfer_recombination
```

默认不启用：

```text
F0 + G0
F+ + G+
```

原因是这些组合更容易变成低约束的公式拼接。

## 位点约束

fragmentation 现在会记录片段断键边界原子：

- `boundary_atom_indices`
- `boundary_elements`

v2.1 的 recombination 默认需要位点元素兼容。

当前允许的位点组合：

```yaml
allowed_site_pairs:
  - ["C", "C"]
  - ["C", "O"]
  - ["C", "N"]
  - ["C", "S"]
  - ["Si", "O"]
```

这仍然是第一版粗粒度位点约束，不等同于完整反应位点化学。它的作用是阻止完全任意的片段两两组合。

## 打分更新

### 新增 fragment_h_shift 结构分

```yaml
structure_scores:
  parent: 0.45
  fragment: 0.72
  fragment_h_shift: 0.68
  recombination: 0.64
```

H-shift 片段比原始 fragment 略低，但仍高于 recombination。

### 新增质量区间先验

真实谱图中强峰多集中在低到中 m/z 区间，因此加入温和质量先验：

```yaml
mass_prior:
  preferred_min_mass: 25.0
  preferred_max_mass: 200.0
  preferred_mass_bonus: 0.05
  high_mass_penalty_start: 500.0
  penalty_per_100_da: 0.02
  max_high_mass_penalty: 0.15
```

这只是小幅微调，避免高质量复杂候选过度靠前。实际评估显示，这一项没有显著改变整体均值，说明当前瓶颈主要还是生成规则覆盖不足，而不是单纯排序问题。

## 真实谱图评价预处理

新增模块：

- `tofsims_formula_network/evaluation_v2.py`

新增命令：

```bash
python -m tofsims_formula_network.cli evaluate-network-v2 --config config/default.yaml
```

输出：

- `outputs/summary/network_v2_evaluation_summary.csv`
- `outputs/summary/network_v2_evaluation_peaks.csv`

### 评价流程

```text
真实谱图
→ 读取与基础过滤
→ centroid 合并相邻 m/z 点
→ 标记污染峰 / 低质量背景峰 / 低质量特征峰
→ 生成主评价峰集合
→ 与 v2.1 formula_summary 做质量匹配
→ 输出 recall 与 top50 指标
```

### Centroid

当前参数：

```yaml
centroid_da: 0.03
centroid_ppm: 50
```

相邻 m/z 点会合并成一个 centroid 峰，强度为簇内强度和。

### 污染峰 / 外源离子过滤

正离子默认标记并排除：

- `Na+`
- `K+`
- `Na2OH+`
- `NaKOH+`
- `K2OH+`
- `Cs+`

负离子默认标记并排除：

- `O-`
- `OH-`
- `Cl-`
- `Cl37-`

### 低质量峰

默认：

```text
m/z < 25 不进入主评价
```

但保留低质量特征峰例外，例如：

- `C2H3+`
- `C2H5+`
- `CF+`
- `CH3O+`
- `F-`
- `CN-`

这些峰会标记为：

```text
low_mass_feature
```

并进入主评价。

## 评价指标

### network_recall

主评价峰中，有多少能被当前物质的 network formula summary 质量匹配命中。

```text
network_recall = matched_included_peaks / included_peaks
```

### top_n_peak_hit_rate

从真实谱图强峰角度看，主评价峰按强度取前 N，有多少能被 network 命中。

当前由于 centroid 后每个谱图主评价峰通常少于 50，因此它和 `network_recall` 数值相同或非常接近。

### top_n_network_precision_proxy

从 network 排名角度看，当前物质当前极性的 formula summary 按 `formula_score` 取前 N，有多少能落到真实主评价峰附近。

这个指标是 m/z 代理指标，不等同于人工确认准确率。

```text
top_n_network_precision_proxy = matched_top_network_candidates / top_network_candidates
```

## 当前运行结果

### v2.1 构建结果

命令：

```bash
/home/yao/PROGRAM/miniforge3/envs/rdkit/bin/python -m tofsims_formula_network.cli build-network-v2 --config config/default.yaml
```

构建 18 个默认纯物质。`PEEK20%GFR` 与 `PPS40%GFR` 已不再构建。

| compound_id | nodes | edges | unique_ion_formulas |
|---|---:|---:|---:|
| STD001 | 16 | 15 | 10 |
| PTFE | 4551 | 5459 | 88 |
| PVDF | 443 | 517 | 82 |
| ETFE | 10014 | 11959 | 353 |
| FEP | 662 | 661 | 31 |
| PFA | 662 | 661 | 31 |
| PEEK | 6795 | 8100 | 450 |
| PEI | 19695 | 23544 | 998 |
| PEN | 25616 | 30615 | 1082 |
| PET | 25616 | 30615 | 1082 |
| PPS | 113 | 127 | 32 |
| PI | 3503 | 4162 | 561 |
| PDMS | 324 | 323 | 52 |
| COC | 1240 | 1464 | 118 |
| EVA | 5364 | 6388 | 361 |
| Nomex | 7160 | 8537 | 575 |
| POMC | 27 | 26 | 10 |
| POMH | 27 | 26 | 10 |

### v2.1 真实谱图评价结果

命令：

```bash
/home/yao/PROGRAM/miniforge3/envs/rdkit/bin/python -m tofsims_formula_network.cli evaluate-network-v2 --config config/default.yaml
```

汇总：

| 指标 | 均值 | 中位数 | 最大值 |
|---|---:|---:|---:|
| `network_recall` | 0.185 | 0.100 | 0.800 |
| `top_n_peak_hit_rate` | 0.185 | 0.100 | 0.800 |
| `top_n_network_precision_proxy` | 0.062 | 0.023 | 0.250 |
| `included_peaks` | 8.13 | 9.00 | 12.00 |
| `excluded_peaks` | 2.47 | 2.00 | 6.00 |
| `contaminant_peaks` | 1.13 | 1.00 | 4.00 |

按材料平均：

| material | network_recall | top_n_peak_hit_rate | top_n_network_precision_proxy |
|---|---:|---:|---:|
| COC | 0.000 | 0.000 | 0.000 |
| ETFE | 0.200 | 0.200 | 0.030 |
| EVA | 0.364 | 0.364 | 0.040 |
| FEP | 0.157 | 0.157 | 0.096 |
| Nomex | 0.171 | 0.171 | 0.020 |
| PEEK | 0.062 | 0.062 | 0.010 |
| PEI | 0.100 | 0.100 | 0.010 |
| PEN | 0.461 | 0.461 | 0.030 |
| PFA | 0.250 | 0.250 | 0.158 |
| PI | 0.000 | 0.000 | 0.000 |
| POMC | 0.100 | 0.100 | 0.200 |
| POMH | 0.097 | 0.097 | 0.200 |
| PPS | 0.000 | 0.000 | 0.000 |
| PTFE | 0.525 | 0.525 | 0.054 |
| PVDF | 0.292 | 0.292 | 0.084 |

## 当前判断

1. 谱图预处理是必要的。尤其是 `Cs+` 在多个正离子谱中非常明显，如果不排除，会严重干扰纯物质 network 的评价。
2. v2.1 的 H-shift 和位点约束 recombination 已经形成可解释路线，但召回率仍偏低。
3. 低召回材料包括 COC、PI、PPS，说明当前 RDKit 断键 + H-shift + 简单重组不足以覆盖这些材料的真实强峰。
4. network top50 precision proxy 偏低，说明公式层排序还需要加入更强的 TOF-SIMS 经验项，例如芳香稳定性、含氟小片段、含硫/含氮特征碎片等。
5. 后续不建议回到材料补丁 rule packs，而应建立机制型规则包。

## 下一步建议

1. 和实验人员确认低召回材料的代表强峰，例如 COC、PI、PPS 的前几个未命中峰。
2. 为 fragment 增加更细的位点类型，而不只是边界元素。
3. 引入机制型规则：
   - aromatic-stabilized fragments
   - fluorocarbon fragments
   - sulfur-containing fragments
   - imide / amide / carbonyl cleavage
   - siloxane rearrangement
4. 将 `top_n_network_precision_proxy` 与人工标注公式对照，逐步升级为真正的 top50 accuracy。
