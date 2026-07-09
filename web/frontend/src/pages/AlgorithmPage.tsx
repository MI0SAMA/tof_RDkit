export default function AlgorithmPage() {
  return (
    <div className="space-y-5 max-w-4xl">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Algorithm Reference</h2>
        <p className="text-sm text-gray-500 mt-1">TOF-SIMS Formula Network v5.1 — pipeline documentation</p>
      </div>

      {/* 1. Main Flow */}
      <Section title="1. Main Pipeline (network_v2.py)">
        <pre className="text-[11px] font-mono text-gray-600 bg-gray-50 rounded-lg p-4 overflow-x-auto leading-relaxed">
{`SMILES Input
  │
  ├─ Step 1: RDKit Parse + AddHs
  ├─ Step 2: Parent Node (neutral)
  ├─ Step 3: Bond Enumeration → Fragment Nodes
  │           └─ v4.0 bond-type-aware (5 types)
  ├─ Step 4: Fragment H-Shift (±H)
  ├─ Step 5: Site-Constrained Recombination (A+B pairs)
  ├─ Step 6: Feature Rule Candidate Generation
  ├─ Step 7: Ionization Variants (4 types)
  ├─ Step 8: Formula Aggregation (dedup + multi-path bonus)
  └─ Output: nodes.csv / edges.csv / formula_summary.csv / .json`}</pre>
      </Section>

      {/* 2. Bond Break Rules */}
      <Section title="2. Bond Break Rules (fragmentation.py)">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Global Defaults</h4>
            <ul className="text-xs text-gray-600 space-y-0.5">
              <li className="flex gap-2"><Dot /> Single bonds only, heavy-atom to heavy-atom</li>
              <li className="flex gap-2"><Dot /> No ring bonds, no aromatic bonds</li>
              <li className="flex gap-2"><Dot /> Max 2 bond breaks</li>
              <li className="flex gap-2"><Dot /> Min 2 heavy atoms per fragment</li>
              <li className="flex gap-2"><Dot /> Max 20,000 fragments per compound</li>
            </ul>
          </div>
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">v4.0 Bond-Type Overrides</h4>
            <table className="w-full text-[11px]">
              <thead>
                <tr className="text-left text-gray-400 border-b">
                  <th className="pb-1 font-medium">Bond</th><th className="pb-1 font-medium">Ring</th><th className="pb-1 font-medium">Aro</th><th className="pb-1 font-medium">1-Atom</th><th className="pb-1 font-medium">Materials</th>
                </tr>
              </thead>
              <tbody>
                <BondRow type="C-S" ring ring_aro atom materials="PPS" />
                <BondRow type="Si-O" ring atom materials="PDMS" />
                <BondRow type="C-N" ring materials="PI" />
                <BondRow type="C-O (ester)" ring materials="PEI" />
                <BondRow type="C-F" atom materials="PTFE / PVDF / ETFE / FEP / PFA" />
              </tbody>
            </table>
          </div>
        </div>
      </Section>

      {/* 3. Fragment H-Shift */}
      <Section title="3. Fragment H-Shift">
        <div className="flex gap-8 items-start">
          <KV k="Shifts" v="[-1, +1]" />
          <KV k="H-shift nodes" v="generation_type = fragment_h_shift" />
          <KV k="Ionization" v="electron_loss / electron_gain only (no protonation/deprotonation)" />
        </div>
      </Section>

      {/* 4. Recombination */}
      <Section title="4. Site-Constrained Recombination">
        <table className="w-full max-w-lg text-xs">
          <thead>
            <tr className="text-left text-gray-400 border-b">
              <th className="pb-1 font-medium">Pair</th><th className="pb-1 font-medium">Mechanism</th>
            </tr>
          </thead>
          <tbody>
            <Tr a="F⁻ + G⁻" b="dehydrogenative_coupling" />
            <Tr a="F⁰ + G⁻" b="single_dehydrogenative_recombination" />
            <Tr a="F⁺ + G⁻" b="h_transfer_recombination" />
          </tbody>
        </table>
        <p className="text-[11px] text-gray-400 mt-2">
          Site compatibility: &#123;C,C&#125; &#123;C,O&#125; &#123;C,N&#125; &#123;C,S&#125; &#123;Si,O&#125; · Max 5,000 pairs · Mass &lt; 2,000 Da
        </p>
      </Section>

      {/* 5. Feature Rules */}
      <Section title="5. Feature Rules — 8 Detectors + 15 Rule Packs (feature_rules_v2.py)">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Structure Feature Detectors</h4>
            <table className="w-full text-[11px]">
              <thead><tr className="text-left text-gray-400 border-b"><th className="pb-1 font-medium">Feature</th><th className="pb-1 font-medium">SMARTS / Method</th></tr></thead>
              <tbody>
                <Tr a="fluorocarbon_motif" b="C-F bond exists" />
                <Tr a="aromatic_ring" b="Any aromatic atom" />
                <Tr a="sulfur_aromatic" b="S adjacent to aromatic ring" />
                <Tr a="acetal_or_ether" b="O-C-O or C-O-C" />
                <Tr a="carbonyl" b="[#6]=[OX1]" />
                <Tr a="imide" b="N(C=O)(C=O)" />
                <Tr a="amide" b="N-C(=O)" />
                <Tr a="cyclic_aliphatic" b="Non-aromatic ring" />
              </tbody>
            </table>
          </div>
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Rule Packs</h4>
            <table className="w-full text-[11px]">
              <thead><tr className="text-left text-gray-400 border-b"><th className="pb-1 font-medium">#</th><th className="pb-1 font-medium">Rule Pack</th><th className="pb-1 font-medium">Trigger</th><th className="pb-1 font-medium">N</th></tr></thead>
              <tbody>
                <Tr a="1" b="fluorocarbon" c="C-F bonds" d="17" />
                <Tr a="2" b="hydrofluorocarbon" c="C-F + C-H" d="8" />
                <Tr a="3" b="acetal_oxonium" c="acetal/ether" d="21" />
                <Tr a="4" b="aromatic_stable" c="aromatic ring" d="5" />
                <Tr a="5" b="sulfur_aromatic" c="aromatic S" d="7" />
                <Tr a="6" b="carbonyl" c="C=O" d="11" />
                <Tr a="7" b="imide" c="imide group" d="6" />
                <Tr a="8" b="amide" c="amide group" d="6" />
                <Tr a="9" b="cyclic_aliphatic" c="non-aromatic ring" d="22" />
                <Tr a="10" b="hydrocarbon_small" c="any C" d="30" />
                <Tr a="11" b="oxygenated_small" c="has O" d="16" />
                <Tr a="12" b="nitrogenated_small" c="has N" d="8" />
                <Tr a="13" b="sulfurated_small" c="has S" d="7" />
                <Tr a="14" b="siloxane_small" c="has Si" d="23" />
                <Tr a="15" b="acetate_ethylene" c="C=O + not aromatic" d="9" />
              </tbody>
            </table>
          </div>
        </div>
      </Section>

      {/* 6. Ionization */}
      <Section title="6. Ionization Variants (4 types)">
        <table className="w-full max-w-xl text-xs">
          <thead><tr className="text-left text-gray-400 border-b"><th className="pb-1 font-medium">Operation</th><th className="pb-1 font-medium">Mode</th><th className="pb-1 font-medium">Charge</th><th className="pb-1 font-medium">Formula Δ</th><th className="pb-1 font-medium">H-Shift</th></tr></thead>
          <tbody>
            <Tr a="electron_loss" b="positive" c="+1" d="none" e="0" />
            <Tr a="electron_gain" b="negative" c="−1" d="none" e="0" />
            <Tr a="protonation" b="positive" c="+1" d="+H" e="+1" />
            <Tr a="deprotonation" b="negative" c="−1" d="−H" e="−1" />
          </tbody>
        </table>
        <p className="text-[11px] text-gray-400 mt-2">
          fragment_h_shift nodes: electron_loss/gain only · parent ionization has extra penalty (−0.18)
        </p>
      </Section>

      {/* 7. Scoring */}
      <Section title="7. Formula Scoring (Step 8)">
        <div className="space-y-3">
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Per-Node path_score</h4>
            <CodeBlock>{`path_score = 0.60 × structure_score + 0.40 × ionization_score
           − 0.03 × |h_shift| − 0.06 (if recombination)
           + mass_prior (+0.05 for 25–200 Da, −0.02/100 Da if >500)`}</CodeBlock>
          </div>
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">structure_score Base Values</h4>
            <table className="w-full max-w-md text-xs">
              <thead><tr className="text-left text-gray-400 border-b"><th className="pb-1 font-medium">Generation Type</th><th className="pb-1 font-medium">Base</th><th className="pb-1 font-medium">Rule Pack Override</th></tr></thead>
              <tbody>
                <Tr a="parent" b="0.45" c="—" />
                <Tr a="fragment" b="0.72" c="—" />
                <Tr a="fragment_h_shift" b="0.68" c="—" />
                <Tr a="recombination" b="0.64" c="—" />
                <Tr a="feature_rule" b="0.70" c="HC=0.48, O/N/S=0.42, siloxane=0.42" />
              </tbody>
            </table>
          </div>
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Final formula_score (after dedup)</h4>
            <CodeBlock>{`formula_score = best_path_score
              + path_support_bonus     (+0.05 / +0.08 / +0.10 for 2/3/4 paths)
              + mechanism_diversity    (+0.05 / +0.08 for 2/3 types)
              + fragment_diversity     (+0.04 / +0.07 for 2/3 sources)`}</CodeBlock>
          </div>
        </div>
      </Section>

      {/* 8. v5.1 Scoring */}
      <Section title="8. v5.1 Evidence-Prior Scoring (score_calibration.py)">
        <p className="text-xs text-gray-500 mb-3">
          Replaces dependence on validated_diagnostic labels with unsupervised signals that work for all materials.
        </p>
        <CodeBlock>{`v51_score = base × 0.60 + traceability × 0.15 + rule_reliability × 0.20
          + material_family × 0.10 − complexity_penalty (max −0.12)`}</CodeBlock>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3">
          <div>
            <h4 className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-1">Traceability</h4>
            <table className="w-full text-[11px]">
              <thead><tr className="text-left text-gray-400 border-b"><th className="pb-1 font-medium">Condition</th><th className="pb-1 font-medium">Score</th></tr></thead>
              <tbody>
                <Tr a="Has fragment path" b="0.60" />
                <Tr a="Feature rule only" b="0.30" />
                <Tr a="Recombination only" b="0.25" />
                <Tr a="No path" b="0.00" />
              </tbody>
            </table>
          </div>
          <div>
            <h4 className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-1">Rule Reliability</h4>
            <table className="w-full text-[11px]">
              <thead><tr className="text-left text-gray-400 border-b"><th className="pb-1 font-medium">Condition</th><th className="pb-1 font-medium">Score</th></tr></thead>
              <tbody>
                <Tr a="validated_diagnostic" b="1.00" />
                <Tr a="validated_generic" b="0.85" />
                <Tr a="fragment + feature_rule" b="0.75" />
                <Tr a="fragment only" b="0.45" />
                <Tr a="feature_rule only" b="0.35" />
                <Tr a="recombination" b="0.30" />
              </tbody>
            </table>
          </div>
        </div>
      </Section>

      {/* 9. Post-processing */}
      <Section title="9. Post-Processing (reporting only, not used in generation)">
        <table className="w-full text-xs">
          <thead><tr className="text-left text-gray-400 border-b"><th className="pb-1 font-medium">Layer</th><th className="pb-1 font-medium">Module</th><th className="pb-1 font-medium">Function</th></tr></thead>
          <tbody>
            <Tr a="Diagnostic Tags" b="specificity.py" c="5-tier classification + cross-material frequency" />
            <Tr a="Pattern Diagnostics" b="pattern_diagnostics.py" c="POM pattern scoring" />
            <Tr a="Evidence Integration" b="evidence_report.py" c="v3.0 five-layer report" />
            <Tr a="Score Calibration" b="score_calibration.py" c="v5.1 evidence-prior (experimental)" />
            <Tr a="Annotation Evaluation" b="evaluation_annotated.py" c="0510 manual label matching" />
            <Tr a="Spectrum Evaluation" b="evaluation_v2.py" c="m/z tolerance matching" />
            <Tr a="Error Attribution" b="error_attribution.py" c="missing vs ranking classification" />
          </tbody>
        </table>
      </Section>
    </div>
  )
}

/* ── Components ── */

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <h3 className="font-semibold text-gray-800 text-sm mb-3">{title}</h3>
      {children}
    </div>
  )
}

function CodeBlock({ children }: { children: string }) {
  return (
    <pre className="text-[11px] font-mono text-gray-600 bg-gray-50 rounded-lg p-3 overflow-x-auto leading-relaxed">
      {children}
    </pre>
  )
}

function Dot() {
  return <span className="text-gray-300 select-none">·</span>
}

function KV({ k, v }: { k: string; v: string }) {
  return (
    <div>
      <div className="text-[11px] text-gray-400">{k}</div>
      <div className="text-xs text-gray-700 font-mono">{v}</div>
    </div>
  )
}

function Tr({ a, b, c, d, e }: { a: string; b?: string; c?: string; d?: string; e?: string }) {
  return (
    <tr className="border-b border-gray-50">
      <td className="py-1 pr-3 text-gray-700 font-mono text-[11px]">{a}</td>
      {b !== undefined && <td className="py-1 pr-3 text-gray-600 text-[11px]">{b}</td>}
      {c !== undefined && <td className="py-1 pr-3 text-gray-600 text-[11px] font-mono">{c}</td>}
      {d !== undefined && <td className="py-1 pr-3 text-gray-500 text-[11px]">{d}</td>}
      {e !== undefined && <td className="py-1 text-gray-500 text-[11px]">{e}</td>}
    </tr>
  )
}

function BondRow({ type, ring, ring_aro, atom, materials }: {
  type: string; ring?: boolean; ring_aro?: boolean; atom?: boolean; materials: string
}) {
  return (
    <tr className="border-b border-gray-50">
      <td className="py-1 pr-2 font-mono text-[11px] text-emerald-700">{type}</td>
      <td className="py-1 pr-2 text-[11px]">{ring ? <Ck /> : <Cross />}</td>
      <td className="py-1 pr-2 text-[11px]">{ring_aro ? <Ck /> : <Cross />}</td>
      <td className="py-1 pr-2 text-[11px]">{atom ? <Ck /> : <Cross />}</td>
      <td className="py-1 text-[11px] text-gray-500">{materials}</td>
    </tr>
  )
}

function Ck() {
  return <span className="text-emerald-500 font-medium">✓</span>
}

function Cross() {
  return <span className="text-gray-300">—</span>
}
