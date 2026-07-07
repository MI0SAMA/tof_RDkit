import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { Beaker, ChevronRight, Plus, FlaskConical, Loader2, CheckCircle, XCircle } from 'lucide-react'

export default function Materials() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { data: materials, isLoading } = useQuery({
    queryKey: ['materials'],
    queryFn: api.getMaterials,
  })

  // SMILES input form
  const [showForm, setShowForm] = useState(false)
  const [smilesInput, setSmilesInput] = useState('')
  const [compoundId, setCompoundId] = useState('')
  const [formula, setFormula] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [taskResult, setTaskResult] = useState<{ task_id: string; status: string } | null>(null)
  const [error, setError] = useState('')

  const handleGenerate = async () => {
    if (!smilesInput.trim()) return
    if (!compoundId.trim()) {
      // Auto-generate ID from SMILES
      setCompoundId('custom_' + Date.now().toString(36))
    }
    setSubmitting(true)
    setError('')
    setTaskResult(null)
    try {
      const result = await api.generateNetwork({
        compound_id: compoundId || 'custom_' + Date.now().toString(36),
        smiles: smilesInput.trim(),
        formula: formula.trim(),
      })
      setTaskResult(result)
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to submit')
    }
    setSubmitting(false)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    )
  }

  const groups = new Map<string, typeof materials>()
  materials?.forEach((m) => {
    const g = m.group || 'other'
    if (!groups.has(g)) groups.set(g, [])
    groups.get(g)!.push(m)
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Materials</h2>
          <p className="text-sm text-gray-500 mt-1">{materials?.length || 0} materials in database</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
        >
          <Plus size={16} />
          New SMILES
        </button>
      </div>

      {/* SMILES Input Form */}
      {showForm && (
        <div className="bg-white rounded-xl border border-blue-200 p-5 shadow-sm">
          <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
            <FlaskConical size={18} className="text-blue-600" />
            Generate Network from SMILES
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-3">
            <div>
              <label className="text-xs text-gray-500 mb-1 block">SMILES *</label>
              <input
                type="text"
                value={smilesInput}
                onChange={(e) => setSmilesInput(e.target.value)}
                placeholder="e.g. O=C(OCCO)c1ccc(C(=O)OCCO)cc1"
                className="w-full border rounded-lg px-3 py-2 text-sm font-mono focus:ring-2 focus:ring-blue-300 focus:border-blue-400 outline-none"
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 mb-1 block">Compound ID</label>
              <input
                type="text"
                value={compoundId}
                onChange={(e) => setCompoundId(e.target.value)}
                placeholder="my_polymer"
                className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-300 outline-none"
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 mb-1 block">Formula (optional)</label>
              <input
                type="text"
                value={formula}
                onChange={(e) => setFormula(e.target.value)}
                placeholder="C10H8O4"
                className="w-full border rounded-lg px-3 py-2 text-sm font-mono focus:ring-2 focus:ring-blue-300 outline-none"
              />
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleGenerate}
              disabled={!smilesInput.trim() || submitting}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium"
            >
              {submitting ? <Loader2 size={16} className="animate-spin" /> : <FlaskConical size={16} />}
              Generate Network
            </button>
            <button
              onClick={() => { setShowForm(false); setTaskResult(null); setError('') }}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              Cancel
            </button>
            {taskResult && (
              <div className="flex items-center gap-2 text-sm">
                <CheckCircle size={16} className="text-green-500" />
                <span>Task <code className="bg-gray-100 px-1 rounded text-xs">{taskResult.task_id}</code> queued</span>
                <button onClick={() => navigate('/tasks')} className="text-blue-600 hover:underline text-xs">
                  View Tasks →
                </button>
              </div>
            )}
            {error && (
              <div className="flex items-center gap-2 text-sm text-red-600">
                <XCircle size={16} />
                {error}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Material Groups */}
      {Array.from(groups.entries()).map(([group, items]) => (
        <div key={group}>
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">
            {group.replace(/_/g, ' ')}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {items?.map((m) => (
              <div
                key={m.compound_id}
                onClick={() => navigate(`/materials/${m.compound_id}`)}
                className="bg-white rounded-xl border border-gray-200 p-4 hover:shadow-md hover:border-blue-300 cursor-pointer transition-all flex items-center justify-between"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-gray-800">{m.compound_id}</span>
                    {m.has_manual_labels && (
                      <span className="text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded">
                        labeled
                      </span>
                    )}
                    {m.group === 'custom' && (
                      <span className="text-xs bg-purple-100 text-purple-700 px-1.5 py-0.5 rounded">
                        custom
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-gray-500 mt-0.5">{m.name}</p>
                  {m.formula && (
                    <code className="text-xs text-gray-400 mt-1 block">{m.formula}</code>
                  )}
                </div>
                <ChevronRight size={18} className="text-gray-300" />
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
