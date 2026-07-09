import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { AlertCircle, Upload, FileText, Download, CheckCircle, XCircle, Play } from 'lucide-react'

const API_BASE = '/api'

interface SpectrumInfo {
  filename: string
  path: string
  polarity: string
  size_kb: number
  annotated?: boolean
}

interface MatchResult {
  compound_id: string
  detected_polarity: string
  total_centroid_peaks: number
  included_peaks: number
  matched_peaks: number
  unmatched_peaks: number
  match_rate: number
  tolerance_ppm: number
  tolerance_da: number
  matched: MatchedPeak[]
  unmatched: UnmatchedPeak[]
  preprocess_stats?: Record<string, unknown>
  error?: string
}

interface MatchedPeak {
  mz: number
  intensity: number
  matched_formula: string
  ion_mode: string
  exact_mass: number
  mass_error_da: number
  mass_error_ppm: number
  formula_score: number
  diagnostic_tag: string
  generation_types: string
  representative_path: string
}

interface UnmatchedPeak {
  mz: number
  intensity: number
  reason: string
}

export default function MatchPeaksPage() {
  const { id } = useParams<{ id: string }>()

  // Available spectra
  const { data: spectraData } = useQuery({
    queryKey: ['spectra', id],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/materials/${id}/spectra`)
      return res.json() as Promise<{ material_id: string; spectra: SpectrumInfo[] }>
    },
    enabled: !!id,
  })

  // State
  const [uploading, setUploading] = useState(false)
  const [matchingExisting, setMatchingExisting] = useState(false)
  const [result, setResult] = useState<MatchResult | null>(null)
  const [error, setError] = useState('')
  const [polarityOverride, setPolarityOverride] = useState('auto')
  const [showOnlyMatched, setShowOnlyMatched] = useState(false)

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file || !id) return
    setUploading(true)
    setError('')
    setResult(null)
    try {
      const form = new FormData()
      form.append('file', file)
      const res = await fetch(`${API_BASE}/materials/${id}/match-peaks?polarity=${polarityOverride}`, {
        method: 'POST',
        body: form,
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Match failed')
      setResult(data)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    }
    setUploading(false)
  }

  const handleMatchExisting = async (spectrum: SpectrumInfo) => {
    if (!id) return
    setMatchingExisting(true)
    setError('')
    setResult(null)
    try {
      const params = new URLSearchParams({
        filename: spectrum.filename,
        polarity: polarityOverride,
      })
      if (spectrum.path) params.set('path', spectrum.path)
      const res = await fetch(
        `${API_BASE}/materials/${id}/match-existing?${params}`,
        { method: 'POST' }
      )
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Match failed')
      setResult(data)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    }
    setMatchingExisting(false)
  }

  const exportCSV = () => {
    if (!result) return
    const rows = ['mz,intensity,matched_formula,ion_mode,exact_mass,mass_error_da,mass_error_ppm,formula_score,diagnostic_tag']
    result.matched.forEach(p => {
      rows.push([p.mz, p.intensity, p.matched_formula, p.ion_mode, p.exact_mass,
        p.mass_error_da, p.mass_error_ppm, p.formula_score, p.diagnostic_tag].join(','))
    })
    const blob = new Blob([rows.join('\n')], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = `${id}_matched_peaks.csv`; a.click()
    URL.revokeObjectURL(url)
  }

  const hasSpectra = spectraData?.spectra && spectraData.spectra.length > 0

  return (
    <div className="space-y-4">
      {/* Upload + Existing Spectra */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Upload new file */}
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <h3 className="font-semibold text-gray-700 mb-2 flex items-center gap-2">
            <Upload size={16} />
            Upload Peak List
          </h3>
          <p className="text-xs text-gray-500 mb-3">
            CSV/TSV/TXT with m/z and intensity columns
          </p>
          <div className="flex items-center gap-2 mb-2">
            <select value={polarityOverride} onChange={(e) => setPolarityOverride(e.target.value)}
              className="text-xs border rounded px-2 py-1 bg-white">
              <option value="auto">Auto-detect polarity</option>
              <option value="positive">Positive</option>
              <option value="negative">Negative</option>
            </select>
          </div>
          <label className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer text-sm transition-colors">
            <Upload size={14} />
            {uploading ? 'Matching...' : 'Select File & Match'}
            <input type="file" accept=".csv,.tsv,.txt,.TXT" onChange={handleFileUpload}
              disabled={uploading} className="hidden" />
          </label>
        </div>

        {/* Existing experimental data */}
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <h3 className="font-semibold text-gray-700 mb-2 flex items-center gap-2">
            <FileText size={16} />
            Existing Experimental Data
          </h3>
          {!hasSpectra && (
            <p className="text-xs text-gray-400">No experimental data files found for {id}</p>
          )}
          {hasSpectra && (
            <div className="space-y-1 max-h-40 overflow-y-auto">
              {spectraData!.spectra.map((s) => (
                <button
                  key={s.filename}
                  onClick={() => handleMatchExisting(s)}
                  disabled={matchingExisting}
                  className="w-full flex items-center justify-between px-2 py-1.5 rounded hover:bg-gray-50 text-sm transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <Play size={12} className="text-blue-500" />
                    <span className="font-mono text-xs">{s.filename}</span>
                    <span className={`text-xs px-1 py-0 rounded ${
                      s.polarity === 'positive' ? 'bg-blue-50 text-blue-600' :
                      s.polarity === 'negative' ? 'bg-red-50 text-red-600' :
                      'bg-gray-100 text-gray-500'
                    }`}>{s.polarity}</span>
                    {s.annotated && (
                      <span className="text-xs bg-green-100 text-green-700 px-1 py-0 rounded">labeled</span>
                    )}
                  </div>
                  <span className="text-xs text-gray-400">{s.size_kb} KB</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-center gap-2 text-red-600 p-3 bg-red-50 rounded-lg text-sm">
          <AlertCircle size={16} /> {error}
        </div>
      )}

      {/* Results */}
      {result && !result.error && (
        <div className="space-y-3">
          {/* Summary */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
            <StatCard label="Centroid Peaks" value={result.total_centroid_peaks} />
            <StatCard label="Included" value={result.included_peaks} />
            <StatCard label="Matched" value={result.matched_peaks} color="text-green-600" />
            <StatCard label="Unmatched" value={result.unmatched_peaks} color="text-red-500" />
            <StatCard label="Match Rate" value={`${result.match_rate}%`} color={result.match_rate > 50 ? 'text-green-600' : 'text-amber-600'} />
            <StatCard label="Polarity" value={result.detected_polarity} />
          </div>

          {/* Export */}
          <div className="flex items-center gap-2">
            <label className="flex items-center gap-1.5 text-sm text-gray-600">
              <input type="checkbox" checked={showOnlyMatched}
                onChange={(e) => setShowOnlyMatched(e.target.checked)} className="rounded" />
              Show only matched
            </label>
            <button onClick={exportCSV} className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800">
              <Download size={14} /> Export CSV
            </button>
          </div>

          {/* Matched peaks table */}
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 sticky top-0">
                  <tr className="text-left text-gray-500 text-xs">
                    <th className="px-3 py-2 font-medium">m/z</th>
                    <th className="px-3 py-2 font-medium">Intensity</th>
                    <th className="px-3 py-2 font-medium">Matched Formula</th>
                    <th className="px-3 py-2 font-medium">Ion</th>
                    <th className="px-3 py-2 font-medium">Δ Da</th>
                    <th className="px-3 py-2 font-medium">Δ ppm</th>
                    <th className="px-3 py-2 font-medium">Score</th>
                    <th className="px-3 py-2 font-medium">Evidence</th>
                    <th className="px-3 py-2 font-medium">Generation</th>
                  </tr>
                </thead>
                <tbody>
                  {(showOnlyMatched ? result.matched : [...result.matched])?.map((p, i) => (
                    <tr key={i} className="border-b border-gray-50 hover:bg-gray-50">
                      <td className="px-3 py-1.5 font-mono text-xs">{p.mz.toFixed(4)}</td>
                      <td className="px-3 py-1.5 text-xs text-gray-500">{p.intensity.toExponential(1)}</td>
                      <td className="px-3 py-1.5 font-mono font-medium">{p.matched_formula}</td>
                      <td className="px-3 py-1.5">
                        <span className={`text-xs px-1 py-0.5 rounded ${
                          p.ion_mode === 'positive' ? 'bg-blue-50 text-blue-600' :
                          p.ion_mode === 'negative' ? 'bg-red-50 text-red-600' : 'bg-gray-50 text-gray-500'
                        }`}>{p.ion_mode}</span>
                      </td>
                      <td className="px-3 py-1.5 font-mono text-xs text-gray-500">{p.mass_error_da.toFixed(4)}</td>
                      <td className="px-3 py-1.5 font-mono text-xs text-gray-500">{p.mass_error_ppm.toFixed(1)}</td>
                      <td className="px-3 py-1.5 font-mono text-xs" style={{
                        color: p.formula_score >= 0.8 ? '#16a34a' : p.formula_score >= 0.5 ? '#ca8a04' : '#9ca3af'
                      }}>{p.formula_score.toFixed(3)}</td>
                      <td className="px-3 py-1.5">
                        <TagBadge tag={p.diagnostic_tag} />
                      </td>
                      <td className="px-3 py-1.5 text-xs text-gray-400 max-w-[150px] truncate">{p.generation_types}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Unmatched peaks */}
          {result.unmatched.length > 0 && !showOnlyMatched && (
            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <h4 className="font-semibold text-red-600 text-sm mb-2">
                Unmatched Peaks ({result.unmatched.length})
              </h4>
              <div className="flex flex-wrap gap-1">
                {result.unmatched.slice(0, 50).map((p, i) => (
                  <span key={i} className="font-mono text-xs bg-red-50 text-red-600 px-1.5 py-0.5 rounded"
                    title={`m/z: ${p.mz.toFixed(4)}, intensity: ${p.intensity}`}>
                    {p.mz.toFixed(2)}
                  </span>
                ))}
                {result.unmatched.length > 50 && (
                  <span className="text-xs text-gray-400">+ {result.unmatched.length - 50} more</span>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function StatCard({ label, value, color = 'text-gray-700' }: {
  label: string; value: string | number; color?: string
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-3 text-center">
      <div className={`text-lg font-bold ${color}`}>{value}</div>
      <div className="text-xs text-gray-400">{label}</div>
    </div>
  )
}

function TagBadge({ tag }: { tag: string }) {
  const colors: Record<string, string> = {
    validated_diagnostic: 'bg-green-100 text-green-700',
    validated_generic: 'bg-blue-100 text-blue-700',
    feature_supported_candidate: 'bg-amber-100 text-amber-700',
    generic_hydrocarbon_background: 'bg-red-100 text-red-700',
    structural_candidate_only: 'bg-gray-100 text-gray-500',
  }
  return (
    <span className={`text-xs px-1.5 py-0.5 rounded ${colors[tag] || 'bg-gray-100 text-gray-500'}`}>
      {(tag || 'unlabeled').replace(/_/g, ' ').substring(0, 20)}
    </span>
  )
}
