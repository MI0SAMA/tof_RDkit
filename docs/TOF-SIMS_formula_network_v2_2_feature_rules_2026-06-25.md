# TOF-SIMS Formula Network v2.2 结构特征触发规则更新

日期：2026-06-25

## 更新原则

本次更新的核心原则是：

```text
规则不按材料名触发，而按结构特征触发。
```

不采用：

```text
if material == PTFE:
    generate F-, CF+, CF2+, CF3+
```

而采用：

```text
if molecule has C-F bonds:
    enable fluorocarbon fragmentation rules
```

因此同一套规则可以自然作用于 PTFE、PVDF、ETFE、FEP、PFA，也可以作用于未来新增的其他含氟材料。

## 新增模块

新增：

- `tofsims_formula_network/feature_rules_v2.py`

该模块负责：

1. 用 RDKit 识别结构特征。
2. 根据结构特征启用机制型规则包。
3. 生成带有触发证据的 feature-rule candidates。

## 当前结构特征

当前识别：

| trigger_feature | 识别依据 | 用途 |
|---|---|---|
| `fluorocarbon_motif` | 存在 C-F 键 | 含氟碎片规则 |
| `acetal_or_ether` | 存在 `O-C-O` 或 `C-O-C` | 氧鎓/醚类小片段规则 |
| `aromatic_ring` | 存在芳香原子 | 芳香稳定碎片规则 |
| `sulfur_aromatic` | S 与芳香环境相连 | 含硫芳香碎片规则 |

## 当前机制型规则包

### fluorocarbon_fragmentation

触发：

```text
fluorocarbon_motif
```

候选：

```text
F-
CF+
CF2+
CF3+
CF3-
C2F3+
C2F3-
C2F4+
C2F4-
C2F5+
C3F5+
C3F7+
```

### acetal_oxonium_series

触发：

```text
acetal_or_ether
```

候选：

```text
CH3O+
C2H5O+
C2H5O2+
C3H7O2+
C3H7O3+
```

该规则目前用于表达缩醛/醚结构容易形成的氧鎓类小片段。它不是按 POMC/POMH 名称触发，而是按结构中的 `C-O-C` / `O-C-O` 特征触发。

### aromatic_stable_fragments

触发：

```text
aromatic_ring
```

候选：

```text
C6H5+
C6H5-
C7H7+
C6H5O+
C6H5O-
```

### sulfur_aromatic_fragments

触发：

```text
sulfur_aromatic
```

候选：

```text
S-
HS-
CS-
C6H5S+
C6H5S-
C6H4S-
C6H6S+
```

## 输出字段

`outputs/networks_v2/*_nodes.csv` 中新增或使用以下字段：

- `generation_type = feature_rule`
- `rule_pack`
- `trigger_feature`
- `evidence`
- `operation`

示例：

```text
formula: CF3
ion_mode: positive
generation_type: feature_rule
rule_pack: fluorocarbon_fragmentation
trigger_feature: fluorocarbon_motif
operation: diagnostic_CF3
evidence: C-F bonds present; heavy element counts=...
```

这样每个候选不只是一个公式，而能说明它为什么被生成。

## 与 v2.1 的指标对比

同一评价流程下，v2.1 到 v2.2 的整体指标变化：

| 指标 | v2.1 | v2.2 |
|---|---:|---:|
| `network_recall` mean | 0.185 | 0.260 |
| `top_n_peak_hit_rate` mean | 0.185 | 0.260 |
| `top_n_network_precision_proxy` mean | 0.062 | 0.100 |
| `network_recall` median | 0.100 | 0.191 |
| `top_n_network_precision_proxy` median | 0.023 | 0.044 |

说明：

- `network_recall` 提升明显，主要来自含氟材料和 POM 系列。
- `top_n_network_precision_proxy` 也有提升，但仍偏低，说明排序规则仍需继续校准。
- v2.2 不是通过材料名补丁提升，而是通过结构特征触发机制规则提升。

## v2.2 当前按材料结果

| material | network_recall | top_n_peak_hit_rate | top_n_network_precision_proxy |
|---|---:|---:|---:|
| COC | 0.000 | 0.000 | 0.000 |
| ETFE | 0.312 | 0.312 | 0.060 |
| EVA | 0.364 | 0.364 | 0.040 |
| FEP | 0.369 | 0.369 | 0.184 |
| Nomex | 0.171 | 0.171 | 0.020 |
| PEEK | 0.062 | 0.062 | 0.010 |
| PEI | 0.100 | 0.100 | 0.010 |
| PEN | 0.461 | 0.461 | 0.030 |
| PFA | 0.450 | 0.450 | 0.234 |
| PI | 0.000 | 0.000 | 0.000 |
| POMC | 0.250 | 0.250 | 0.322 |
| POMH | 0.264 | 0.264 | 0.378 |
| PPS | 0.111 | 0.111 | 0.053 |
| PTFE | 0.650 | 0.650 | 0.066 |
| PVDF | 0.333 | 0.333 | 0.096 |

## 代表性新增命中

### 含氟材料

新增/增强命中：

```text
F-
CF+
CF2+
CF3+
C2F4+
C2F5+
C3F5+
C3F7+
```

例如：

- PTFE negative `m/z 19.001` 命中 `F-`
- FEP positive `m/z 30.999` 命中 `CF+`
- FEP/PFA positive `m/z 99.995-99.997` 命中 `C2F4+`
- PFA positive `m/z 168.998` 命中 `C3F7+`

### POMC / POMH

新增/增强命中：

```text
CH3O+
C2H5O+
C2H5O2+
C3H7O2+
C3H7O3+
```

例如：

- POMC/POMH positive `m/z 45.034` 命中 `C2H5O+`
- POMC/POMH positive `m/z 61.028` 命中 `C2H5O2+`
- POMC/POMH positive `m/z 75.040` 命中 `C3H7O2+`

### PPS

新增含硫芳香规则后，PPS 出现少量改善：

```text
S-
HS-
C6H5S
C6H4S
```

但 PPS 主要强峰仍未充分解释，后续需要更细的含硫芳香裂解机制。

## 当前仍存在的问题

1. COC、PI 仍然为 0，说明当前 feature rules 还没有覆盖其主要真实强峰机制。
2. PEEK、PEI、Nomex 的改善有限，需要更精细的 aromatic / carbonyl / amide-imide 规则。
3. `top_n_network_precision_proxy` 仍偏低，说明 feature rules 提高了召回，但公式排序还需要加入更好的 TOF-SIMS 稳定性与通用背景峰惩罚。
4. 当前 feature rules 的候选公式仍是人工列举的机制型小集合，后续应逐步改成由结构位点生成。

## 下一步建议

1. 增加 `carbonyl / ester / imide / amide` 特征识别。
2. 为 PI、PEI、Nomex 引入结构约束的 `CO`、`CO2`、`NCO`、`HCN` 相关裂解规则。
3. 为 COC 引入环烃/降冰片烯类结构碎片规则，但仍需按结构特征触发。
4. 将 common-background peaks 单独建模，对跨材料高频通用峰做评价降权。
5. 继续把 rule evidence 暴露给实验人员审核，逐条确认哪些机制规则可信。
