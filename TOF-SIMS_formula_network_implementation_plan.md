# TOF-SIMS 候选分子式网络生成与 RF 结果校准模块：Codex 实施方案

## 0. 项目背景与目标

当前大项目的目标是：根据 TOF-SIMS 实验谱图，分析并给出可能对应的物质/分子式。现有技术路线已经实现：

1. 从公开数据建立分子库；
2. 对实验谱图中的质量数 `m/z`，通过随机森林模型输出多个候选分子式。

本实施方案新增一个独立模块：

> 从纯物质分子结构出发，基于化学图规则生成该物质在 TOF-SIMS 中可能出现的断裂、脱氢/加氢、加合、二聚体、同源碎片重组等候选分子式网络，并用该网络对随机森林输出的候选分子式进行校准、筛选和重排序。

本模块**不做 DFT/MD**，也**不预测峰强**。第一阶段目标是做一个稳定、可验证、可扩展的工程原型。

---

## 1. 设计原则

### 1.1 只做“分子式网络”，不做完整 TOF-SIMS 机理模拟

本模块的核心问题是：

> 给定母体分子结构，哪些分子式可以通过相对合理的结构断裂、加合、脱氢、聚合或重组路径得到？

因此输出应是：

```text
母体结构 -> 候选分子式集合 -> 生成路径 -> 规则评分 -> 与实验峰/RF候选的匹配结果
```

不要输出“该峰强度为多少”或“完整理论谱图”。最多输出 high / medium / low plausibility。

### 1.2 模块定位

随机森林模块负责：

```text
实验 m/z -> 候选分子式列表
```

本模块负责：

```text
母体分子结构 -> 可生成分子式网络
```

最终融合逻辑：

```text
RF候选分子式 ∩ 结构网络生成分子式 = 更可信候选
```

### 1.3 优先支持纯物质

第一版以纯物质标准品为对象，不处理复杂混合物中的跨分子重组。

允许：

```text
同一母体分子内部碎片重组
母体 + 自身碎片
母体二聚体
```

暂不允许：

```text
不同母体分子之间任意碎片重组
未知基质碎片参与重组
没有来源约束的任意元素加合
```

---

## 2. 推荐项目目录结构

Codex 请在项目根目录下创建以下结构。已有真实谱图 txt 数据在 `data/` 文件夹中，不要覆盖原始数据。

```text
tof_formula_network/
├── README.md
├── pyproject.toml
├── requirements.txt
├── config/
│   └── default.yaml
├── data/
│   ├── spectra/                 # 真实 TOF-SIMS txt 谱图，或直接存放 txt
│   ├── compounds.csv             # 纯物质分子结构表，后续人工补充
│   └── rf_candidates.csv         # 随机森林输出候选分子式，后续接入
├── outputs/
│   ├── parsed_spectra/
│   ├── networks/
│   ├── matches/
│   ├── reports/
│   └── summary/
├── src/
│   └── tofsims_formula_network/
│       ├── __init__.py
│       ├── cli.py
│       ├── formula.py
│       ├── spectrum_io.py
│       ├── molecule_io.py
│       ├── fragmentation.py
│       ├── ion_rules.py
│       ├── network.py
│       ├── matching.py
│       ├── scoring.py
│       ├── reporting.py
│       └── utils.py
└── tests/
    ├── test_formula.py
    ├── test_spectrum_io.py
    ├── test_fragmentation.py
    ├── test_ion_rules.py
    └── test_matching.py
```

如果当前项目已有目录结构，可以不强行新建根目录，但请保证源码、配置、原始数据、输出结果分开。

---

## 3. 依赖环境

建议使用 Python 3.10 或 3.11。

`requirements.txt` 建议：

```text
rdkit
pandas
numpy
pyyaml
networkx
tqdm
pytest
```

说明：

- `rdkit`：读取 SMILES/SDF、解析分子图、计算分子式；
- `pandas`：处理谱图、RF结果、输出表格；
- `networkx`：可选，用于保存和导出分子式网络；
- `pyyaml`：读取规则开关和权重配置；
- `pytest`：单元测试。

---

## 4. 输入文件规范

### 4.1 纯物质结构表：`data/compounds.csv`

第一版需要人工准备一个标准品/纯物质结构表。

建议列：

```csv
compound_id,name,smiles,formula,group,notes
STD001,Toluene,Cc1ccccc1,C7H8,small_organic,
STD002,Bisphenol_A,CC(C)(c1ccc(O)cc1)c1ccc(O)cc1,C15H16O2,polymer_additive,
```

字段说明：

| 字段 | 必填 | 说明 |
|---|---:|---|
| compound_id | 是 | 唯一ID |
| name | 是 | 物质名称 |
| smiles | 是 | 分子结构，优先用 canonical SMILES |
| formula | 否 | 可人工提供；如果为空，由 RDKit 计算 |
| group | 否 | small_organic / polymer_additive / contaminant 等 |
| notes | 否 | 备注 |

第一阶段只要求支持 SMILES。SDF/MOL 可作为后续扩展。

### 4.2 谱图 txt 数据：`data/` 或 `data/spectra/`

真实谱图 txt 已在 `data/` 文件夹中。Codex 需要先实现一个鲁棒解析器，自动识别以下格式：

```text
m/z intensity
15.023 1023
27.018 5021
```

或：

```text
Mass,Intensity
15.023,1023
27.018,5021
```

或：

```text
# comment lines
15.023	1023
27.018	5021
```

解析要求：

1. 支持空格、tab、逗号分隔；
2. 忽略空行和注释行；
3. 自动识别前两列数值列作为 `mz` 和 `intensity`；
4. 如果有表头，保留表头信息；
5. 如果无法识别，输出清晰错误，不要静默失败；
6. 原始 txt 不可修改；
7. 解析后的标准化结果保存到 `outputs/parsed_spectra/*.csv`。

标准输出格式：

```csv
spectrum_id,mz,intensity,source_file
sample001,15.023,1023,data/sample001.txt
sample001,27.018,5021,data/sample001.txt
```

### 4.3 随机森林候选结果：`data/rf_candidates.csv`

第一版预留接口。建议格式：

```csv
spectrum_id,peak_mz,candidate_formula,rf_rank,rf_score
sample001,91.054,C7H7,1,
sample001,91.054,C3H7O3,2,
sample001,105.070,C8H9,1,
```

字段说明：

| 字段 | 必填 | 说明 |
|---|---:|---|
| spectrum_id | 是 | 谱图ID |
| peak_mz | 是 | 峰 m/z |
| candidate_formula | 是 | RF输出候选分子式 |
| rf_rank | 否 | RF排序；如果没有则为空 |
| rf_score | 否 | RF置信度；如果没有则为空 |

当前用户说明 RF 目前只输出“单纯分子式”，不一定有概率。代码中需要允许 `rf_rank` 和 `rf_score` 缺失。

---

## 5. 配置文件：`config/default.yaml`

Codex 请创建默认配置文件，所有规则开关和权重都从 YAML 读取。

```yaml
project:
  name: "tofsims_formula_network"

io:
  data_dir: "data"
  spectra_glob: "data/**/*.txt"
  compounds_file: "data/compounds.csv"
  rf_candidates_file: "data/rf_candidates.csv"
  output_dir: "outputs"

spectrum:
  min_mz: 1.0
  max_mz: 2000.0
  min_intensity: 0.0
  top_n_peaks: 300
  normalize_intensity: true
  peak_match_ppm: 20
  peak_match_da: 0.01

fragmentation:
  max_bond_breaks: 2
  max_fragment_depth: 2
  min_heavy_atoms_per_fragment: 2
  break_heavy_atom_bonds_only: true
  allow_ring_bond_break: false
  allow_aromatic_bond_break: false
  max_generated_formulas_per_compound: 20000

ion_modes:
  positive: true
  negative: true

ion_rules:
  parent_ion: true
  h_shift: true
  h_shift_range: [-2, -1, 0, 1, 2]
  common_adducts_positive: ["H", "Na", "K"]
  common_adducts_negative: ["-H", "Cl", "O", "OH"]
  neutral_losses: ["H2", "H2O", "CO", "CO2", "NH3", "CH3", "OH", "HCl", "HF"]
  dimers: true
  parent_fragment_clusters: true
  fragment_recombination: true
  max_recombined_fragments: 2

formula:
  allowed_elements: ["H", "C", "N", "O", "F", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "K", "Ca", "Ti", "Fe", "Cu", "Zn", "Br", "I"]
  allow_external_adduct_elements: true
  electron_mass_correction: false

scoring:
  base_parent: 1.00
  base_fragment: 0.75
  penalty_per_broken_bond: 0.15
  penalty_per_h_shift: 0.05
  penalty_neutral_loss: 0.10
  penalty_non_h_adduct: 0.12
  penalty_dimer: 0.20
  penalty_recombination: 0.25
  bonus_rf_match: 0.30
  bonus_multi_peak_support: 0.05
  min_score: 0.0
  max_score: 1.0

report:
  write_json_network: true
  write_csv_matches: true
  write_markdown_report: true
```

---

## 6. 核心数据结构

### 6.1 FormulaRecord

建议用 `dataclass`。

```python
@dataclass
class FormulaRecord:
    formula: str
    counts: dict[str, int]
    exact_mass: float
    ion_mode: str              # "positive" / "negative" / "both" / "neutral"
    charge: int                # +1 / -1 / 0
    source_compound_id: str
    source_name: str
    generation_type: str       # parent / fragment / neutral_loss / adduct / dimer / recombination
    path: list[str]
    broken_bonds: int
    h_shift: int
    adduct: str | None
    neutral_losses: list[str]
    fragment_atom_indices: list[int] | None
    score: float
```

### 6.2 MatchRecord

```python
@dataclass
class MatchRecord:
    spectrum_id: str
    peak_mz: float
    intensity: float | None
    rf_formula: str
    network_formula: str
    source_compound_id: str
    source_name: str
    mass_error_da: float
    mass_error_ppm: float
    network_score: float
    final_score: float
    generation_type: str
    path: str
```

---

## 7. 模块实现细节

## 7.1 `formula.py`

负责分子式解析、标准化、质量计算和公式加减。

必须实现：

```python
parse_formula(formula: str) -> dict[str, int]
format_formula(counts: dict[str, int]) -> str
add_formula(a: dict, b: dict) -> dict
subtract_formula(a: dict, b: dict) -> dict | None
exact_mass(counts: dict[str, int]) -> float
is_valid_formula(counts: dict[str, int], allowed_elements: list[str]) -> bool
normalize_formula_string(formula: str) -> str
mass_error(observed_mz: float, theoretical_mz: float) -> tuple[float, float]
```

### 7.1.1 分子式排序规则

输出分子式采用 Hill system 风格：

1. 如果含 C：先 C，再 H，再其他元素按字母顺序；
2. 如果不含 C：全部元素按字母顺序；
3. 数量为 1 时省略数字。

例如：

```text
C7H7
C15H16O2
NaCl
H2O
```

### 7.1.2 单同位素质量表

第一版内置 monoisotopic mass 表，至少包括：

```python
MASS = {
    "H": 1.00782503223,
    "C": 12.00000000000,
    "N": 14.00307400443,
    "O": 15.99491461957,
    "F": 18.99840316273,
    "Na": 22.9897692820,
    "Mg": 23.985041697,
    "Al": 26.98153853,
    "Si": 27.97692653465,
    "P": 30.97376199842,
    "S": 31.9720711744,
    "Cl": 34.968852682,
    "K": 38.9637064864,
    "Ca": 39.962590863,
    "Ti": 47.94794198,
    "Fe": 55.93493633,
    "Cu": 62.92959772,
    "Zn": 63.92914201,
    "Br": 78.9183376,
    "I": 126.9044719,
}
```

### 7.1.3 注意事项

- 分子式中不能出现负元素数；
- 不认识的元素直接报错；
- RF候选分子式可能格式不统一，需统一为规范格式再比较；
- 公式比较必须比较元素计数字典，不要直接比较字符串。

---

## 7.2 `spectrum_io.py`

负责读取真实 txt 谱图。

必须实现：

```python
find_spectrum_files(data_dir: str) -> list[Path]
read_spectrum_txt(path: Path) -> pd.DataFrame
standardize_spectrum(df: pd.DataFrame, spectrum_id: str, source_file: str) -> pd.DataFrame
write_parsed_spectrum(df: pd.DataFrame, output_path: Path) -> None
```

### 7.2.1 解析策略

1. 读取文件前 30 行，判断分隔符；
2. 尝试 `pandas.read_csv`，分隔符依次为：逗号、tab、任意空白；
3. 如果有非数值表头，自动跳过或作为表头；
4. 在所有列中找到前两个可转换为 float 的列；
5. 第一数值列作为 `mz`，第二数值列作为 `intensity`；
6. 删除无法转换的行；
7. 删除 `mz <= 0` 的行；
8. 按 `mz` 升序排序；
9. 输出统一列：`spectrum_id, mz, intensity, source_file`。

### 7.2.2 谱图预处理

第一版做轻量处理即可：

```python
filter_mz_range(df, min_mz, max_mz)
filter_intensity(df, min_intensity)
normalize_intensity_to_100(df)
select_top_n_peaks(df, top_n)
```

不要做复杂去噪、基线校正和峰拟合。

---

## 7.3 `molecule_io.py`

负责读取 `compounds.csv` 并用 RDKit 解析分子。

必须实现：

```python
read_compounds(path: Path) -> pd.DataFrame
mol_from_smiles(smiles: str) -> Chem.Mol
get_formula_from_mol(mol: Chem.Mol) -> str
validate_compound_row(row) -> None
```

要求：

1. SMILES 无法解析时，记录错误并跳过该物质；
2. 如果 `formula` 缺失，用 RDKit 自动计算；
3. 如果人工 formula 和 RDKit formula 不一致，输出 warning；
4. 对分子加显式 H：`Chem.AddHs(mol)`，用于后续按原子计数切割。

---

## 7.4 `fragmentation.py`

负责从分子图生成结构片段。

### 7.4.1 基本思路

将分子视为图：

```text
原子 = 节点
化学键 = 边
```

枚举可以断裂的重原子键，删除 1 根或 2 根键，得到连通子图。每个连通子图对应一个候选片段。

### 7.4.2 必须实现

```python
get_breakable_bonds(mol, config) -> list[int]
break_bonds_and_get_components(mol, bond_indices: tuple[int, ...]) -> list[Fragment]
generate_fragments(mol, compound_id, config) -> list[Fragment]
fragment_to_formula(fragment, mol) -> dict[str, int]
```

`Fragment` 建议：

```python
@dataclass
class Fragment:
    atom_indices: tuple[int, ...]
    broken_bond_indices: tuple[int, ...]
    counts: dict[str, int]
    formula: str
    heavy_atom_count: int
    path: list[str]
```

### 7.4.3 可断裂键规则

第一版建议：

默认允许：

```text
单键 C-C, C-O, C-N, C-S, C-Si, Si-O 等重原子键
```

默认禁止：

```text
H-X 键
芳香键
环内键
双键/三键
```

配置控制：

```yaml
allow_ring_bond_break: false
allow_aromatic_bond_break: false
break_heavy_atom_bonds_only: true
```

### 7.4.4 多键断裂限制

如果 `max_bond_breaks = 2`，则枚举：

```python
for k in [1, 2]:
    for bond_combo in combinations(breakable_bonds, k):
        ...
```

必须设置上限：

```yaml
max_generated_formulas_per_compound: 20000
```

如果超过上限，停止生成并输出 warning。

### 7.4.5 片段去重

不同路径可能生成相同分子式。不要丢弃路径信息。应聚合为：

```python
formula -> [path1, path2, path3]
```

最终该分子式的得分取最高路径得分，报告中保留 Top 3 路径。

---

## 7.5 `ion_rules.py`

负责将母体或片段分子式转化为可能的离子分子式。

### 7.5.1 母体相关规则

正离子模式：

```text
[M]+
[M+H]+
[M-H]+
[M+Na]+
[M+K]+
```

负离子模式：

```text
[M]-
[M-H]-
[M+O]-
[M+OH]-
[M+Cl]-
```

注意：输出的 `formula` 只记录元素组成，不写电荷符号。例如 `[M+H]+` 输出 `C7H9`，charge 记录为 `+1`。

### 7.5.2 H-shift 规则

对母体和片段允许：

```text
-H2, -H, +H, +H2
```

对应配置：

```yaml
h_shift_range: [-2, -1, 0, 1, 2]
```

约束：

- 减 H 后 H 数不能小于 0；
- 加 H 不应无限制，第一版最多 +2；
- H-shift 次数越多，得分越低。

### 7.5.3 中性损失规则

常见中性损失：

```text
H2, H2O, CO, CO2, NH3, CH3, OH, HCl, HF
```

实现方式：

```python
apply_neutral_loss(counts, loss_formula) -> new_counts | None
```

约束：

- 元素数量不足时不能损失；
- `H2O` 需要至少 O1H2；
- `CO2` 需要至少 C1O2；
- `NH3` 需要至少 N1H3；
- `HCl` 需要至少 H1Cl1；
- `HF` 需要至少 H1F1；
- 第一版可以只做公式约束，后续再加入官能团约束。

### 7.5.4 加合规则

正离子模式默认加合：

```text
+H, +Na, +K
```

负离子模式默认加合：

```text
-H, +Cl, +O, +OH
```

外源元素如 Na/K/Cl 是否允许由配置决定：

```yaml
allow_external_adduct_elements: true
```

如果关闭，则母体中不存在 Na/K/Cl 时不允许生成对应加合物。

### 7.5.5 二聚体规则

正离子：

```text
[2M+H]+
[2M+Na]+
```

负离子：

```text
[2M-H]-
[2M+Cl]-
```

第一版只做母体二聚体，不做任意片段多聚。

### 7.5.6 同源碎片重组规则

只允许两个同一母体来源片段重组：

```text
fragment_i + fragment_j
```

约束：

1. 最多两个片段；
2. 两片段必须来自同一个母体分子；
3. 默认只对 Top N 片段做重组，避免组合爆炸；
4. 重组生成式的 score 低于直接断裂；
5. 如果重组后公式等于母体公式，保留但标记为 recombination。

建议第一版参数：

```yaml
fragment_recombination: true
max_recombined_fragments: 2
max_fragments_for_recombination: 100
```

---

## 7.6 `network.py`

负责生成完整候选分子式网络。

必须实现：

```python
generate_formula_network(compound_row, config) -> list[FormulaRecord]
merge_duplicate_formula_records(records) -> list[FormulaRecord]
write_network_json(records, path)
write_network_csv(records, path)
```

### 7.6.1 生成流程

```text
输入 SMILES
↓
RDKit 解析分子
↓
生成母体分子式记录
↓
枚举可断裂片段
↓
对母体和片段应用 H-shift
↓
应用正/负离子规则
↓
应用中性损失
↓
应用二聚体规则
↓
应用同源碎片重组规则
↓
去重并保留路径
↓
计算 score
↓
输出 network JSON/CSV
```

### 7.6.2 JSON 输出格式

`outputs/networks/STD001_positive_negative.json`

```json
{
  "compound_id": "STD001",
  "name": "Toluene",
  "smiles": "Cc1ccccc1",
  "parent_formula": "C7H8",
  "records": [
    {
      "formula": "C7H8",
      "exact_mass": 92.0626,
      "ion_mode": "positive",
      "charge": 1,
      "generation_type": "parent",
      "path": ["M+"],
      "broken_bonds": 0,
      "h_shift": 0,
      "adduct": null,
      "neutral_losses": [],
      "score": 1.0
    },
    {
      "formula": "C7H7",
      "exact_mass": 91.0548,
      "ion_mode": "positive",
      "charge": 1,
      "generation_type": "h_shift",
      "path": ["M", "-H", "+"],
      "broken_bonds": 0,
      "h_shift": -1,
      "adduct": null,
      "neutral_losses": [],
      "score": 0.95
    }
  ]
}
```

---

## 7.7 `matching.py`

负责将结构网络、实验谱图、RF候选结果合并。

必须实现：

```python
load_networks(network_dir) -> pd.DataFrame
load_rf_candidates(path) -> pd.DataFrame
match_rf_with_network(rf_df, network_df) -> pd.DataFrame
match_spectrum_by_mass(spectrum_df, network_df, ppm, da) -> pd.DataFrame
calculate_final_score(match_df, config) -> pd.DataFrame
```

### 7.7.1 首选匹配逻辑：分子式交集

因为 RF 输出是分子式，所以第一优先级是公式匹配：

```text
RF candidate_formula == network formula
```

匹配前必须规范化公式：

```python
normalize_formula_string("H7C7") == "C7H7"
```

### 7.7.2 m/z 辅助匹配

如果某些峰没有 RF 候选，或者用于检查质量误差，可以用 m/z 匹配：

```python
abs(observed_mz - theoretical_mass) <= max(da, observed_mz * ppm * 1e-6)
```

第一版默认：

```yaml
peak_match_ppm: 20
peak_match_da: 0.01
```

### 7.7.3 最终评分

如果 RF 没有概率，只给候选分子式，则：

```text
final_score = network_score + bonus_rf_match + multi_peak_support_bonus - mass_error_penalty
```

如果 RF 有 rank：

```text
final_score = network_score + bonus_rf_match + rf_rank_bonus + multi_peak_support_bonus - mass_error_penalty
```

如果 RF 有 score：

```text
final_score = alpha * network_score + beta * rf_score + gamma * multi_peak_support - mass_error_penalty
```

第一版可以设置：

```python
if rf_score is missing:
    rf_component = 0
else:
    rf_component = 0.3 * normalized_rf_score
```

### 7.7.4 多峰支持

如果一个母体分子网络能解释同一谱图中多个主要峰，应该提高该母体相关候选的可信度。

实现：

```python
support_count = number of matched peaks for source_compound_id in same spectrum
bonus = min(0.2, support_count * bonus_multi_peak_support)
```

---

## 7.8 `scoring.py`

负责规则评分。

建议第一版规则：

```python
def score_record(record, config):
    if record.generation_type == "parent":
        score = base_parent
    else:
        score = base_fragment

    score -= penalty_per_broken_bond * record.broken_bonds
    score -= penalty_per_h_shift * abs(record.h_shift)
    score -= penalty_neutral_loss * len(record.neutral_losses)

    if record.adduct not in [None, "H", "-H"]:
        score -= penalty_non_h_adduct

    if record.generation_type == "dimer":
        score -= penalty_dimer

    if record.generation_type == "recombination":
        score -= penalty_recombination

    return clip(score, min_score, max_score)
```

规则优先级建议：

```text
最高：母体离子、M±H
较高：单键断裂碎片、单次脱氢/加氢
中等：常见中性损失、Na/K/Cl 加合
较低：二级断裂、二聚体
最低：同源碎片重组、多步规则组合
```

---

## 7.9 `reporting.py`

负责输出用户可读报告。

必须输出：

1. 每个谱图的匹配 CSV；
2. 每个谱图的 Markdown 报告；
3. 全局 summary CSV。

### 7.9.1 匹配 CSV

`outputs/matches/sample001_matches.csv`

字段：

```csv
spectrum_id,peak_mz,intensity,rf_formula,matched_formula,compound_id,compound_name,generation_type,path,network_score,final_score,mass_error_da,mass_error_ppm
```

### 7.9.2 Markdown 报告

`outputs/reports/sample001_report.md`

内容结构：

```markdown
# TOF-SIMS Formula Network Matching Report: sample001

## 1. Input

- Spectrum: data/sample001.txt
- RF candidates: data/rf_candidates.csv
- Peak count: 300
- Matching tolerance: 20 ppm or 0.01 Da

## 2. Summary

| Metric | Value |
|---|---:|
| Total peaks | 300 |
| RF candidate formulas | 1200 |
| Network matched formulas | 85 |
| Matched major peaks | 42 |
| Candidate reduction ratio | 68% |

## 3. Top matched peaks

| m/z | intensity | RF formula | matched source | path | score |
|---:|---:|---|---|---|---:|
| 91.054 | 100.0 | C7H7 | STD001 Toluene | M - H | 0.95 |

## 4. Compound-level support

| compound | explained peaks | top formulas | score |
|---|---:|---|---:|
| Toluene | 8 | C7H7, C6H5, C7H8 | 0.88 |

## 5. Unmatched high-intensity peaks

| m/z | intensity | RF formulas |
|---:|---:|---|
| ... | ... | ... |
```

---

## 8. 命令行接口设计

在 `cli.py` 中实现以下命令。

### 8.1 解析谱图

```bash
python -m tofsims_formula_network.cli parse-spectra \
  --config config/default.yaml
```

功能：

- 搜索 `data/**/*.txt`；
- 解析所有谱图；
- 输出到 `outputs/parsed_spectra/`；
- 生成 `outputs/summary/spectrum_parse_summary.csv`。

### 8.2 生成结构网络

```bash
python -m tofsims_formula_network.cli build-network \
  --config config/default.yaml \
  --compounds data/compounds.csv
```

功能：

- 读取 compounds；
- 对每个纯物质生成正/负离子模式网络；
- 输出 JSON 和 CSV。

### 8.3 匹配 RF 候选

```bash
python -m tofsims_formula_network.cli match-rf \
  --config config/default.yaml \
  --rf data/rf_candidates.csv \
  --networks outputs/networks
```

功能：

- 读取 RF 候选分子式；
- 与结构网络公式做交集；
- 输出匹配结果。

### 8.4 匹配谱图质量峰

```bash
python -m tofsims_formula_network.cli match-spectrum \
  --config config/default.yaml \
  --spectra outputs/parsed_spectra \
  --networks outputs/networks
```

功能：

- 用 exact mass 与实验 `m/z` 做质量容差匹配；
- 用于没有 RF 候选时的辅助检查。

### 8.5 一键运行

```bash
python -m tofsims_formula_network.cli run-all \
  --config config/default.yaml
```

执行顺序：

```text
parse-spectra -> build-network -> match-rf -> match-spectrum -> report
```

---

## 9. 第一版开发任务拆分

Codex 按以下顺序实施。

### Task 1：初始化项目结构

- 创建目录；
- 创建 `requirements.txt`；
- 创建 `config/default.yaml`；
- 创建空模块文件；
- 添加 README 基本说明。

验收：

```bash
python -m pytest
```

可以运行，即使暂时没有测试。

### Task 2：实现 formula 工具

实现：

- `parse_formula`
- `format_formula`
- `exact_mass`
- `add_formula`
- `subtract_formula`
- `normalize_formula_string`

测试用例：

```python
parse_formula("C7H8") == {"C": 7, "H": 8}
normalize_formula_string("H8C7") == "C7H8"
subtract_formula(parse_formula("C7H8"), parse_formula("H")) == {"C": 7, "H": 7}
subtract_formula(parse_formula("C7H8"), parse_formula("O")) is None
```

### Task 3：实现谱图 txt 解析

- 自动读取 `data/**/*.txt`；
- 兼容空格/tab/逗号；
- 输出标准 csv；
- 输出 parse summary。

验收：

```bash
python -m tofsims_formula_network.cli parse-spectra --config config/default.yaml
```

`outputs/parsed_spectra/` 中出现 csv 文件。

### Task 4：实现 molecule 读取

- 读取 `data/compounds.csv`；
- RDKit 解析 SMILES；
- 自动计算分子式；
- 对错误行给出 warning。

验收：

给一个测试 compounds.csv：

```csv
compound_id,name,smiles,formula,group,notes
STD001,Toluene,Cc1ccccc1,C7H8,small_organic,
```

能正确读出 `C7H8`。

### Task 5：实现单键/双键断裂片段生成

- 枚举可断裂键；
- 默认不切芳香键、不切环内键、不切 H-X；
- 生成 Fragment；
- 片段公式去重。

验收：

对 toluene 应能生成甲基/苯基相关片段公式，如 `CH3`、`C6H5` 等；具体结果以 RDKit 显式 H 计数为准。

### Task 6：实现 ion rules

- H-shift；
- 正/负离子加合；
- 中性损失；
- 二聚体；
- 同源碎片重组。

验收：

对 `C7H8` 至少能生成：

```text
C7H8
C7H9
C7H7
C7H8Na
C14H17
```

### Task 7：实现 network 生成

- 对每个 compound 生成 FormulaRecord；
- 合并重复公式；
- 保存 JSON/CSV。

验收：

```bash
python -m tofsims_formula_network.cli build-network --config config/default.yaml
```

生成 `outputs/networks/*.json` 和 `*.csv`。

### Task 8：实现 RF 公式匹配

- 读取 `data/rf_candidates.csv`；
- 规范化 RF 分子式；
- 与 network formula 做交集；
- 输出 match csv。

验收：

如果 RF 中含 `C7H7`，而 network 中也有 `C7H7`，应成功匹配并输出路径。

### Task 9：实现 m/z 辅助匹配

- 根据 network exact_mass 与谱图 m/z 匹配；
- 输出 mass error Da/ppm；
- 支持 ppm 和 Da 双阈值。

### Task 10：实现报告输出

- 每个谱图生成 md report；
- 输出 top matched peaks；
- 输出 unmatched high-intensity peaks；
- 输出 compound-level support。

---

## 10. 评分与校准策略

### 10.1 第一版固定规则评分

第一版使用配置文件中的手动权重即可。

评分目标不是绝对准确，而是满足：

```text
简单路径得分高；复杂路径得分低；多峰共同支持得分提高。
```

### 10.2 标准品校准

由于项目中有标准品，后续可以做规则权重校准。

每个标准品运行后统计：

```text
规则类型 -> 命中峰数量
规则类型 -> 命中峰总强度
规则类型 -> 生成公式总数
规则类型 -> 命中率 = 命中公式数 / 生成公式数
```

推荐输出：

`outputs/summary/rule_performance.csv`

```csv
rule_type,generated_count,matched_count,matched_intensity_sum,hit_rate
parent,20,12,5400,0.60
single_bond_fragment,800,85,12000,0.106
recombination,3000,30,900,0.010
```

后续可据此调整权重：

```text
高命中率规则 -> 提高权重
低命中率且生成量巨大的规则 -> 降低权重或默认关闭
```

---

## 11. 防止候选爆炸的限制

必须实现以下保护：

1. `max_bond_breaks <= 2`；
2. `min_heavy_atoms_per_fragment >= 2`；
3. 默认不切芳香键；
4. 默认不切环内键；
5. 重组只允许两个片段；
6. 每个母体最多生成 `max_generated_formulas_per_compound` 个公式；
7. 所有规则可通过 YAML 关闭；
8. 如果超过上限，输出 warning，并在 report 中注明。

---

## 12. 第一版验收标准

### 12.1 功能验收

必须能完成：

```bash
python -m tofsims_formula_network.cli run-all --config config/default.yaml
```

并生成：

```text
outputs/parsed_spectra/*.csv
outputs/networks/*.json
outputs/networks/*.csv
outputs/matches/*.csv
outputs/reports/*.md
outputs/summary/*.csv
```

### 12.2 结果验收

对至少 3 个标准品：

1. 母体分子式必须出现在 network 中；
2. `[M+H]+` 或 `[M-H]-` 相关公式应按模式生成；
3. 主要单键断裂片段应生成；
4. RF候选中能被网络解释的公式应被标出；
5. 报告中应能看到每个匹配公式的生成路径；
6. 如果生成公式数过多，报告必须提示候选爆炸风险。

### 12.3 代码验收

```bash
pytest
```

所有测试通过。

---

## 13. 后续扩展方向

第一版完成后再考虑：

1. 官能团条件约束中性损失；
2. 芳香体系特征碎片规则；
3. 聚合物重复单元规则：`end_group + n * repeat_unit`；
4. Bi 源特异规则权重；
5. 正负离子模式分别校准；
6. 标准品数据驱动的规则权重学习；
7. 与随机森林输出 rank/score 深度融合；
8. 网络图可视化；
9. Streamlit 或简单网页界面；
10. 混合物多母体联合解释。

---

## 14. 不要在第一版做的事情

第一版不要做：

```text
DFT
MD
AIMD
真实轰击过程模拟
峰强预测
复杂自由基迁移
跨母体任意重组
过深碎片树
自动识别未知分子结构
```

这些会显著拉高复杂度，且短期内不一定提升项目可交付性。

---

## 15. 给 Codex 的最终执行要求

请 Codex 优先实现一个“能跑通真实 data 文件夹”的版本：

1. 先解析真实 txt 谱图，确认数据格式；
2. 再用 1–3 个手动输入的 SMILES 做 network demo；
3. 如果 `rf_candidates.csv` 暂时不存在，允许跳过 RF 匹配，只做 m/z 辅助匹配；
4. 所有输出放到 `outputs/`；
5. 不修改原始 `data/`；
6. 每一步都要有日志和错误提示；
7. 优先保证可运行、可检查、可扩展，不追求第一版规则完美。

