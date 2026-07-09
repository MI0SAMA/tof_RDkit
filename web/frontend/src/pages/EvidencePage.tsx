import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import { AlertCircle, CheckCircle, Download, Eye, EyeOff, FileText, Layers, Shield } from 'lucide-react'

const STRATEGY_COLORS: Record<string, string> = {
  'formula-driven': 'bg-green-100 text-green-800 border-green-300',
  'pattern-driven': 'bg-blue-100 text-blue-800 border-blue-300',
  'mixed': 'bg-yellow-100 text-yellow-800 border-yellow-300',
  'validation-limited': 'bg-red-100 text-red-800 border-red-300',
}

export default function EvidencePage() {
  const { id } = useParams<{ id: string }>()
  const { data, isLoading, error } = useQuery({
    queryKey: ['evidence', id],
    queryFn: () => api.getEvidence(id!),
    enabled: !!id,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="flex items-center gap-2 text-red-600 p-4">
        <AlertCircle size={20} />
        <span>Failed to load evidence report.</span>
      </div>
    )
  }

  const { summary } = data
  const hiddenPct = summary.total_formulas > 0
    ? (summary.struct_only / summary.total_formulas * 100).toFixed(1)
    : '0'

  return (
    <div className="space-y-4">
      {/* Evidence Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        <SummaryCard icon={<FileText />} label="Total Formulas" value={summary.total_formulas.toLocaleString()} />
        <SummaryCard icon={<CheckCircle />} label="ValDiag" value={summary.val_diag} color="text-green-600" />
        <SummaryCard icon={<CheckCircle />} label="ValGen" value={summary.val_gen} color="text-blue-600" />
        <SummaryCard icon={<Shield />} label="FeatSupp" value={summary.feat_supp} color="text-amber-600" />
        <SummaryCard icon={<Eye />} label="GenHC" value={summary.gen_hc} color="text-red-500" />
        <SummaryCard icon={<EyeOff />} label="StructOnly" value={`${summary.struct_only} (${hiddenPct}%)`} color="text-gray-400" />
      </div>

      {/* Evidence Level */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Layers size={16} />
            Evidence Levels
          </h3>
          <div className="space-y-3">
            <EvidenceRow label="Formula Evidence" value={summary.formula_evidence}
              map={{ strong: 'text-green-600', moderate: 'text-yellow-600', weak: 'text-orange-500', feature_only: 'text-gray-400', gen_only: 'text-blue-500', validated_generic_only: 'text-blue-500' }} />
            <EvidenceRow label="Pattern Evidence" value={summary.pattern_evidence}
              map={{ strong: 'text-green-600', weak: 'text-orange-500', none: 'text-gray-400' }} />
            <EvidenceRow label="Background Level" value={summary.background_level}
              map={{ low: 'text-green-600', medium: 'text-yellow-600', high: 'text-red-500' }} />
            {summary.pom_pattern_score > 0 && (
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">POM Pattern Score</span>
                <span className="font-mono font-semibold text-blue-600">{summary.pom_pattern_score.toFixed(3)}</span>
              </div>
            )}
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Shield size={16} />
            Final Strategy
          </h3>
          <div className={`inline-block px-4 py-2 rounded-lg border font-semibold text-lg ${STRATEGY_COLORS[summary.final_evidence] || 'bg-gray-100 text-gray-800'}`}>
            {summary.final_evidence.replace(/-/g, ' ')}
          </div>
          <div className="mt-4">
            {/* Composition bar */}
            <div className="text-xs text-gray-500 mb-1">Formula Composition</div>
            <div className="h-4 w-full bg-gray-100 rounded-full overflow-hidden flex">
              {summary.val_diag > 0 && (
                <div className="h-full bg-green-500" style={{ width: `${summary.val_diag / summary.total_formulas * 100}%` }}
                  title={`ValDiag: ${summary.val_diag}`} />
              )}
              {summary.val_gen > 0 && (
                <div className="h-full bg-blue-500" style={{ width: `${summary.val_gen / summary.total_formulas * 100}%` }}
                  title={`ValGen: ${summary.val_gen}`} />
              )}
              {summary.feat_supp > 0 && (
                <div className="h-full bg-amber-400" style={{ width: `${summary.feat_supp / summary.total_formulas * 100}%` }}
                  title={`FeatSupp: ${summary.feat_supp}`} />
              )}
              {summary.gen_hc > 0 && (
                <div className="h-full bg-red-400" style={{ width: `${summary.gen_hc / summary.total_formulas * 100}%` }}
                  title={`GenHC: ${summary.gen_hc}`} />
              )}
              <div className="h-full bg-gray-300 flex-1" title={`StructOnly: ${summary.struct_only}`} />
            </div>
          </div>
        </div>
      </div>

      {/* Formula Lists */}
      {data.validated_diagnostic.length > 0 && (
        <FormulaSection title="Validated Diagnostic Formulas" formulas={data.validated_diagnostic} color="green" />
      )}
      {data.validated_generic.length > 0 && (
        <FormulaSection title="Validated Generic Formulas" formulas={data.validated_generic} color="blue" />
      )}
      {data.feature_supported.length > 0 && (
        <FormulaSection title="Feature Supported Candidates" formulas={data.feature_supported} color="amber" />
      )}
      {data.generic_hydrocarbon.length > 0 && (
        <FormulaSection title="Generic Hydrocarbon Background" formulas={data.generic_hydrocarbon} color="red" />
      )}

      <div className="flex gap-2">
        <button onClick={() => api.exportEvidenceMd()} className="flex items-center gap-1.5 text-sm px-3 py-1.5 bg-white border rounded-lg hover:bg-gray-50">
          <Download size={14} /> Export Markdown
        </button>
        <button onClick={() => api.exportNetworkJson(id!)} className="flex items-center gap-1.5 text-sm px-3 py-1.5 bg-white border rounded-lg hover:bg-gray-50">
          <Download size={14} /> Export Network JSON
        </button>
      </div>
    </div>
  )
}

function SummaryCard({ icon, label, value, color = 'text-gray-700' }: {
  icon: React.ReactNode; label: string; value: string | number; color?: string
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-3 text-center">
      <div className="flex justify-center mb-1 text-gray-400">{icon}</div>
      <div className={`text-lg font-bold ${color}`}>{value}</div>
      <div className="text-xs text-gray-400">{label}</div>
    </div>
  )
}

function EvidenceRow({ label, value, map }: {
  label: string; value: string; map: Record<string, string>
}) {
  return (
    <div className="flex items-center justify-between text-sm">
      <span className="text-gray-500">{label}</span>
      <span className={`font-medium capitalize ${map[value] || 'text-gray-600'}`}>
        {value.replace(/_/g, ' ')}
      </span>
    </div>
  )
}

function FormulaSection({ title, formulas, color }: {
  title: string; formulas: Array<{ formula: string; ion_mode: string; formula_score: number; representative_path: string; generation_types: string }>; color: string
}) {
  const [expanded, setExpanded] = useState(false)
  const display = expanded ? formulas : formulas.slice(0, 10)

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      <h4 className={`font-semibold text-${color}-700 mb-2`}>{title} ({formulas.length})</h4>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-400 border-b">
              <th className="pb-1 font-medium">Formula</th>
              <th className="pb-1 font-medium">Ion</th>
              <th className="pb-1 font-medium">Score</th>
              <th className="pb-1 font-medium">Generation</th>
              <th className="pb-1 font-medium">Path</th>
            </tr>
          </thead>
          <tbody>
            {display.map((f, i) => (
              <tr key={i} className="border-b border-gray-50">
                <td className="py-1 font-mono font-medium">{f.formula}</td>
                <td className="py-1">
                  <span className={`text-xs px-1.5 py-0.5 rounded ${f.ion_mode === 'positive' ? 'bg-blue-50 text-blue-600' : f.ion_mode === 'negative' ? 'bg-red-50 text-red-600' : 'bg-gray-50 text-gray-500'}`}>
                    {f.ion_mode}
                  </span>
                </td>
                <td className="py-1 font-mono text-gray-600">{f.formula_score.toFixed(3)}</td>
                <td className="py-1 text-xs text-gray-500">{f.generation_types}</td>
                <td className="py-1 text-xs text-gray-400 max-w-xs truncate">{f.representative_path}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {formulas.length > 10 && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="mt-2 text-sm text-blue-600 hover:text-blue-800"
        >
          {expanded ? 'Show less' : `Show all ${formulas.length} formulas`}
        </button>
      )}
    </div>
  )
}

import { useState } from 'react'
