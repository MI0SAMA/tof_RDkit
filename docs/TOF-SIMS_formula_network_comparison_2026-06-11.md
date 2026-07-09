# TOF-SIMS Formula Network 对比记录

> 日期：2026-06-11  
> 范围：对比 formula network 不同阶段的算法规则、0510 物质级召回率、网络规模和规则贡献。

## 1. 文档目的

本文比较当前 formula network 算法与此前 0510 验证基线的差异。

比较重点是算法召回率：

```text
人工标注公式
vs
同材料生成的 formula network
```

本文不评价最终化学归属准确率，也不使用全库 m/z 匹配结果。

## 2. 版本阶段

| 阶段 | 说明 | 行为影响 |
|---|---|---|
| Baseline ver1 | 原始 formula network，包含 parent、fragment、H-shift、adduct、neutral loss、oligomer、dimer | 0510 总命中率 44.0% |
| 规则拆分版 | 将 `fragmentation.py` 和 `ion_rules.py` 从 `network.py` 拆出 | 行为不变，总记录数保持 85,811 |
| 召回率规则包版 | 新增 `carbon_cluster`、`siloxane_fragment`、`external_adduct` | 命中率提升到 87.6%，总记录数提升到 104,204 |

## 3. 0510 总体对比

| 指标 | Baseline ver1 | 当前 rule-pack 版本 | 变化 |
|---|---:|---:|---:|
| 评价标注数 | 1,199 | 1,199 | 0 |
| 命中标注数 | 527 | 1,050 | +523 |
| 未命中标注数 | 672 | 149 | -523 |
| 命中率 | 44.0% | 87.6% | +43.6 percentage points |
| 强度覆盖率 | 65.7% | 96.2% | +30.5 percentage points |

## 4. 物质级对比

下表合并每个物质的正谱和负谱。

| Material | Baseline 命中/评价 | Baseline hit | 当前命中/评价 | 当前 hit | 当前强度覆盖 | 主要新增支持 |
|---|---:|---:|---:|---:|---:|---|
| COC | 18 / 129 | 14.0% | 115 / 129 | 89.1% | 95.2% | `carbon_cluster` |
| EVA | 38 / 117 | 32.5% | 113 / 117 | 96.6% | 96.0% | `carbon_cluster`, `adduct` |
| PDMS | 58 / 188 | 30.9% | 144 / 188 | 76.6% | 94.6% | `siloxane_fragment` |
| PET | 267 / 552 | 48.4% | 483 / 552 | 87.5% | 96.5% | `carbon_cluster`, `neutral_loss` |
| POMC | 70 / 108 | 64.8% | 102 / 108 | 94.4% | 98.5% | `adduct`, `carbon_cluster` |
| POMH | 76 / 105 | 72.4% | 93 / 105 | 88.6% | 94.6% | `adduct`, `neutral_loss` |

## 5. 当前正负谱结果

| Material | Polarity | Evaluated | Matched | Unmatched | Hit rate | Intensity coverage |
|---|---:|---:|---:|---:|---:|---:|
| COC | neg | 60 | 55 | 5 | 91.7% | 98.7% |
| COC | pos | 69 | 60 | 9 | 87.0% | 94.5% |
| EVA | neg | 48 | 44 | 4 | 91.7% | 90.9% |
| EVA | pos | 69 | 69 | 0 | 100.0% | 100.0% |
| PDMS | neg | 92 | 69 | 23 | 75.0% | 91.3% |
| PDMS | pos | 96 | 75 | 21 | 78.1% | 96.3% |
| PET | neg | 254 | 221 | 33 | 87.0% | 96.9% |
| PET | pos | 298 | 262 | 36 | 87.9% | 96.0% |
| POMC | neg | 54 | 51 | 3 | 94.4% | 98.6% |
| POMC | pos | 54 | 51 | 3 | 94.4% | 98.5% |
| POMH | neg | 52 | 47 | 5 | 90.4% | 93.5% |
| POMH | pos | 53 | 46 | 7 | 86.8% | 95.5% |

## 6. 网络规模对比

| Compound | Baseline records | Current records | 变化 | 主要原因 |
|---|---:|---:|---:|---|
| COC | 3,108 | 3,588 | +480 | `carbon_cluster` |
| EVA | 8,576 | 10,471 | +1,895 | `carbon_cluster`, `external_adduct` |
| PDMS | 4,483 | 15,027 | +10,544 | `siloxane_fragment` |
| PET | 11,222 | 13,040 | +1,818 | `carbon_cluster` |
| POMC | 1,334 | 3,162 | +1,828 | `carbon_cluster`, `external_adduct` |
| POMH | 1,334 | 3,162 | +1,828 | `carbon_cluster`, `external_adduct` |
| All compounds | 85,811 | 104,204 | +18,393 | 召回率规则包 |

## 7. 当前规则贡献

数据来自 `outputs/summary/0510_rule_contribution.csv`。

| generation_type | Matched formulas | Matched intensity |
|---|---:|---:|
| `carbon_cluster` | 437 | 40,764,078.67 |
| `adduct` | 251 | 70,898,234.99 |
| `neutral_loss` | 243 | 27,914,798.48 |
| `siloxane_fragment` | 96 | 8,043,371.50 |
| `fragment` | 23 | 5,332,415.60 |

解释：

- `carbon_cluster` 是 COC、EVA、PET 和 POM 系材料召回率提升的最大来源。
- `siloxane_fragment` 对 PDMS 是关键新增规则。
- 原有 `adduct` 和 `neutral_loss` 在规则包加入后仍然贡献很大。
- 保守 RDKit fragment 的命中数量较少，但它仍是更高可信度的结构证据。

## 8. 各物质提升原因

### COC

Baseline COC 很差，主要是近似 COC SMILES 无法覆盖大量烃类碳簇。加入 `carbon_cluster` 后，高强度 `C_nH_m` 片段大多被覆盖。

剩余缺口包括含 O/Cl/Cs 的外源或污染相关公式，以及少量更高碳数公式。

### EVA

EVA 明显受益于烃类碳簇覆盖。当前 0510 子集中，EVA 正谱公式覆盖率达到 100.0%。

剩余缺口主要是 K/N/S 等外源或污染相关公式。

### PDMS

PDMS 仍是命中率最低的物质，但强度覆盖率已经较高。`siloxane_fragment` 捕捉了常见 Si/C/H/O 碎片，例如 `C3H9Si`、`C5H15OSi2`、`O2Si`。

剩余 unmatched 说明下一步应做更结构化的 siloxane oligomer / fragment 模型，而不是任意扩大 Si/C/H/O 枚举范围。

### PET

PET 通过碳簇和氧化碳簇规则显著提升。但 PET 的 0510 标注数量最多，剩余 unmatched 也最多，其中包含不少富氧、含 S/Cl/N 或高质量公式。

这部分需要谨慎处理，因为可能涉及污染、二次离子或外源加合。

### POMC / POMH

POMC 和 POMH 在 baseline 中已经较好。当前主要通过 adduct 与 carbon cluster 进一步提升。

剩余缺口较少，优先级低于 PDMS 细化和 ion_mode 一致性验证。

## 9. 解释注意事项

本文比较的是公式覆盖率，不是最终化学归属准确率。

需要注意：

- 一个公式可以由宽泛低分规则包生成，但仍需要人工化学审查。
- 当前 0510 验证还没有要求正/负谱 polarity 与 network `ion_mode` 严格一致。
- 更大的 network 会增加常规 `match-spectrum` 的 mass-only 候选数，因此后续必须做样品限制和 ion-mode 过滤。
- 规则包命中应理解为召回支持，不是机理证明。

## 10. 下一步建议比较

下一轮比较建议拆成两个指标：

```text
formula coverage:
  annotation formula exists in same-material network

polarity-consistent coverage:
  annotation formula exists in same-material network with compatible ion_mode
```

这样可以回答两个不同问题：

1. 当前网络能不能生成人工标注公式。
2. 当前网络能不能通过与正/负谱一致的离子模式生成该公式。

建议新增输出：

```text
outputs/summary/0510_formula_vs_ionmode_coverage.csv
outputs/summary/0510_ionmode_rule_contribution.csv
```
