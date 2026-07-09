# TOF-SIMS Formula Network v2 开发记录

日期：2026-06-24

## 背景

实验室沟通后，v2 的目标从“尽量召回公式”调整为“面向纯物质 TOF-SIMS 的机理候选网络”。因此 v2 不再默认依赖外源 adduct、通用 neutral loss、parent dimer 和材料补丁式 rule packs，而是优先表达单个物质内部的碎片、得失电荷/得失 H、片段重组和路径关联。

## 当前实现位置

新增模块：

- `tofsims_formula_network/network_v2.py`

新增命令：

```bash
python -m tofsims_formula_network.cli build-network-v2 --config config/default.yaml
```

新增输出目录：

- `outputs/networks_v2/`
- `outputs/summary/network_v2_build_summary.csv`

## v2 核心原则

1. 网络生成只针对一个物质独立进行。
2. 多物质网络可以后续合并分析，但生成阶段不跨物质组合。
3. 当前版本不引入 AI 生成结果做交叉筛选。
4. 输出不只给公式，还保留节点、边、来源路径和分叉关系。
5. 相同 `formula + ion_mode + charge` 的候选会在公式层汇总，并根据多路径支持提高 `formula_score`。

## 当前默认关闭/不使用的 v1 规则

v2 当前不使用：

- 外源 adduct：例如 `Na`、`K`、`Cl`
- 通用 neutral loss
- parent dimer
- 材料补丁式 rule packs
- AI 生成结果交叉筛选

注意：v1 仍保留原逻辑。上述关闭只针对 v2 新入口。

## v2 当前生成路线

```text
单个 compound SMILES / formula
→ parent neutral node
→ RDKit fragmentation
→ fragment neutral nodes
→ fragment-fragment recombination
→ parent / fragment / recombination 的 ionization variants
→ formula-level summary
→ nodes / edges / formula_summary 输出
```

当前 ionization variants：

- `electron_loss`：公式不变，positive
- `electron_gain`：公式不变，negative
- `protonation`：`+H`，positive
- `deprotonation`：`-H`，negative

当前 recombination variants：

- `fragment_i + fragment_j`
- `fragment_i + fragment_j - H`
- `fragment_i + fragment_j - H2`

当前片段重组只发生在同一个物质内部，且最多是一轮 fragment-fragment recombination。

## 输出文件说明

每个物质输出 4 类文件。

`<compound_id>_nodes.csv`：

- 每一行是一个路径级节点。
- 包含 `node_id`、`formula`、`ion_mode`、`charge`、`generation_type`、`operation`、`source_nodes`、`path`、`path_score`、`formula_score` 等字段。

`<compound_id>_edges.csv`：

- 每一行是一个生成关系。
- 用于表达 parent 到 fragment、fragment 到 ion、fragment 到 recombination 的连接。
- 关键字段为 `source_node`、`target_node`、`operation`、`operation_type`。

`<compound_id>_formula_summary.csv`：

- 公式层汇总表。
- 相同 `formula + ion_mode + charge` 的多个路径会汇总到同一行。
- 关键字段包括：
  - `formula_score`
  - `best_path_score`
  - `path_count`
  - `mechanism_count`
  - `source_fragment_count`
  - `generation_types`
  - `representative_path`
  - `all_node_ids`

`<compound_id>.json`：

- 包含 nodes、edges、formula_summary 的完整 JSON 版本。

## v2 打分

v2 将单条路径分和公式层分数拆开。

### 单条路径分

```text
path_score =
  structure_weight × structure_score
  + ionization_weight × ionization_score
  - H-shift penalty
  - recombination penalty
```

当前默认权重：

- `structure_weight = 0.60`
- `ionization_weight = 0.40`

结构来源分：

- `parent = 0.45`
- `fragment = 0.72`
- `recombination = 0.64`

电离相关分：

- `electron_loss = 0.55`
- `electron_gain = 0.55`
- `protonation = 0.72`
- `deprotonation = 0.72`

额外扣分：

- parent ionization penalty：`-0.18`
- 每个 broken bond：`-0.08`
- 每个 H-shift 绝对值：`-0.03`
- recombination：`-0.06`

### 公式层分数

```text
formula_score =
  best_path_score
  + path_support_bonus
  + mechanism_diversity_bonus
  + source_fragment_diversity_bonus
```

路径支持加分：

- 2 条路径：`+0.05`
- 3 条路径：`+0.08`
- 4 条及以上：`+0.10`

机制多样性加分：

- 2 种机制：`+0.05`
- 3 种及以上机制：`+0.08`

来源片段多样性加分：

- 2 个来源：`+0.04`
- 3 个及以上来源：`+0.07`

这意味着同一公式如果能从多条独立路径、多个片段或多种机制产生，会比单一路径候选更可信。

## 本次实际构建结果

命令：

```bash
/home/yao/PROGRAM/miniforge3/envs/rdkit/bin/python -m tofsims_formula_network.cli build-network-v2 --config config/default.yaml
```

汇总：

| compound_id | nodes | edges | formulas |
|---|---:|---:|---:|
| STD001 | 10 | 9 | 8 |
| PTFE | 2925 | 3533 | 83 |
| PVDF | 257 | 301 | 74 |
| ETFE | 6162 | 7371 | 347 |
| FEP | 17864 | 22234 | 66 |
| PFA | 17864 | 22234 | 66 |
| PEEK | 4264 | 5091 | 449 |
| PEEK20%GFR | 4264 | 5091 | 449 |
| PEI | 11905 | 14244 | 1012 |
| PEN | 24144 | 28919 | 1345 |
| PET | 24144 | 28919 | 1345 |
| PPS | 65 | 73 | 28 |
| PPS40%GFR | 65 | 73 | 28 |
| PI | 2390 | 2848 | 684 |
| PDMS | 6240 | 7457 | 220 |
| COC | 730 | 864 | 110 |
| EVA | 3567 | 4257 | 373 |
| Nomex | 4607 | 5503 | 575 |
| POMC | 30 | 32 | 16 |
| POMH | 30 | 32 | 16 |

## 测试

命令：

```bash
/home/yao/PROGRAM/miniforge3/envs/rdkit/bin/python -m unittest discover -s tests
```

结果：

```text
Ran 16 tests
OK
```

新增测试：

- v2 能生成单物质 lineage，并包含 fragmentation、ionization、recombination edge。
- v2 不生成外源 `Na/K/Cl` adduct，也不生成 `dimer`。
- 相同公式的多路径支持会提高 `formula_score`。

## 当前限制

1. fragment 公式仍继承当前 RDKit fragmentation 的原子计数方式，氢处理仍需和实验人员进一步校准。
2. recombination 当前只按公式组合和 `-H/-H2` 处理，还没有严格检查反应位点。
3. neutral loss 暂时完全关闭，后续如果恢复，应改成 fragment-local、结构前提明确的规则。
4. repeat_formula / extend_formula 暂未接入 v2；当前 v2 的“聚合”指片段重组，不是 repeat-unit extension。
5. `electron_loss/electron_gain` 目前表达的是电荷模式，精确 m/z 尚未扣除/加入电子质量。
6. v2 现在优先建立可解释数据结构，参数还需要结合实验谱图继续校准。

## 下一步建议

1. 和实验人员确认可接受的 recombination 类型：`A+B`、`A+B-H`、`A+B-H2` 是否合理。
2. 为 fragment 标记潜在反应位点，避免所有 fragment 两两组合。
3. 按官能团建立机制型 rule packs，而不是按材料名打补丁。
4. 重新校准 ionization 分数，区分正/负离子模式下的稳定基团。
5. 将 v2 formula_summary 与真实谱图做质量匹配评估，但暂不让 AI 生成结果参与基础规则。
