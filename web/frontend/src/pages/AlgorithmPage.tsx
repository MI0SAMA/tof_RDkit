import { Layers, GitBranch, Zap, Target, Shield, Atom } from 'lucide-react'

export default function AlgorithmPage() {
  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Algorithm Architecture</h2>
        <p className="text-sm text-gray-500 mt-1">TOF-SIMS Formula Network v3.0 — four-layer pipeline</p>
      </div>

      {/* Pipeline Overview */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <Layers size={18} className="text-blue-600" /> Pipeline Overview
        </h3>
        <div className="flex items-center gap-0 text-xs font-mono flex-wrap">
          <StepBox label="SMILES" color="bg-gray-100" />
          <Arrow />
          <StepBox label="Layer 1\nRDKit Frag" color="bg-blue-50" />
          <Arrow />
          <StepBox label="Layer 2\nFeature Rules" color="bg-amber-50" />
          <Arrow />
          <StepBox label="Layer 3\nSmall Fragments" color="bg-green-50" />
          <Arrow />
          <StepBox label="Layer 4\nDiagnostics" color="bg-purple-50" />
          <Arrow />
          <StepBox label="Evidence\nReport" color="bg-gray-100" />
        </div>
      </div>

      {/* Layer 1 */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
          <Atom size={18} className="text-blue-600" /> Layer 1 — RDKit Fragmentation
        </h3>
        <p className="text-sm text-gray-600 mb-3">
          Bond-breaking enumeration on the parent SMILES structure, followed by H-shift, recombination, and ionization.
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
          <RuleBadge label="Parent" desc="Root molecule" />
          <RuleBadge label="Fragment" desc="Bond breaks (≤2)" />
          <RuleBadge label="H-Shift" desc="±1 H transfer" />
          <RuleBadge label="Recombination" desc="Site-constrained fragment pairs" />
        </div>
        <div className="mt-2 text-xs text-gray-400">
          Ionization: e⁻ loss/gain · H⁺ addition/removal · max 300 fragment nodes
        </div>
      </div>

      {/* Layer 2 */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
          <GitBranch size={18} className="text-amber-600" /> Layer 2 — Structure Feature Rules
        </h3>
        <p className="text-sm text-gray-600 mb-3">
          RDKit substructure-triggered rule packs. Each rule fires only when specific functional groups or structural motifs are detected in the parent molecule.
        </p>
        <div className="space-y-2 text-sm">
          <FeatureRow name="fluorocarbon_fragmentation" trigger="C-F bonds" materials="PTFE, PVDF, ETFE, FEP, PFA" />
          <FeatureRow name="acetal_oxonium_series" trigger="O-C-O acetal motif" materials="POMC, POMH" />
          <FeatureRow name="aromatic_stable_fragments" trigger="Aromatic rings" materials="PET, PEEK, PEI, PEN, PI, Nomex, PPS" />
          <FeatureRow name="sulfur_aromatic_fragments" trigger="Aromatic S" materials="PPS" />
          <FeatureRow name="carbonyl_fragmentation" trigger="C=O carbonyl" materials="PET, PEEK, PEI, PI, Nomex, EVA" />
          <FeatureRow name="imide_fragments" trigger="Imide group" materials="PI, PEI" />
          <FeatureRow name="amide_fragments" trigger="Amide group" materials="Nomex" />
          <FeatureRow name="cyclic_aliphatic_fragments" trigger="Non-aromatic rings" materials="COC" />
          <FeatureRow name="acetate_ethylene_fragments" trigger="Carbonyl + NOT aromatic" materials="EVA" />
        </div>
      </div>

      {/* Layer 3 */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
          <Zap size={18} className="text-green-600" /> Layer 3 — Small Fragment Experience Rules
        </h3>
        <p className="text-sm text-gray-600 mb-3">
          Empirical fragment libraries generated from domain knowledge. Element-gated: each rule only activates when the parent contains the relevant element.
        </p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-xs">
          <RuleBadge label="hydrocarbon_small" desc="C₂–C₆ (C-gated)" />
          <RuleBadge label="oxygenated_small" desc="C₁–C₃ (O-gated)" />
          <RuleBadge label="nitrogenated_small" desc="C₁–C₃ (N-gated)" />
          <RuleBadge label="sulfurated_small" desc="Thio fragments (S-gated)" />
          <RuleBadge label="siloxane_small" desc="Si₁–₂ (Si-gated, PDMS)" />
        </div>
      </div>

      {/* Layer 4 */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
          <Target size={18} className="text-purple-600" /> Layer 4 — Diagnostic Scoring (v2.9→v3.0)
        </h3>
        <p className="text-sm text-gray-600 mb-3">
          Five-tier evidence tagging system that classifies every formula by its diagnostic value for material identification.
        </p>
        <div className="space-y-2 text-sm">
          <TagRow tag="validated_diagnostic" score="0.80" color="bg-green-100 text-green-800"
            desc="≤3 materials + confirmed by manual annotation. Formula-driven identification." />
          <TagRow tag="validated_generic" score="0.50" color="bg-blue-100 text-blue-800"
            desc="4+ materials + annotation confirmed. Shared but validated." />
          <TagRow tag="feature_supported_candidate" score="0.30" color="bg-amber-100 text-amber-800"
            desc="Rule-supported but unvalidated against manual labels." />
          <TagRow tag="generic_hydrocarbon_background" score="0.00" color="bg-red-100 text-red-800"
            desc="13+ materials, pure HC. Cross-material background noise." />
          <TagRow tag="structural_candidate_only" score="0.10" color="bg-gray-100 text-gray-600"
            desc="RDKit-only theoretical candidate. Hidden by default (86.8% of all formulas)." />
        </div>
      </div>

      {/* Scoring */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
          <Shield size={18} className="text-gray-600" /> Scoring Model
        </h3>
        <p className="text-sm text-gray-600 mb-3">
          Composite heuristic score (0–1) combining structure plausibility, ionization likelihood, mass prior, and diversity bonuses.
        </p>
        <div className="text-sm text-gray-600 space-y-1">
          <div><code className="bg-gray-100 px-1 rounded text-xs">formula_score = path_score + path_bonus + mechanism_bonus + source_fragment_bonus</code></div>
          <div className="ml-4 text-xs text-gray-400">path_score = 0.60 × structure_score + 0.40 × ionization_score − h_shift_penalty − recombination_penalty + mass_prior</div>
          <div className="ml-4 text-xs text-gray-400">structure_score = base − penalty_per_bond × n_broken_bonds</div>
        </div>
      </div>

      {/* Evidence Strategy */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-3">Material Identification Strategy</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
          <StrategyCard type="formula-driven" desc="Strong validated_diagnostic formulas exist. Material can be identified by individual diagnostic peaks." materials="PDMS" />
          <StrategyCard type="pattern-driven" desc="No diagnostic single formulas, but fragment pattern combination is unique. POM backbone density + element consistency." materials="POMC, POMH" />
          <StrategyCard type="mixed" desc="Some validated formulas + pattern evidence. Combined approach recommended." materials="COC, EVA, PET, PEEK, PEI, PEN, PI, Nomex" />
          <StrategyCard type="validation-limited" desc="Only feature_supported candidates available. Insufficient for standalone identification." materials="PTFE, PVDF, ETFE, FEP, PFA, PPS" />
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
    <div className="flex items-start gap-3 py-1.5 border-b border-gray-50">
      <code className="text-xs font-mono text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded shrink-0 w-44">{name}</code>
      <span className="text-xs text-gray-500 w-48 shrink-0">{trigger}</span>
      <span className="text-xs text-gray-400">{materials}</span>
    </div>
  )
}

function TagRow({ tag, score, color, desc }: { tag: string; score: string; color: string; desc: string }) {
  return (
    <div className="flex items-start gap-3 py-1.5 border-b border-gray-50">
      <span className={`text-xs px-1.5 py-0.5 rounded font-medium shrink-0 w-56 ${color}`}>{tag.replace(/_/g, ' ')}</span>
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
