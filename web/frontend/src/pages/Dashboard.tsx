import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { AlertCircle } from 'lucide-react'

export default function Dashboard() {
  const navigate = useNavigate()
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: api.getDashboard,
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
        <span>Failed to load dashboard. Make sure data has been imported.</span>
      </div>
    )
  }

  const { materials, evaluation_metrics: metrics } = data

  const getEvidenceColor = (strategy: string) => {
    if (strategy === 'formula-driven') return 'bg-green-100 text-green-800'
    if (strategy === 'pattern-driven') return 'bg-blue-100 text-blue-800'
    if (strategy === 'mixed') return 'bg-yellow-100 text-yellow-800'
    return 'bg-gray-100 text-gray-800'
  }

  const barColor = (v: number | null) => {
    if (v === null) return '#d1d5db'
    if (v >= 80) return '#22c55e'
    if (v >= 50) return '#f59e0b'
    return '#ef4444'
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
        <p className="text-sm text-gray-500 mt-1">
          {materials.length} materials · v5.1 · pos / neg recall
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
        {materials.map((m) => (
          <div
            key={m.compound_id}
            onClick={() => navigate(`/materials/${m.compound_id}`)}
            className="bg-white rounded-xl border border-gray-200 p-4 hover:shadow-md hover:border-blue-300 cursor-pointer transition-all"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold text-gray-800">{m.compound_id}</span>
              <span className={`text-xs px-2 py-0.5 rounded-full ${getEvidenceColor(m.final_evidence)}`}>
                {m.final_evidence}
              </span>
            </div>
            <p className="text-xs text-gray-500 truncate">{m.name}</p>

            {/* Positive bar */}
            <div className="mt-3 flex items-center gap-1">
              <span className="text-xs text-blue-600 w-5 font-medium">+</span>
              <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div className="h-full rounded-full" style={{
                  width: `${Math.min(m.match_rate_pos || 0, 100)}%`,
                  backgroundColor: barColor(m.match_rate_pos),
                }} />
              </div>
              <span className="text-xs text-gray-500 w-10 text-right font-medium">
                {m.match_rate_pos !== null ? `${m.match_rate_pos}%` : '—'}
              </span>
            </div>

            {/* Negative bar */}
            <div className="mt-1 flex items-center gap-1">
              <span className="text-xs text-red-500 w-5 font-medium">−</span>
              <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div className="h-full rounded-full" style={{
                  width: `${Math.min(m.match_rate_neg || 0, 100)}%`,
                  backgroundColor: barColor(m.match_rate_neg),
                }} />
              </div>
              <span className="text-xs text-gray-500 w-10 text-right font-medium">
                {m.match_rate_neg !== null ? `${m.match_rate_neg}%` : '—'}
              </span>
            </div>

            {/* Evidence tags */}
            <div className="flex gap-1.5 mt-2 text-xs">
              <span className="px-1.5 py-0.5 bg-green-100 text-green-700 rounded">VD:{m.val_diag}</span>
              <span className="px-1.5 py-0.5 bg-blue-100 text-blue-700 rounded">VG:{m.val_gen}</span>
              <span className="px-1.5 py-0.5 bg-amber-100 text-amber-700 rounded">FS:{m.feat_supp}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Evaluation Metrics Table */}
      {metrics && metrics.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-100">
            <h3 className="font-semibold text-gray-800 text-sm">Evaluation Metrics by Material</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-left text-gray-400 bg-gray-50">
                  <th className="px-3 py-2 font-medium">Material</th>
                  <th className="px-3 py-2 font-medium text-center" colSpan={2}>Recall</th>
                  <th className="px-3 py-2 font-medium text-center" colSpan={2}>Recall@50</th>
                  <th className="px-3 py-2 font-medium text-center" colSpan={2}>Precision@50</th>
                  <th className="px-3 py-2 font-medium text-center" colSpan={2}>Peaks</th>
                </tr>
                <tr className="text-left text-gray-400 bg-gray-50 text-[10px]">
                  <th className="px-3 py-1"></th>
                  <th className="px-2 py-1 text-center text-blue-500">+</th>
                  <th className="px-2 py-1 text-center text-red-500">−</th>
                  <th className="px-2 py-1 text-center text-blue-500">+</th>
                  <th className="px-2 py-1 text-center text-red-500">−</th>
                  <th className="px-2 py-1 text-center text-blue-500">+</th>
                  <th className="px-2 py-1 text-center text-red-500">−</th>
                  <th className="px-2 py-1 text-center text-blue-500">+</th>
                  <th className="px-2 py-1 text-center text-red-500">−</th>
                </tr>
              </thead>
              <tbody>
                {metrics.map((m) => (
                  <tr key={m.material} className="border-b border-gray-50 hover:bg-gray-50">
                    <td className="px-3 py-1.5 font-medium text-gray-700">{m.material}</td>
                    <TdColor v={m.pos_recall} />
                    <TdColor v={m.neg_recall} />
                    <TdColor v={m.pos_recall50} />
                    <TdColor v={m.neg_recall50} />
                    <TdColor v={m.pos_precision50} />
                    <TdColor v={m.neg_precision50} />
                    <td className="px-2 py-1.5 text-center text-gray-400">{m.pos_included ?? '—'}</td>
                    <td className="px-2 py-1.5 text-center text-gray-400">{m.neg_included ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

function TdColor({ v }: { v: number | null }) {
  if (v === null) return <td className="px-2 py-1.5 text-center text-gray-300">—</td>
  const color = v >= 80 ? 'text-green-600' : v >= 50 ? 'text-amber-600' : 'text-red-500'
  return <td className={`px-2 py-1.5 text-center font-mono font-medium ${color}`}>{v}%</td>
}
