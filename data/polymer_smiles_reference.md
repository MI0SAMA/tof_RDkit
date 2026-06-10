# 聚合物 TOF-SIMS 标准品 SMILES 参考表

> 生成日期：2026-06-10
> 用途：为 `data/compounds.csv` 提供各材料的 repeat unit SMILES，用于分子式网络生成。
> 说明：对 TOF-SIMS 分析，使用**聚合物的重复单元 (repeat unit)** 作为"母体分子"输入 RDKit。
>       所有 SMILES 表示为 **H-封端的小分子寡聚体**（1-2 个重复单元）。

## 聚合物 SMILES 一览

| compound_id | name | repeat_unit_formula | smiles | group | notes |
|---|---|---|---|---|---|
| PTFE | Polytetrafluoroethylene | C2F4 | `C(F)(F)C(F)(F)F` | fluoropolymer | -(CF2-CF2)- 重复单元，H封端后为 CF3-CF3 |
| PVDF | Polyvinylidene Fluoride | C2H2F2 | `CC(F)F` | fluoropolymer | -(CH2-CF2)- 重复单元，H封端后为 CH3-CHF2 |
| ETFE | Ethylene-TFE copolymer | C4H4F4 | `CCC(F)(F)C(F)F` | fluoropolymer | 交替共聚 -(CH2-CH2-CF2-CF2)- |
| FEP | Fluorinated Ethylene Propylene | C5F10 | `FC(F)(F)C(F)(C(F)(F)F)C(F)(F)F` | fluoropolymer | -(CF2-CF2-CF(CF3)-CF2)-，TFE-HFP 共聚 |
| PFA | Perfluoroalkoxy Alkane | — | 同 FEP | fluoropolymer | 与 FEP 类似，侧链含全氟烷氧基，用 FEP 近似 |
| PEEK | Polyether Ether Ketone | C19H12O3 | `O=C(c1ccc(Oc2ccc(O)cc2)cc1)c1ccc(O)cc1` | engineering_plastic | 芳醚酮，重复单元含 3 个苯环 + 醚/酮桥 |
| PEEK20%GFR | PEEK + 20% Glass Fiber | — | 同 PEEK | engineering_plastic | 玻纤不参与分子离子生成，SMILES 同 PEEK |
| PEI | Polyetherimide (Ultem) | C37H24N2O6 | `Cc1ccc(Oc2ccc3c(c2)C(=O)N(c2cccc(N4C(=O)c5cc(Oc6ccc(C(C)(C)c7ccc(Oc8cc9c(cc8)C(=O)N(C)C9=O)cc7)cc6)ccc5C4=O)c2)C3=O)cc1` | engineering_plastic | 双酚A二酐 + 间苯二胺缩聚产物 |
| PEN | Polyethylene Naphthalate | C14H10O4 | `O=C(OCCO)c1ccc2ccccc2c1C(=O)OCCO` | engineering_plastic | 类似 PET，萘环替代苯环 |
| PET | Polyethylene Terephthalate | C10H8O4 | `O=C(OCCO)c1ccc(C(=O)OCCO)cc1` | engineering_plastic | 对苯二甲酸 + 乙二醇缩聚 |
| PPS | Polyphenylene Sulfide | C6H4S | `Sc1ccc(S)cc1` | engineering_plastic | -(Ph-S)- 重复单元 |
| PPS40%GFR | PPS + 40% Glass Fiber | — | 同 PPS | engineering_plastic | 玻纤不参与分子离子生成 |
| PI | Polyimide (Kapton) | C22H10N2O5 | `O=C1N(c2ccc(Oc3ccc(N4C(=O)c5ccc(C(=O)N(C)C5=O)cc4)cc3)cc2)C(=O)c2ccc(C1=O)cc2` | engineering_plastic | PMDA-ODA 型聚酰亚胺 |
| PDMS | Polydimethylsiloxane | C2H6OSi | `C[Si](C)(O)[Si](C)(C)O` | siloxane | -(Si(CH3)2-O)- 重复单元 |
| COC | Cyclic Olefin Copolymer | C7H10 | `C1CC2C=CC1C2` | specialty | 降冰片烯 (norbornene) 单元，Topas 型 COC |
| EVA | Ethylene-Vinyl Acetate | C6H10O2 | `CCC(OC(=O)C)C` | specialty | 乙烯-醋酸乙烯酯共聚，~14% VA |
| Nomex | meta-Aramid | C14H10N2O2 | `O=C(Nc1cccc(NC(=O)c2cccc(C(=O))c2)c1)` | aramid | 间位芳纶，聚间苯二甲酰间苯二胺 |
| POMC | Polyoxymethylene Copolymer | CH2O | `COC` | acetal | 共聚甲醛，重复单元 -O-CH2-，用二甲氧基甲烷 |
| POMH | Polyoxymethylene Homopolymer | CH2O | `COC` | acetal | 均聚甲醛，重复单元 -O-CH2-，用二甲氧基甲烷 |

## 各聚合物结构详情

### 1. PTFE — 聚四氟乙烯 (Teflon)
```
重复单元:  -[CF2-CF2]-
H-封端:    CF3-CF3
SMILES:    C(F)(F)C(F)(F)F
分子量:    138.01 Da (C2F6)
```

### 2. PVDF — 聚偏二氟乙烯
```
重复单元:  -[CH2-CF2]-
H-封端:    CH3-CHF2
SMILES:    CC(F)F
分子量:    66.05 Da (C2H4F2)
```

### 3. ETFE — 乙烯-四氟乙烯共聚物 (Tefzel)
```
重复单元:  -[CH2-CH2-CF2-CF2]-
H-封端:    CH3-CH2-CF2-CHF2
SMILES:    CCC(F)(F)C(F)F
分子量:    134.06 Da (C4H6F4)
```

### 4. FEP — 氟化乙烯丙烯共聚物
```
重复单元:  -[CF2-CF2-CF(CF3)-CF2]-
H-封端:    CF3-CF2-CF(CF3)-CF3
SMILES:    FC(F)(F)C(F)(C(F)(F)F)C(F)(F)F
分子量:    238.03 Da (C5F10)
```

### 5. PEEK — 聚醚醚酮
```
重复单元结构:
  -[O-Ph-O-Ph-C(=O)-Ph]-
  即: 醚 - 苯 - 醚 - 苯 - 酮 - 苯
  
SMILES:    O=C(c1ccc(Oc2ccc(O)cc2)cc1)c1ccc(O)cc1
分子量:    304.30 Da (C19H12O3)
来源:     ChEBI:53370
```

### 6. PEI — 聚醚酰亚胺 (Ultem)
```
结构: 双酚A二酐 (BPADA) + 间苯二胺 (MPD) 缩聚
含酰亚胺环 + 醚键 + 异丙基桥

SMILES 来源: Sigma-Aldrich 700193
分子量:    ~592.61 Da (C37H24N2O6)
```

### 7. PEN — 聚萘二甲酸乙二醇酯
```
类似 PET，但以萘-2,6-二羧酸替代对苯二甲酸
重复单元含萘环 + 两个酯键 + 乙二醇桥

SMILES:    O=C(OCCO)c1ccc2ccccc2c1C(=O)OCCO
分子量:    242.23 Da (C14H10O4)
```

### 8. PET — 聚对苯二甲酸乙二醇酯
```
重复单元:  -[O-CH2-CH2-O-CO-Ph-CO]-
H-封端:    HO-CH2-CH2-O-CO-Ph-CO-O-CH2-CH2-OH
SMILES:    O=C(OCCO)c1ccc(C(=O)OCCO)cc1
分子量:    194.18 Da (C10H8O4)
```

### 9. PPS — 聚苯硫醚
```
重复单元:  -[Ph-S]-
H-封端:    HS-Ph-SH (1,4-苯二硫酚)
SMILES:    Sc1ccc(S)cc1
分子量:    108.16 Da (C6H4S)
来源:     Sigma-Aldrich 427233
```

### 10. PI — 聚酰亚胺 (Kapton)
```
PMDA (均苯四甲酸二酐) + ODA (4,4'-二氨基二苯醚) 缩聚
含酰亚胺五元环 + 二苯醚桥

分子量:    ~382.31 Da (C22H10N2O5)
```

### 11. PDMS — 聚二甲基硅氧烷 (硅橡胶)
```
重复单元:  -[Si(CH3)2-O]-
典型SMILES (二聚体):  C[Si](C)(O)[Si](C)(C)O
分子量:    166.33 Da (C4H14O2Si2)
来源:     ChEBI:31498
```

### 12. COC — 环烯烃共聚物 (Topas)
```
主要结构单元: 降冰片烯 (norbornene)
SMILES:    C1CC2C=CC1C2
分子量:    94.15 Da (C7H10)
注: COC 有多种类型，此处用降冰片烯代表
```

### 13. EVA — 乙烯-醋酸乙烯酯共聚物
```
重复单元含乙烯 + 醋酸乙烯酯
用含一个 VA 单元的三聚体近似表示
SMILES:    CCC(OC(=O)C)C
分子量:    114.14 Da (C6H10O2)
注: 实际 VA 含量影响碎片分布，此处用 ~33% VA 近似
```

### 14. Nomex — 间位芳纶
```
聚间苯二甲酰间苯二胺: -[NH-Ph-NH-CO-Ph-CO]-
SMILES:    O=C(Nc1cccc(NC(=O)c2cccc(C(=O))c2)c1)
分子量:    238.24 Da (C14H10N2O2)
```

### 15. POMC / POMH — 聚甲醛 (共聚/均聚)
```
重复单元:  -[O-CH2]-
H-封端:    CH3-O-CH3 (二甲氧基甲烷)
SMILES:    COC
分子量:    46.07 Da (C2H6O)
注: POMC (共聚) 含少量 -O-CH2-CH2- 共聚单元，此处简化
```

### 16. PFA — 全氟烷氧基树脂
```
与 FEP 类似，TFE + 全氟烷氧基乙烯基醚共聚
侧链: -O-CF2-CF2-CF3 或 -O-CF3
用 FEP 结构近似表示
```

## 已知局限性

1. **共聚物近似**：ETFE、FEP、PFA、EVA、COC 均为共聚物，用单一重复单元 SMILES 近似。实际 TOF-SIMS 信号来自更复杂的序列分布。
2. **端基未考虑**：实际聚合物链端基（如 -OH、-COOH、-F）对低质量碎片有贡献。
3. **添加剂/残留物**：实际 TOF-SIMS 谱中含添加剂、残留单体、低聚物峰，本表仅覆盖主链结构。
4. **交联/支化**：部分材料可能有交联，SMILES 简化表示未包含。
5. **长链效应**：TOF-SIMS 中长链分子会有更丰富的碎片模式，单重复单元可能不足以捕获所有特征峰。建议后续用 2-3 个重复单元的寡聚体测试。

## 后续建议

1. 优先用标准品实验数据验证每个 SMILES 的碎片生成合理性
2. 对于含氟聚合物（PTFE/PVDF/ETFE/FEP/PFA），氟化学碎片规则可能需要特殊处理
3. 对于含 Si 聚合物（PDMS），Si 同位素分布显著，需在匹配中考虑
4. 对于含 S 聚合物（PPS），S 的同位素也需注意
5. PEEK20%GFR 和 PPS40%GFR 玻纤增强不影响有机分子离子，SMILES 同基体
