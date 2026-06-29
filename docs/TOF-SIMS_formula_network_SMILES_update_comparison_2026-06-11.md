# TOF-SIMS Formula Network：SMILES 更新版比对与 POMC/POMH 谱图对比

> 日期：2026-06-11  
> 数据来源：`data/SMILES更新版.xlsx`、`data/compounds.csv`、`data/POMC/`、`data/POMH/`  
> 输出表格：`outputs/summary/smiles_update_comparison.csv`  
> 谱图输出：`outputs/summary/smiles_update_analysis/`

## 1. 本次任务

实验室提供了 `data/SMILES更新版.xlsx`，用于校准当前 `data/compounds.csv` 中纯物质或材料代表结构的 SMILES。

本次工作包括：

1. 将新版 xlsx 与当前 `compounds.csv` 做逐项比对。
2. 特别检查 `PPS40%GFR`、`PEEK20%GFR`、`POMC`、`POMH`。
3. 使用 POMC/POMH 的全谱数据绘制正负谱叠图。
4. 给出对后续算法和测试标记方式的建议。

## 2. 文件覆盖情况

| 项目 | 数量 |
|---|---:|
| 当前 `compounds.csv` compound_id | 20 |
| xlsx compound_id | 19 |
| 只在当前 CSV 中存在 | `STD001` |
| 只在 xlsx 中存在 | 无 |

`STD001` 是 demo 的 Toluene 行，不属于实验室这批材料更新内容。

## 3. 总体差异

新版 xlsx 的最大变化是：大部分聚合物 SMILES 使用了 `[*]` 作为链连接点，例如：

```text
POMH: [*]OC[*]
PPS:  [*]Sc1ccc([*])cc1
PTFE: [*]C(F)(F)C(F)(F)[*]
```

这比当前 `compounds.csv` 中的短链或端基近似更接近“链内重复单元”表达。

但是它不能直接无脑替换到当前程序里：

```text
RDKit CalcMolFormula("[*]OC[*]") -> CH2*2O
```

当前 `formula.py` 不支持 `*` 元素，`fragmentation.py` 也没有忽略 dummy atom 的逻辑。因此，如果要采用新版 `[*]` SMILES，需要同时做至少一项处理：

1. 在 `compounds.csv` 中为这些材料显式填写 `formula`，避免由 RDKit 自动计算含 `*` 的公式。
2. 在 fragment 生成时跳过 dummy atom，或把 dummy atom 当作连接点而非真实元素。
3. 更稳妥地，把新版 SMILES 作为 `polymer_smiles` 或 `repeat_unit_smiles` 字段保留，当前运行用有限低聚物/端基模型。

## 4. 关键材料比对

### 4.1 PPS40%GFR 与 PEEK20%GFR

你的判断是对的：这两个不是纯物质。

| compound_id | 当前处理 | xlsx 说明 | 建议 |
|---|---|---|---|
| `PEEK20%GFR` | SMILES 与 PEEK 相同 | SMILES 仅代表 PEEK 基体；玻纤应作为 SiO2/硅醇化表面单独建模 | 不要当纯 PEEK 结果解释；在算法和测试中标记为 composite |
| `PPS40%GFR` | SMILES 与 PPS 相同 | SMILES 仅代表 PPS 基体；玻纤需作为独立无机相或表面模型处理 | 不要当纯 PPS 结果解释；在算法和测试中标记为 composite |

建议后续在 `compounds.csv` 中新增字段，例如：

```text
material_type = pure_polymer / copolymer / composite / demo
matrix_compound_id = PEEK 或 PPS
filler = glass_fiber
filler_fraction = 20% 或 40%
```

这样当前 formula network 可以继续生成 PEEK/PPS 基体候选，但报告和验证时明确显示：

```text
PEEK20%GFR = PEEK matrix only; glass fiber not modeled
PPS40%GFR = PPS matrix only; glass fiber not modeled
```

这比把玻纤强行并入一个有机 SMILES 更合理。

### 4.2 POMC 与 POMH

xlsx 给出的结构信息：

| compound_id | xlsx SMILES | repeat unit | 说明 |
|---|---|---|---|
| `POMC` | `[*]OC[*]` | mainly `CH2O` | 共聚 POM 主链主要为 `-O-CH2-`，还含少量稳定单元 |
| `POMH` | `[*]OC[*]` | `CH2O` | 均聚 POM 主链单元为 `-O-CH2-` |

当前 `compounds.csv` 中二者都写作：

```text
smiles = COC
extend_formula = CH2O
```

这个近似虽然不严格，但对于当前 formula network 来说是可运行的，并且与 xlsx 的核心重复单元一致。POMC/POMH 的主要差异是聚合度、端基稳定化和少量共聚单元比例，这些不是当前公式网络能可靠区分的内容。

因此不建议为了 POMC/POMH 大改算法。更合理的做法是：

- 保持二者共享 `extend_formula = CH2O`。
- 在 notes 或 metadata 中标记：
  - `POMC`: copolymer, mainly CH2O, minor stabilizing/comonomer units
  - `POMH`: homopolymer, CH2O, degree-of-polymerization differs
- 后续报告中说明 formula network 对 POMC/POMH 的区分能力有限。

## 5. POMC/POMH 全谱对比

使用全谱 `All.TXT` 数据，按 0.05 Da bin 做最大强度重采样，并将每张谱归一化到最大强度 100。

输出文件：

```text
outputs/summary/smiles_update_analysis/pomc_pomh_positive_full_overlay.png
outputs/summary/smiles_update_analysis/pomc_pomh_positive_full_difference.png
outputs/summary/smiles_update_analysis/pomc_pomh_negative_full_overlay.png
outputs/summary/smiles_update_analysis/pomc_pomh_negative_full_difference.png
outputs/summary/smiles_update_analysis/pomc_pomh_spectral_similarity.csv
```

谱图相似度：

| mode | cosine similarity | Pearson correlation | POMC base m/z | POMH base m/z |
|---|---:|---:|---:|---:|
| positive | 0.9791 | 0.9791 | 31.0200 | 31.0206 |
| negative | 0.9938 | 0.9938 | 45.0011 | 45.0003 |

结论：

- POMC/POMH 的正谱高度相似。
- POMC/POMH 的负谱几乎重合。
- 这支持“二者组分主体相同，差异主要来自聚合度、端基或少量共聚单元”的判断。
- 当前 formula-network 层面不适合强行区分 POMC/POMH。

## 6. 其他重要差异

| compound_id | 当前问题 | xlsx 更新重点 | 建议 |
|---|---|---|---|
| `PFA` | 当前近似为 FEP 结构 | xlsx 改为 TFE-PPVE 型 PFA，repeat formula 为 representative `C7F14O` | 后续应单独更新 PFA，不再写成同 FEP |
| `COC` | 当前用单一短链结构 `CCC1CC2CCC1C2CC` | xlsx 表达为乙烯单元和降冰片烯加成单元集合，比例 variable | 保留为 copolymer，需要按牌号或比例构建代表低聚物 |
| `EVA` | 当前用单一短链结构 `CCC(OC(=O)C)C` | xlsx 表达乙烯单元 + VA 单元，比例 variable； notes 指出约 14% VA 可按 1 VA : 6 ethylene | 应作为 copolymer 处理，当前单 repeat 近似会影响召回解释 |
| `PTFE/PVDF/ETFE/FEP` | 当前多为 H/F 端基短链近似 | xlsx 改为链内重复单元 `[*]...[*]` | 需要 dummy atom 处理后再直接用于 fragmentation |
| `PEEK/PPS/PEN/PET/PI/Nomex/PEI` | 当前多为端基或短链近似 | xlsx 多改为链内重复单元 | 建议保留新版作为 repeat-unit reference，直接替换前需处理 `[*]` |

## 7. 是否应立即更新 `compounds.csv`

不建议直接一次性把 `smiles` 列替换为 xlsx 的 `[*]` SMILES。

原因：

1. 当前 RDKit 公式计算会产生 `*`，例如 `CH2*2O`。
2. 当前公式解析器不支持 dummy atom。
3. 当前 fragment 生成会把 dummy atom 当作元素 `*`，后续质量计算会失败。

建议分两步：

### 第一步：增加标记字段

先把 xlsx 信息整合为 metadata，而不是替换运行字段：

```text
repeat_unit_smiles
repeat_unit_formula
material_type
matrix_compound_id
filler
composition_note
smiles_source
```

其中：

- `smiles` 继续保留当前可运行模型。
- `repeat_unit_smiles` 保存 xlsx 中更准确的 `[*]` 表达。
- `material_type` 标记 pure / copolymer / composite。

### 第二步：算法适配 dummy atom

如果未来要让 `[*]` SMILES 直接参与网络生成，需要：

- 在 formula 计算时忽略 dummy atom 或由 `repeat_unit_formula` 覆盖。
- 在 fragmentation 中跳过 dummy atom 相关 bond 或特殊处理连接点。
- 对多组分 SMILES，例如 `[*]CC[*].[*]C1CC2CCC1C2[*]`，定义各单元比例或组合策略。

## 8. 结论与思考

1. 新版 xlsx 化学表达更准确，尤其把“短链端基近似”改为“链内重复单元/共聚单元”。
2. 但新版 SMILES 不是当前程序可直接替换的运行输入，因为 `[*]` dummy atom 会进入 RDKit formula 和 fragment 计算。
3. `PEEK20%GFR` 和 `PPS40%GFR` 应明确标记为 composite。当前 SMILES 只能代表有机基体，不能代表玻纤相。
4. `POMC` 和 `POMH` 的主体重复单元相同，全谱高度相似；当前算法不需要为了区分聚合度而大改。
5. 当前最稳妥的路线是：把 xlsx 作为 repeat-unit reference 和 metadata 引入，而不是直接覆盖 `smiles`。
6. 后续如果要进一步提高结构真实性，应先实现 dummy atom / repeat-unit 支持，再考虑替换主 SMILES。

## 9. 建议下一步

建议下一步做一个保守的数据结构升级：

```text
保留 smiles              # 当前可运行模型
新增 repeat_unit_smiles  # xlsx 校准结构
新增 material_type       # pure_polymer / copolymer / composite / demo
新增 matrix_compound_id  # 复合材料基体
新增 composition_note    # 共聚比例、玻纤说明、端基说明
```

然后在报告和验证中加入 material_type 提示：

```text
PEEK20%GFR: network represents PEEK matrix only; glass fiber not modeled.
PPS40%GFR: network represents PPS matrix only; glass fiber not modeled.
POMC/POMH: same main repeat unit; formula-network distinction is limited.
```
