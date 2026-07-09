import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api, FormulaItem } from '../api/client'
import { useMemo, useState } from 'react'
import { AgGridReact } from 'ag-grid-react'
import { ColDef } from 'ag-grid-community'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-alpine.css'
import { AlertCircle, Download, Filter, Search } from 'lucide-react'

const TAG_OPTIONS = [
  { value: '', label: 'All Tags' },
  { value: 'validated_diagnostic', label: 'Validated Diagnostic' },
  { value: 'validated_generic', label: 'Validated Generic' },
  { value: 'feature_supported_candidate', label: 'Feature Supported' },
  { value: 'generic_hydrocarbon_background', label: 'Generic HC Background' },
  { value: 'structural_candidate_only', label: 'Structural Only' },
]

const ION_OPTIONS = [
  { value: '', label: 'All Ions' },
  { value: 'positive', label: 'Positive' },
  { value: 'negative', label: 'Negative' },
]

export default function FormulasPage() {
  const { id } = useParams<{ id: string }>()
  const [evidenceTag, setEvidenceTag] = useState('')
  const [ionMode, setIonMode] = useState('')
  const [minScore, setMinScore] = useState('')
  const [hideSO, setHideSO] = useState(true)
  const [hideHC, setHideHC] = useState(false)
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(50)

  const params = useMemo(() => {
    const p: Record<string, string | number | boolean> = {
      page,
      page_size: pageSize,
      hide_struct_only: hideSO,
      hide_generic_hc: hideHC,
      sort_by: 'formula_score',
      sort_dir: 'desc',
    }
    if (evidenceTag) p.evidence_tag = evidenceTag
    if (ionMode) p.ion_mode = ionMode
    if (minScore) p.min_score = parseFloat(minScore)
    if (search) p.search = search
    return p
  }, [evidenceTag, ionMode, minScore, hideSO, hideHC, search, page, pageSize])

  const { data, isLoading, error } = useQuery({
    queryKey: ['formulas', id, params],
    queryFn: () => api.getFormulas(id!, params),
    enabled: !!id,
  })

  const columns: ColDef<FormulaItem>[] = [
    { field: 'formula', headerName: 'Formula', flex: 1, sortable: true, filter: true,
      cellStyle: { fontFamily: 'monospace', fontWeight: 500 } },
    { field: 'ion_mode', headerName: 'Ion', width: 80, sortable: true,
      cellStyle: (p) => p.value === 'positive' ? { color: '#2563eb' } : p.value === 'negative' ? { color: '#dc2626' } : null },
    { field: 'charge', headerName: 'Chg', width: 60 },
    { field: 'exact_mass', headerName: 'Exact Mass', width: 110, sortable: true,
      valueFormatter: (p) => p.value?.toFixed(4) },
    { field: 'formula_score', headerName: 'Score', width: 80, sortable: true,
      cellStyle: (p) => ({
        color: p.value >= 0.8 ? '#16a34a' : p.value >= 0.5 ? '#ca8a04' : '#9ca3af',
        fontWeight: p.value >= 0.8 ? 600 : 400,
      }),
      valueFormatter: (p) => p.value?.toFixed(3) },
    { field: 'diagnostic_tag', headerName: 'Evidence Tag', width: 180, sortable: true,
      cellStyle: (p) => {
        const colors: Record<string, string> = {
          validated_diagnostic: '#16a34a',
          validated_generic: '#2563eb',
          feature_supported_candidate: '#ca8a04',
          generic_hydrocarbon_background: '#dc2626',
          structural_candidate_only: '#9ca3af',
        }
        return { color: colors[p.value] || '#6b7280', fontWeight: p.value === 'validated_diagnostic' ? 600 : 400 }
      } },
    { field: 'generation_types', headerName: 'Generation', width: 150,
      cellStyle: { fontSize: '11px' } },
    { field: 'path_count', headerName: 'Paths', width: 70 },
    { field: 'mechanism_count', headerName: 'Mechs', width: 70 },
    { field: 'representative_path', headerName: 'Representative Path', flex: 2,
      cellStyle: { fontSize: '10px', color: '#6b7280' } },
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center gap-2 text-red-600 p-4">
        <AlertCircle size={20} />
        <span>Failed to load formulas.</span>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-1.5 bg-white border rounded-lg px-2 py-1">
          <Filter size={14} className="text-gray-400" />
          <select value={evidenceTag} onChange={(e) => setEvidenceTag(e.target.value)}
            className="text-sm bg-transparent outline-none">
            {TAG_OPTIONS.map(o => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </div>

        <select value={ionMode} onChange={(e) => setIonMode(e.target.value)}
          className="text-sm border rounded-lg px-2 py-1 bg-white">
          {ION_OPTIONS.map(o => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>

        <input type="number" placeholder="Min score" value={minScore} onChange={(e) => setMinScore(e.target.value)}
          className="text-sm border rounded-lg px-2 py-1 w-24" step="0.1" min="0" max="1" />

        <div className="flex items-center gap-1.5 bg-white border rounded-lg px-2 py-1">
          <Search size={14} className="text-gray-400" />
          <input type="text" placeholder="Search formula..." value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1) }}
            className="text-sm bg-transparent outline-none w-40" />
        </div>

        <label className="flex items-center gap-1.5 text-sm text-gray-600">
          <input type="checkbox" checked={hideSO} onChange={(e) => { setHideSO(e.target.checked); setPage(1) }} className="rounded" />
          Hide StructOnly
        </label>

        <label className="flex items-center gap-1.5 text-sm text-gray-600">
          <input type="checkbox" checked={hideHC} onChange={(e) => { setHideHC(e.target.checked); setPage(1) }} className="rounded" />
          Hide GenHC
        </label>

        <button onClick={() => api.exportFormulasCsv(id)} className="ml-auto flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800">
          <Download size={14} /> CSV
        </button>
      </div>

      {/* Tag counts */}
      {data?.tag_counts && (
        <div className="flex gap-3 text-xs">
          {Object.entries(data.tag_counts).map(([tag, count]) => (
            <button
              key={tag}
              onClick={() => setEvidenceTag(evidenceTag === tag ? '' : tag)}
              className={`px-2 py-0.5 rounded-full transition-colors ${
                evidenceTag === tag
                  ? 'bg-blue-100 text-blue-700 font-medium'
                  : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
              }`}
            >
              {tag.replace(/_/g, ' ')}: {count}
            </button>
          ))}
        </div>
      )}

      {/* Table */}
      <div className="ag-theme-alpine bg-white rounded-xl border border-gray-200 overflow-hidden" style={{ height: 600 }}>
        <AgGridReact
          rowData={data?.items || []}
          columnDefs={columns}
          pagination={true}
          paginationPageSize={pageSize}
          suppressPaginationPanel={true}
          domLayout="normal"
          defaultColDef={{
            resizable: true,
            sortable: true,
          }}
        />
      </div>

      {/* Pagination */}
      {data && (
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>Page {data.page} of {data.total_pages} ({data.total} total)</span>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page <= 1}
              className="px-3 py-1 border rounded-lg disabled:opacity-30 hover:bg-gray-50"
            >
              Prev
            </button>
            <select value={pageSize} onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1) }}
              className="border rounded-lg px-2 py-1">
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
              <option value={200}>200</option>
            </select>
            <button
              onClick={() => setPage(Math.min(data.total_pages, page + 1))}
              disabled={page >= data.total_pages}
              className="px-3 py-1 border rounded-lg disabled:opacity-30 hover:bg-gray-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
