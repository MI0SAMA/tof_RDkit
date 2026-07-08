import { Layers, GitBranch, Zap, Target, Shield, Atom, Scissors } from 'lucide-react'

export default function AlgorithmPage() {
  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Algorithm Architecture</h2>
        <p className="text-sm text-gray-500 mt-1">TOF-SIMS Formula Network v4.3 — bond-type-aware fragmentation</p>
      </div>

      {/* Pipeline Overview */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <Layers size={18} className="text-blue-600" /> Pipeline Overview
        </h3>
        <div className="flex items-center gap-0 text-xs font-mono flex-wrap">
          <StepBox label="SMILES" color="bg-gray-100" />
          <Arrow />
          <StepBox label="Layer 1\nConservative Frag" color="bg-blue-50" />
          <Arrow />
          <StepBox label="Layer 2\nBond-Type-Aware" color="bg-emerald-50" />
          <Arrow />
          <StepBox label="Layer 3\nFeature/Pattern" color="bg-amber-50" />
          <Arrow />
          <StepBox label="Layer 4\nResidual Empirical" color="bg-purple-50" />
          <Arrow />
          <StepBox label="Diagnostic\nScoring" color="bg-gray-100" />
        </div>
        <p className="text-xs text-gray-400 mt-3">
          v4.3 key insight: per-bond-type selective relaxation replaces one-size-fits-all conservative rules. C-S, Si-O, C-N, C-O(ester), C-F bonds now break under chemically justified conditions, providing structurally traceable paths for fragments previously requiring empirical Layer 4 rules.
        </p>
      </div>

      {/* Layer 1 */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
          <Atom size={18} className="text-blue-600" /> Layer 1 — Conservative RDKit Fragmentation
        </h3>
        <p className="text-sm text-gray-600 mb-3">
          Global bond-breaking rules on the parent SMILES. Single bonds between heavy atoms only. Default: no ring/aromatic bond breaks, min 2 heavy atoms per fragment, ≤2 bond breaks.
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
          <RuleBadge label="Parent" desc="Root molecule" />
          <RuleBadge label="Fragment" desc="Bond breaks (≤2)" />
          <RuleBadge label="H-Shift" desc="±1 H transfer" />
          <RuleBadge label="Recombination" desc="Site-constrained pairs" />
        </div>
        <div className="mt-2 text-xs text-gray-400">
          Ionization: e⁻ loss/gain · H⁺ addition/removal · max 300 fragment nodes
        </div>
      </div>

      {/* Layer 2 — NEW in v4.0 */}
      <div className="bg-white rounded-xl border border-emerald-200 p-5">
        <div className="flex items-center gap-2 mb-3">
          <Scissors size={18} className="text-emerald-600" />
          <h3 className="font-semibold text-gray-800">Layer 2 — Bond-Type-Aware Fragmentation</h3>
          <span className="text-xs bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded font-medium">v4.0 NEW</span>
        </div>
        <p className="text-sm text-gray-600 mb-3">
          Per-bond-type selective relaxation of conservative rules. Each bond type has chemical justifications for when ring/aromatic/single-atom exceptions are allowed. Every fragment now answers: "which bond broke and why?"
        </p>
        <div className="space-y-2 text-sm">
          <BondRow type="C-S" ring={true} aromatic={true} singleAtom={true}
            conditions="—" materials="PPS" impact="+11 nodes, +11pp neg recall"
            desc="Aromatic C-S bond in PPS now breakable. S⁻/HS⁻ fragments gain structural traceability." />
          <BondRow type="Si-O" ring={true} aromatic={false} singleAtom={true}
            conditions="—" materials="PDMS" impact="+48 nodes, +3pp recall"
            desc="Siloxane backbone Si-O bonds breakable inside rings." />
          <BondRow type="C-N" ring={true} aromatic={false} singleAtom={false}
            conditions="—" materials="PI" impact="+127 nodes"
            desc="Imide ring C-N bonds open. Saturates PI recall (already 78-86%)." />
          <BondRow type="C-O (ester)" ring={true} aromatic={false} singleAtom={false}
            conditions="require_carbonyl" materials="PEI" impact="+122 nodes"
            desc="Carbonyl-adjacent C-O in anhydride rings breakable. PEI recall at ceiling." />
          <BondRow type="C-F" ring={false} aromatic={false} singleAtom={true}
            conditions="—" materials="PTFE/PVDF/ETFE/FEP/PFA" impact="+3 each"
            desc="F⁻ now structurally traceable via C-F bond break path." />
        </div>
        <div className="mt-3 p-3 bg-emerald-50 rounded-lg text-xs text-emerald-700">
          <strong>Total impact:</strong> +311 nodes across 7 materials. 5 empirical Layer 4 rules replaced with structurally traceable Layer 2 paths. Non-target materials: zero impact.
        </div>
      </div>

      {/* Layer 3 */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
          <GitBranch size={18} className="text-amber-600" /> Layer 3 — Structure Feature & Pattern Rules
        </h3>
        <p className="text-sm text-gray-600 mb-3">
          RDKit substructure-triggered rule packs. Feature detectors now include carbonyl, imide, amide, and cyclic_aliphatic (v4.2+).
        </p>
        <div className="space-y-1.5 text-sm">
          <FeatureRow name="fluorocarbon_fragmentation" trigger="C-F bonds" materials="PTFE, PVDF, ETFE, FEP, PFA" />
          <FeatureRow name="acetal_oxonium_series" trigger="O-C-O acetal motif" materials="POMC, POMH" />
          <FeatureRow name="aromatic_stable_fragments" trigger="Aromatic rings" materials="PET, PEEK, PEI, PEN, PI, Nomex, PPS" />
          <FeatureRow name="sulfur_aromatic_fragments" trigger="Aromatic S" materials="PPS" />
          <FeatureRow name="carbonyl_fragmentation" trigger="C=O carbonyl" materials="PET, PEEK, PEI, PI, Nomex, EVA" />
          <FeatureRow name="imide_fragmentation" trigger="Imide O=C-N-C=O" materials="PI, PEI" />
          <FeatureRow name="amide_fragmentation" trigger="Amide N-C=O" materials="Nomex" />
          <FeatureRow name="cyclic_aliphatic_fragments" trigger="Non-aromatic rings" materials="COC" />
          <FeatureRow name="acetate_ethylene_fragments" trigger="Carbonyl + NOT aromatic" materials="EVA" />
        </div>
      </div>

      {/* Layer 4 — Reduced from v3.0 */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
          <Zap size={18} className="text-purple-600" /> Layer 4 — Residual Empirical Fragments
        </h3>
        <p className="text-sm text-gray-600 mb-3">
          Remaining empirical rules not yet covered by bond-type-aware or feature rules. Element-gated. Significantly reduced from v3.0 (5 rules replaced by Layer 2 structural paths).
        </p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-xs">
          <RuleBadge label="hydrocarbon_small" desc="C₂–C₆ (C-gated)" />
          <RuleBadge label="oxygenated_small" desc="C₁–C₃ (O-gated)" />
          <RuleBadge label="nitrogenated_small" desc="C₁–C₃ (N-gated)" />
          <RuleBadge label="sulfurated_small" desc="Thio fragments (S-gated)" />
          <RuleBadge label="siloxane_small" desc="Si₁–₂ (Si-gated, PDMS)" />
        </div>
        <div className="mt-3 text-xs text-gray-400">
          Still empirical: hydrocarbon C2-C6 (needs 3+ C-C breaks), oxygen migration, multi-step F loss, POM oligomer fragments.
        </div>
      </div>

      {/* Diagnostic Scoring */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
          <Target size={18} className="text-indigo-600" /> Diagnostic Scoring (v2.9→v4.3)
        </h3>
        <p className="text-sm text-gray-600 mb-3">
          Five-tier evidence tagging. v4.3 adds per-rule-pack structure score overrides, allowing bond-type-aware fragments to receive appropriate scores distinct from conservative fragments.
        </p>
        <div className="space-y-2 text-sm">
          <TagRow tag="validated_diagnostic" score="0.80" color="bg-green-100 text-green-800"
            desc="≤3 materials + manual annotation confirmed. Formula-driven identification." />
          <TagRow tag="validated_generic" score="0.50" color="bg-blue-100 text-blue-800"
            desc="4+ materials + annotation confirmed. Shared but validated." />
          <TagRow tag="feature_supported_candidate" score="0.30" color="bg-amber-100 text-amber-800"
            desc="Rule-supported (Layer 2 or 3), unvalidated against manual labels." />
          <TagRow tag="generic_hydrocarbon_background" score="0.00" color="bg-red-100 text-red-800"
            desc="13+ materials, pure HC. Cross-material background noise." />
          <TagRow tag="structural_candidate_only" score="0.10" color="bg-gray-100 text-gray-600"
            desc="RDKit-only candidate. Hidden by default. Now reduced via Layer 2 traceability." />
        </div>
      </div>

      {/* Scoring */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
          <Shield size={18} className="text-gray-600" /> Scoring Model (v4.3)
        </h3>
        <div className="text-sm text-gray-600 space-y-1">
          <div><code className="bg-gray-100 px-1 rounded text-xs">formula_score = path_score + path_bonus + mechanism_bonus + fragment_bonus</code></div>
          <div className="ml-4 text-xs text-gray-400">path_score = 0.60 × structure_score + 0.40 × ionization_score − penalties + mass_prior</div>
          <div className="ml-4 text-xs text-gray-400">structure_score = base(rule_pack) − 0.08 × n_broken_bonds</div>
          <div className="mt-2 text-xs text-gray-500">
            v4.3: <code className="bg-emerald-50 px-1 rounded">rule_pack_structure_scores</code> allow per-rule-pack base overrides.
            Bond-type-aware fragments get distinct scores from conservative fragments.
          </div>
        </div>
      </div>

      {/* Evidence Strategy */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-3">Material Identification Strategy</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
          <StrategyCard type="formula-driven" desc="Strong validated_diagnostic formulas. Material identified by individual diagnostic peaks." materials="PDMS" />
          <StrategyCard type="pattern-driven" desc="No diagnostic single formulas, but fragment pattern combination is unique." materials="POMC, POMH" />
          <StrategyCard type="mixed" desc="Validated formulas + pattern evidence. Combined approach." materials="COC, EVA, PET, PEEK, PEI, PEN, PI, Nomex, PPS" />
          <StrategyCard type="validation-limited" desc="Only feature_supported candidates. Insufficient for standalone ID." materials="PTFE, PVDF, ETFE, FEP, PFA" />
        </div>
      </div>

      {/* v4.3 Changelog */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-3">v3.0 → v4.3 Changelog</h3>
        <div className="space-y-2 text-sm">
          <ChangeRow version="v4.0-S" desc="C-S bond-type-aware: allow ring + aromatic break + single-atom S. PPS +11 nodes, +11pp neg recall." />
          <ChangeRow version="v4.0-SiO" desc="Si-O bond-type-aware: allow ring break + single-atom. PDMS +48 nodes, +3pp recall." />
          <ChangeRow version="v4.0-CN" desc="C-N bond-type-aware: allow ring break. PI +127 nodes (imide ring opening)." />
          <ChangeRow version="v4.2" desc="C-O(ester) bond-type-aware: carbonyl-adjacent break. PEI +122 nodes." />
          <ChangeRow version="v4.3" desc="C-F bond-type-aware: single-atom F structural traceability. All fluoropolymers +3 each." />
          <ChangeRow version="v4.2+" desc="New feature detectors: carbonyl, imide, amide, cyclic_aliphatic. Per-rule-pack scoring." />
        </div>
      </div>
    </div>
  )
}

function StepBox({ label, color }: { label: string; color: string }) {
  return (
    <div className={`${color} px-3 py-2 rounded-lg text-center whitespace-pre-line leading-tight`}>
      {label}
    </div>
  )
}

function Arrow() {
  return <span className="text-gray-300 mx-1">→</span>
}

function RuleBadge({ label, desc }: { label: string; desc: string }) {
  return (
    <div className="bg-gray-50 rounded-lg p-2">
      <div className="font-medium text-gray-700">{label}</div>
      <div className="text-gray-400">{desc}</div>
    </div>
  )
}

function FeatureRow({ name, trigger, materials }: { name: string; trigger: string; materials: string }) {
  return (
    <div className="flex items-start gap-3 py-1 border-b border-gray-50">
      <code className="text-xs font-mono text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded shrink-0 w-52">{name}</code>
      <span className="text-xs text-gray-500 w-52 shrink-0">{trigger}</span>
      <span className="text-xs text-gray-400">{materials}</span>
    </div>
  )
}

function BondRow({ type, ring, aromatic, singleAtom, conditions, materials, impact, desc }: {
  type: string; ring: boolean; aromatic: boolean; singleAtom: boolean; conditions: string; materials: string; impact: string; desc: string
}) {
  const bool = (v: boolean) => v
    ? <span className="text-green-600 font-medium">✓</span>
    : <span className="text-gray-300">—</span>
  return (
    <div className="border border-gray-100 rounded-lg p-3">
      <div className="flex items-center gap-3 mb-1">
        <code className="text-sm font-mono font-semibold text-emerald-700 w-24">{type}</code>
        <span className="text-xs text-gray-500">
          Ring:{bool(ring)} Aro:{bool(aromatic)} 1-Atom:{bool(singleAtom)}
          {conditions !== '—' && <span className="ml-2 text-emerald-600">[{conditions}]</span>}
        </span>
        <span className="text-xs text-gray-400 ml-auto font-mono">{materials}</span>
      </div>
      <div className="flex items-center gap-3 text-xs">
        <span className="text-emerald-600 font-medium">{impact}</span>
        <span className="text-gray-400">{desc}</span>
      </div>
    </div>
  )
}

function TagRow({ tag, score, color, desc }: { tag: string; score: string; color: string; desc: string }) {
  return (
    <div className="flex items-start gap-3 py-1.5 border-b border-gray-50">
      <span className={`text-xs px-1.5 py-0.5 rounded font-medium shrink-0 w-60 ${color}`}>{tag.replace(/_/g, ' ')}</span>
      <span className="text-xs font-mono text-gray-500 w-10 shrink-0">{score}</span>
      <span className="text-xs text-gray-600">{desc}</span>
    </div>
  )
}

function StrategyCard({ type, desc, materials }: { type: string; desc: string; materials: string }) {
  return (
    <div className="border rounded-lg p-3">
      <div className="font-medium text-sm capitalize mb-1">{type.replace(/-/g, ' ')}</div>
      <div className="text-xs text-gray-500 mb-1">{desc}</div>
      <div className="text-xs text-gray-400 font-mono">{materials}</div>
    </div>
  )
}

function ChangeRow({ version, desc }: { version: string; desc: string }) {
  return (
    <div className="flex items-start gap-3 py-1">
      <span className="text-xs font-mono font-medium text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded shrink-0 w-24 text-center">{version}</span>
      <span className="text-xs text-gray-600">{desc}</span>
    </div>
  )
}
