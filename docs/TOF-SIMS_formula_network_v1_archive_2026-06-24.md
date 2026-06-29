# TOF-SIMS Formula Network v1 留档说明

日期：2026-06-24

## 留档目的

本文件用于固定 v1 算法状态，便于后续与 v2 版本对比。v1 的核心目标是提高候选公式召回率，因此包含较宽松的公式生成规则和若干经验补充规则。v2 将转向更强调纯物质 TOF-SIMS 机理解释、单物质独立生成、路径关联和公式层多路径支持。

## v1 默认生成逻辑

v1 入口仍为：

```text
tofsims_formula_network.network.generate_formula_network()
```

命令行入口仍为：

```bash
python -m tofsims_formula_network.cli build-network --config config/default.yaml
```

v1 主要步骤：

1. 读取单个 compound 的 SMILES / formula。
2. 若 `formula` 为空，则由 RDKit 计算母体公式。
3. 生成母体 `parent`。
4. 基于 RDKit 可断键生成 `fragment`。
5. 对 parent / fragment / repeat-unit extension 结果做 H-shift。
6. 对 H-shift 后的公式套用通用 adduct。
7. 对 H-shift 后的公式套用通用 neutral loss。
8. 根据 `extend_formula` 做 repeat-unit extension。
9. 生成 parent dimer。
10. 追加 rule packs，包括 carbon cluster、siloxane fragment、external adduct。
11. 合并相同 `(formula, ion_mode, generation_type)` 的记录。
12. 输出 v1 的 `outputs/networks/*.csv` 和 `*.json`。

## v1 规则特点

v1 默认开启：

- 外源 adduct：`H`、`Na`、`K`、`-H`、`Cl`、`O`、`OH`
- 通用 neutral loss：`H2`、`H2O`、`CO`、`CO2`、`NH3`、`CH3`、`OH`、`HCl`、`HF`
- parent dimer：`2M + H`、`2M + Na`、`2M - H`、`2M + Cl`
- repeat-unit extension：`base + n × extend_formula`
- 材料相关 rule packs：
  - `carbon_cluster`
  - `siloxane_fragment`
  - `external_adduct`

## v1 打分逻辑

v1 主要使用单条记录分数：

```text
parent: 1.00
fragment: 0.75
carbon_cluster: 0.22
siloxane_fragment: 0.28
external_adduct: 0.25
```

扣分项：

- 每断 1 根键：`-0.15`
- 每 H-shift 绝对值 1：`-0.05`
- 每个 neutral loss：`-0.10`
- 非 H / -H adduct：`-0.12`
- dimer：`-0.20`
- repeat-unit extension：`-0.08 × repeat 次数`

## 已知问题

v1 适合做召回实验，但和实验室讨论后的纯物质 TOF-SIMS 机理目标存在偏差：

1. 外源 Na/K/Cl 等 adduct 更像污染物或环境离子，不适合作为纯物质默认规则。
2. 通用 neutral loss 缺少结构前提，可能重复 fragmentation 已经表达的官能团脱除。
3. parent dimer 与纯物质碎片化解释关系较弱。
4. rule packs 仍有材料补丁色彩，应改为更通用的机制规则。
5. parent 默认最高分不合理，TOF-SIMS 中母体本身未必容易得失电荷。
6. v1 输出以公式记录为主，路径、分叉和共同来源信息不足。
7. 相同 formula 的多路径支持没有被系统性纳入公式层打分。

## v1 当前保留方式

当前没有覆盖 v1 代码路径。v1 相关模块仍保留：

- `tofsims_formula_network/network.py`
- `tofsims_formula_network/ion_rules.py`
- `tofsims_formula_network/rule_packs.py`
- `tofsims_formula_network/scoring.py`

v1 输出目录仍为：

- `outputs/networks/`
- `outputs/summary/network_build_summary.csv`

v2 已作为并行实现新增，便于后续对照。
