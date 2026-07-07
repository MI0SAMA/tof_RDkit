import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import { useMemo, useState } from 'react'
import CytoscapeComponent from 'react-cytoscapejs'
import SankeyChart from '../components/SankeyChart'
import { AlertCircle, Filter, Share2, GitBranch } from 'lucide-react'

type ViewMode = 'sankey' | 'graph'

const TAG_OPTIONS = [
  { value: '', label: 'All' },
  { value: 'validated_diagnostic', label: 'ValDiag' },
  { value: 'validated_generic', label: 'ValGen' },
  { value: 'feature_supported_candidate', label: 'FeatSupp' },
  { value: 'generic_hydrocarbon_background', label: 'GenHC' },
]

export default function NetworkPage() {
  const { id } = useParams<{ id: string }>()
  const [viewMode, setViewMode] = useState<ViewMode>('sankey')

  // Sankey data
  const { data: sankeyData, isLoading: sankeyLoading } = useQuery({
    queryKey: ['network-sankey', id],
    queryFn: async () => {
      const res = await fetch(`/api/materials/${id}/network-sankey`)
      if (!res.ok) throw new Error('Failed')
      return res.json()
    },
    enabled: !!id,
  })

  // Graph data (for Cytoscape)
  const [hideStructOnly, setHideStructOnly] = useState(true)
  const [hideNeutral, setHideNeutral] = useState(true)
  const [layout, setLayout] = useState('cose')
  const [tagFilter, setTagFilter] = useState('')

  const { data: graphData, isLoading: graphLoading } = useQuery({
    queryKey: ['network', id, hideStructOnly],
    queryFn: () => api.getNetwork(id!, hideStructOnly),
    enabled: !!id && viewMode === 'graph',
  })

  const elements = useMemo(() => {
    if (!graphData) return []
    let nodes = graphData.nodes
    if (tagFilter) nodes = nodes.filter(n => n.diagnostic_tag === tagFilter)
    if (hideNeutral) nodes = nodes.filter(n => n.ion_mode !== 'neutral' || n.generation_type === 'parent')
    const nodeIds = new Set(nodes.map(n => n.node_id))
    const edges = graphData.edges.filter(e => nodeIds.has(e.source_node) && nodeIds.has(e.target_node))
    return [
      ...nodes.map(n => ({ data: { id: n.node_id, label: n.formula, ...n }, classes: `type-${n.generation_type} tag-${n.diagnostic_tag || 'unknown'}` })),
      ...edges.map(e => ({ data: { id: e.edge_id, source: e.source_node, target: e.target_node, ...e } })),
    ]
  }, [graphData, tagFilter, hideNeutral])

  const stylesheet = useMemo(() => [
    { selector: 'node', style: { 'background-color': '#93c5fd', 'label': 'data(label)', 'font-size': '8px', 'width': 12, 'height': 12, 'border-width': 1, 'border-color': '#d1d5db' } },
    { selector: 'node.tag-validated_diagnostic', style: { 'background-color': '#22c55e', 'border-color': '#16a34a', 'border-width': 2, 'width': 16, 'height': 16 } },
    { selector: 'node.tag-validated_generic', style: { 'background-color': '#3b82f6', 'width': 14, 'height': 14 } },
    { selector: 'node.tag-feature_supported_candidate', style: { 'background-color': '#f59e0b' } },
    { selector: 'node.tag-generic_hydrocarbon_background', style: { 'background-color': '#ef4444', 'width': 10, 'height': 10 } },
    { selector: 'node.type-parent', style: { 'width': 24, 'height': 24, 'border-width': 3, 'border-color': '#1e40af', 'background-color': '#60a5fa' } },
    { selector: 'node.type-feature_rule', style: { 'shape': 'diamond' } },
    { selector: 'node.type-recombination', style: { 'shape': 'triangle' } },
    { selector: 'edge', style: { 'width': 0.3, 'line-color': '#e5e7eb', 'target-arrow-color': '#d1d5db', 'target-arrow-shape': 'triangle', 'arrow-scale': 0.4, 'curve-style': 'bezier' } },
  ], [])

  const layoutOptions = useMemo(() => {
    if (layout === 'cose') return { name: 'cose', idealEdgeLength: 80, nodeOverlap: 20, fit: true, padding: 30, nodeRepulsion: 200000, numIter: 2000 }
    if (layout === 'breadthfirst') return { name: 'breadthfirst', directed: true, spacingFactor: 1.1 }
    return { name: layout, fit: true, padding: 30 }
  }, [layout])

  if (sankeyLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {/* View mode toggle */}
      <div className="flex items-center gap-2">
        <div className="flex bg-gray-100 rounded-lg p-0.5">
          <button
            onClick={() => setViewMode('sankey')}
            className={`flex items-center gap-1 px-3 py-1.5 rounded-md text-sm transition-colors ${
              viewMode === 'sankey' ? 'bg-white text-blue-700 shadow-sm font-medium' : 'text-gray-500'
            }`}
          >
            <GitBranch size={14} /> Sankey Flow
          </button>
          <button
            onClick={() => setViewMode('graph')}
            className={`flex items-center gap-1 px-3 py-1.5 rounded-md text-sm transition-colors ${
              viewMode === 'graph' ? 'bg-white text-blue-700 shadow-sm font-medium' : 'text-gray-500'
            }`}
          >
            <Share2 size={14} /> Node Graph
          </button>
        </div>
        {sankeyData && (
          <span className="text-xs text-gray-400">
            {sankeyData.total_formulas} ionized formulas
          </span>
        )}
      </div>

      {/* Sankey View */}
      {viewMode === 'sankey' && sankeyData && (
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <SankeyChart
            nodes={sankeyData.nodes}
            links={sankeyData.links}
            totalFormulas={sankeyData.total_formulas}
          />
        </div>
      )}
      {viewMode === 'sankey' && !sankeyData?.nodes?.length && (
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400">
          No formula data available for this material
        </div>
      )}

      {/* Graph View */}
      {viewMode === 'graph' && (
        <>
          <div className="flex items-center gap-3 flex-wrap text-sm">
            <label className="flex items-center gap-1.5 text-gray-600">
              <input type="checkbox" checked={hideStructOnly} onChange={(e) => setHideStructOnly(e.target.checked)} className="rounded" />
              Hide StructOnly
            </label>
            <label className="flex items-center gap-1.5 text-gray-600">
              <input type="checkbox" checked={hideNeutral} onChange={(e) => setHideNeutral(e.target.checked)} className="rounded" />
              Hide neutral
            </label>
            <div className="flex items-center gap-1">
              <Filter size={14} className="text-gray-400" />
              <select value={tagFilter} onChange={(e) => setTagFilter(e.target.value)} className="border rounded px-2 py-1 bg-white text-sm">
                {TAG_OPTIONS.map(o => (<option key={o.value} value={o.value}>{o.label}</option>))}
              </select>
            </div>
            <select value={layout} onChange={(e) => setLayout(e.target.value)} className="border rounded px-2 py-1 bg-white text-sm">
              <option value="cose">Force</option>
              <option value="breadthfirst">Breadth</option>
              <option value="concentric">Concentric</option>
            </select>
            <span className="text-gray-400 text-xs">{elements.filter(e => 'label' in (e.data || {})).length} nodes</span>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden" style={{ height: 600 }}>
            {graphLoading ? (
              <div className="flex items-center justify-center h-full"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" /></div>
            ) : (
              <CytoscapeComponent key={`${id}-${tagFilter}-${hideNeutral}-${layout}`}
                elements={elements} stylesheet={stylesheet} layout={layoutOptions}
                style={{ width: '100%', height: '100%' }} wheelSensitivity={0.3} minZoom={0.1} maxZoom={5} />
            )}
          </div>
        </>
      )}
    </div>
  )
}
