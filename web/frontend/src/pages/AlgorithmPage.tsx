export default function AlgorithmPage() {
  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Algorithm Reference</h2>
        <p className="text-sm text-gray-500 mt-1">TOF-SIMS Formula Network v4.3 — complete pipeline documentation</p>
      </div>

      {/* Main Flow */}
      <Section title="一、主流程 (network_v2.py)">
        <pre className="text-xs font-mono text-gray-700 bg-gray-50 rounded-lg p-4 overflow-x-auto leading-relaxed">{`
  SMILES 输入
  │
  ├─ Step 1: RDKit 解析分子 (AddHs)
  ├─ Step 2: 生成母体节点 (parent neutral)
  ├─ Step 3: 枚举可断裂键 → 生成 fragment neutral 节点
  │           └─ v4.0 键型感知规则 (5 种)
  ├─ Step 4: Fragment H-shift (±H)
  ├─ Step 5: 位点约束重组 (A+B 组合)
  ├─ Step 6: Feature rule 候选生成
  ├─ Step 7: 电离变体 (4 种)
  ├─ Step 8: Formula 汇总 (去重 + 多路径加分)
  └─ 输出: nodes.csv / edges.csv / formula_summary.csv / .json`}</pre>
      </Section>

      {/* Step 3: Bond Break Rules */}
      <Section title="二、Step 3: 断键规则 (fragmentation.py)">
        <SubTitle>全局默认</SubTitle>
        <ul className="text-sm text-gray-600 space-y-0.5 ml-4 mb-3">
          <li>• 仅单键、仅重原子-重原子</li>
          <li>• 禁环内键、禁芳香键</li>
          <li>• 最多 2 键断裂 · 每碎片最少 2 个重原子</li>
          <li>• 单材料最多 20,000 个碎片</li>
        </ul>

        <SubTitle>v4.0 键型感知覆盖 (5 种)</SubTitle>
        <Table>
          <thead><tr>
            <Th>键型</Th><Th>允许环内断裂</Th><Th>允许芳香断裂</Th><Th>允许单原子</Th><Th>受影响材料</Th>
          </tr></thead>
          <tbody>
            <Tr v1="C-S" v2="✓" v3="✓" v4="✓" v5="PPS" green />
            <Tr v1="Si-O" v2="✓" v3="—" v4="✓" v5="PDMS" green />
            <Tr v1="C-N" v2="✓" v3="—" v4="—" v5="PI" green />
            <Tr v1="C-O (ester)" v2="✓" v3="—" v4="—" v5="PEI" green />
            <Tr v1="C-F" v2="—" v3="—" v4="✓" v5="PTFE/PVDF/ETFE/FEP/PFA" green />
          </tbody>
        </Table>
      </Section>

      {/* Step 4: H-shift */}
      <Section title="三、Step 4: Fragment H-shift">
        <Table>
          <thead><tr><Th>操作</Th><Th>配置</Th></tr></thead>
          <tbody>
            <Tr v1="fragment − H" v2="shifts: [-1, 1]" />
            <Tr v1="fragment + H" v2="enabled: true" />
          </tbody>
        </Table>
        <p className="text-xs text-gray-400 mt-2">
          H-shift 节点 generation_type = fragment_h_shift，仅接 electron_loss/gain 电离，不接 protonation/deprotonation。
        </p>
      </Section>

      {/* Step 5: Recombination */}
      <Section title="四、Step 5: 位点约束重组">
        <Table>
          <thead><tr><Th>允许配对</Th><Th>机制</Th></tr></thead>
          <tbody>
            <Tr v1="F⁻ + G⁻" v2="dehydrogenative_coupling" />
            <Tr v1="F⁰ + G⁻" v2="single_dehydrogenative_recombination" />
            <Tr v1="F⁺ + G⁻" v2="h_transfer_recombination" />
          </tbody>
        </Table>
        <p className="text-xs text-gray-400 mt-2">
          位点兼容: &#123;C,C&#125;, &#123;C,O&#125;, &#123;C,N&#125;, &#123;C,S&#125;, &#123;Si,O&#125; · 最多 5000 对 · 质量 &lt; 2000 Da
        </p>
      </Section>

      {/* Step 6: Feature Rules */}
      <Section title="五、Step 6: Feature Rules (15 个规则包)">
        <SubTitle>8 个结构特征检测</SubTitle>
        <Table>
          <thead><tr><Th>特征</Th><Th>SMARTS / 方法</Th></tr></thead>
          <tbody>
            <Tr v1="fluorocarbon_motif" v2="C-F 键存在" />
            <Tr v1="aromatic_ring" v2="任何芳香原子" />
            <Tr v1="sulfur_aromatic" v2="S 邻接芳香环" />
            <Tr v1="acetal_or_ether" v2="O-C-O 或 C-O-C" />
            <Tr v1="carbonyl" v2="[#6]=[OX1]" />
            <Tr v1="imide" v2="#7;D3([#6]=[OX1])([#6]=[OX1])" />
            <Tr v1="amide" v2="[#7;D3]#6(=[OX1])" />
            <Tr v1="cyclic_aliphatic" v2="非芳香环存在" />
          </tbody>
        </Table>

        <SubTitle className="mt-4">15 个规则包</SubTitle>
        <div className="overflow-x-auto">
          <Table>
            <thead><tr>
              <Th>#</Th><Th>规则包</Th><Th>触发条件</Th><Th>公式数</Th><Th>约束</Th>
            </tr></thead>
            <tbody>
              <Tr v1="1" v2="fluorocarbon" v3="C-F 键" v4="17" v5="strict=False" />
              <Tr v1="2" v2="hydrofluorocarbon" v3="C-F + C-H 键" v4="8" v5="strict=False" />
              <Tr v1="3" v2="acetal_oxonium" v3="acetal_or_ether" v4="21" v5="strict=False" />
              <Tr v1="4" v2="aromatic_stable" v3="aromatic_ring" v4="5" v5="strict=True" />
              <Tr v1="5" v2="sulfur_aromatic" v3="sulfur_aromatic" v4="7" v5="strict=True" />
              <Tr v1="6" v2="carbonyl" v3="carbonyl" v4="11" v5="strict=True" />
              <Tr v1="7" v2="imide" v3="imide" v4="6" v5="strict=True" />
              <Tr v1="8" v2="amide" v3="amide" v4="6" v5="strict=True" />
              <Tr v1="9" v2="cyclic_aliphatic" v3="cyclic_aliphatic" v4="22" v5="strict=True" />
              <Tr v1="10" v2="hydrocarbon_small" v3="任何含 C" v4="30" v5="strict=True" />
              <Tr v1="11" v2="oxygenated_small" v3="含 O" v4="16" v5="strict=True" />
              <Tr v1="12" v2="nitrogenated_small" v3="含 N" v4="8" v5="strict=True" />
              <Tr v1="13" v2="sulfurated_small" v3="含 S" v4="7" v5="strict=True" />
              <Tr v1="14" v2="siloxane_small" v3="含 Si" v4="23" v5="strict=False" />
              <Tr v1="15" v2="acetate_ethylene" v3="carbonyl + 无芳香" v4="9" v5="strict=False" />
            </tbody>
          </Table>
        </div>
      </Section>

      {/* Step 7: Ionization */}
      <Section title="六、Step 7: 电离变体 (4 种)">
        <Table>
          <thead><tr>
            <Th>操作</Th><Th>ion_mode</Th><Th>charge</Th><Th>公式变化</Th><Th>H-shift</Th>
          </tr></thead>
          <tbody>
            <Tr v1="electron_loss" v2="positive" v3="+1" v4="不变" v5="0" />
            <Tr v1="electron_gain" v2="negative" v3="−1" v4="不变" v5="0" />
            <Tr v1="protonation" v2="positive" v3="+1" v4="+H" v5="+1" />
            <Tr v1="deprotonation" v2="negative" v3="−1" v4="−H" v5="−1" />
          </tbody>
        </Table>
        <p className="text-xs text-gray-400 mt-2">
          fragment_h_shift 节点仅接 electron_loss/gain。parent 电离有额外 penalty (−0.18)。
        </p>
      </Section>

      {/* Step 8: Scoring */}
      <Section title="七、Step 8: 公式层评分">
        <p className="text-sm text-gray-700 mb-2 font-medium">单节点 path_score:</p>
        <pre className="text-xs font-mono text-gray-600 bg-gray-50 rounded-lg p-3 mb-3 overflow-x-auto">
{`path_score = 0.60 × structure_score + 0.40 × ionization_score
           − 0.03 × |h_shift|
           − 0.06 (if recombination)
           + mass_prior (+0.05 if 25–200 Da, −0.02/100Da if >500)`}</pre>

        <p className="text-sm text-gray-700 mb-2 font-medium">structure_score (按 generation_type):</p>
        <Table>
          <thead><tr><Th>generation_type</Th><Th>base</Th><Th>rule_pack 覆盖</Th></tr></thead>
          <tbody>
            <Tr v1="parent" v2="0.45" v3="—" />
            <Tr v1="fragment" v2="0.72" v3="—" />
            <Tr v1="fragment_h_shift" v2="0.68" v3="—" />
            <Tr v1="recombination" v2="0.64" v3="—" />
            <Tr v1="feature_rule" v2="0.70" v3="HC=0.48, O/N/S=0.42, siloxane=0.42" />
          </tbody>
        </Table>

        <p className="text-sm text-gray-700 mt-3 mb-2 font-medium">formula_score (去重后):</p>
        <pre className="text-xs font-mono text-gray-600 bg-gray-50 rounded-lg p-3 overflow-x-auto">
{`formula_score = best_path_score
              + path_support_bonus    (2路+0.05, 3路+0.08, 4路+0.10)
              + mechanism_diversity   (2种+0.05, 3种+0.08)
              + source_fragment_diversity (2源+0.04, 3源+0.07)`}</pre>
      </Section>

      {/* Post-processing */}
      <Section title="八、后处理层 (不参与生成，仅用于报告)">
        <Table>
          <thead><tr><Th>层</Th><Th>模块</Th><Th>功能</Th></tr></thead>
          <tbody>
            <Tr v1="诊断标签" v2="specificity.py" v3="5 标签分类 + 跨材料频率" />
            <Tr v1="模式诊断" v2="pattern_diagnostics.py" v3="POM pattern score" />
            <Tr v1="证据整合" v2="evidence_report.py" v3="v3.0 五层报告" />
            <Tr v1="评分校准" v2="score_calibration.py" v3="v5.1 evidence-prior (实验性)" />
            <Tr v1="四指标评价" v2="evaluation_annotated.py" v3="0510 标注公式匹配" />
            <Tr v1="频谱评价" v2="evaluation_v2.py" v3="m/z 容差匹配" />
            <Tr v1="错误归因" v2="error_attribution.py" v3="missing vs ranking 分类" />
          </tbody>
        </Table>
      </Section>
    </div>
  )
}

/* ── Reusable layout components ── */

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <h3 className="font-semibold text-gray-800 mb-3">{title}</h3>
      {children}
    </div>
  )
}

function SubTitle({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return <p className={`text-sm font-medium text-gray-600 mb-2 ${className}`}>{children}</p>
}

function Table({ children }: { children: React.ReactNode }) {
  return (
    <table className="w-full text-sm border-collapse">
      {children}
    </table>
  )
}

function Th({ children }: { children: React.ReactNode }) {
  return (
    <th className="text-left text-xs font-medium text-gray-500 bg-gray-50 px-2 py-1.5 border-b border-gray-200 first:rounded-l last:rounded-r">
      {children}
    </th>
  )
}

function Tr({ v1, v2, v3, v4, v5, green }: {
  v1: string; v2?: string; v3?: string; v4?: string; v5?: string; green?: boolean
}) {
  return (
    <tr className={`border-b border-gray-100 ${green ? 'bg-green-50/30' : ''}`}>
      <Td mono={!green}>{v1}</Td>
      {v2 !== undefined && <Td>{v2}</Td>}
      {v3 !== undefined && <Td>{v3}</Td>}
      {v4 !== undefined && <Td>{v4}</Td>}
      {v5 !== undefined && <Td mono>{v5}</Td>}
    </tr>
  )
}

function Td({ children, mono }: { children: React.ReactNode; mono?: boolean }) {
  return (
    <td className={`px-2 py-1.5 text-xs ${mono ? 'font-mono' : ''} text-gray-700`}>
      {children}
    </td>
  )
}
