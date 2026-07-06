import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import { useMemo, useState } from 'react'
import CytoscapeComponent from 'react-cytoscapejs'
import { AlertCircle, Filter } from 'lucide-react'

const TAG_OPTIONS = [
  { value: '', label: 'All' },
  { value: 'validated_diagnostic', label: 'ValDiag' },
  { value: 'validated_generic', label: 'ValGen' },
  { value: 'feature_supported_candidate', label: 'FeatSupp' },
  { value: 'generic_hydrocarbon_background', label: 'GenHC' },
]

export default function NetworkPage() {
  const { id } = useParams<{ id: string }>()
  const [hideStructOnly, setHideStructOnly] = useState(true)
  const [hideNeutral, setHideNeutral] = useState(true)
  const [layout, setLayout] = useState('cose')
  const [tagFilter, setTagFilter] = useState('')
  const [maxNodes, setMaxNodes] = useState(500)

  const { data, isLoading, error } = useQuery({
    queryKey: ['network', id, hideStructOnly],
    queryFn: () => api.getNetwork(id!, hideStructOnly),
    enabled: !!id,
  })

  const elements = useMemo(() => {
    if (!data) return []

    let nodes = data.nodes

    // Filter by evidence tag
    if (tagFilter) {
      nodes = nodes.filter(n => n.diagnostic_tag === tagFilter)
    }

    // Filter neutral nodes (intermediate, not ionized)
    if (hideNeutral) {
      nodes = nodes.filter(n => n.ion_mode !== 'neutral' || n.generation_type === 'parent')
    }

    // Cap nodes for performance
    const nodeIds = new Set(nodes.map(n => n.node_id))
    const edges = data.edges.filter(e => nodeIds.has(e.source_node) && nodeIds.has(e.target_node))

    const cytoscapeNodes = nodes.map((n) => ({
      data: {
        id: n.node_id,
        label: n.formula,
        formula: n.formula,
        generation_type: n.generation_type,
        ion_mode: n.ion_mode,
        diagnostic_tag: n.diagnostic_tag,
        path_score: n.path_score,
        formula_score: n.formula_score,
        rule_pack: n.rule_pack,
      },
      classes: `type-${n.generation_type} tag-${n.diagnostic_tag || 'unknown'}`,
    }))

    const cytoscapeEdges = edges.map((e) => ({
      data: {
        id: e.edge_id,
        source: e.source_node,
        target: e.target_node,
        operation: e.operation,
        operation_type: e.operation_type,
        weight: e.weight,
      },
    }))

    return [...cytoscapeNodes, ...cytoscapeEdges]
  }, [data, tagFilter, hideNeutral])

  const stylesheet = useMemo(() => [
    {
      selector: 'node',
      style: {
        'background-color': '#93c5fd',
        'label': 'data(label)',
        'font-size': '8px',
        'text-valign': 'center',
        'text-halign': 'center',
        'color': '#374151',
        'width': 12,
        'height': 12,
        'border-width': 1,
        'border-color': '#d1d5db',
      },
    },
    {
      selector: 'node.tag-validated_diagnostic',
      style: { 'background-color': '#22c55e', 'border-color': '#16a34a', 'border-width': 2, 'width': 16, 'height': 16 },
    },
    {
      selector: 'node.tag-validated_generic',
      style: { 'background-color': '#3b82f6', 'border-color': '#2563eb', 'border-width': 2, 'width': 14, 'height': 14 },
    },
    {
      selector: 'node.tag-feature_supported_candidate',
      style: { 'background-color': '#f59e0b', 'width': 12, 'height': 12 },
    },
    {
      selector: 'node.tag-generic_hydrocarbon_background',
      style: { 'background-color': '#ef4444', 'width': 10, 'height': 10 },
    },
    {
      selector: 'node.type-parent',
      style: { 'width': 24, 'height': 24, 'border-width': 3, 'border-color': '#1e40af', 'background-color': '#60a5fa' },
    },
    {
      selector: 'node.type-feature_rule',
      style: { 'shape': 'diamond' },
    },
    {
      selector: 'node.type-recombination',
      style: { 'shape': 'triangle' },
    },
    {
      selector: 'edge',
      style: {
        'width': 0.3,
        'line-color': '#e5e7eb',
        'target-arrow-color': '#d1d5db',
        'target-arrow-shape': 'triangle',
        'arrow-scale': 0.4,
        'curve-style': 'bezier',
      },
    },
  ], [])

  const layoutOptions = useMemo(() => {
    if (layout === 'cose') {
      return {
        name: 'cose',
        idealEdgeLength: 80,
        nodeOverlap: 20,
        refresh: 20,
        fit: true,
        padding: 30,
        randomize: false,
        componentSpacing: 100,
        nodeRepulsion: 200000,
        edgeElasticity: 100,
        nestingFactor: 5,
        gravity: 80,
        numIter: 2000,
        initialTemp: 200,
        coolingFactor: 0.95,
        minTemp: 1.0,
      }
    }
    if (layout === 'breadthfirst') {
      return {
        name: 'breadthfirst',
        directed: true,
        spacingFactor: 1.1,
        roots: data?.nodes.find(n => n.generation_type === 'parent')?.node_id,
      }
    }
    if (layout === 'concentric') {
      return { name: 'concentric', fit: true, padding: 30 }
    }
    return { name: layout, fit: true, padding: 30 }
  }, [layout, data])

  // Count nodes by tag for current filter state
  const tagCounts = useMemo(() => {
    if (!data) return {}
    let nodes = data.nodes
    if (hideNeutral) {
      nodes = nodes.filter(n => n.ion_mode !== 'neutral' || n.generation_type === 'parent')
    }
    const counts: Record<string, number> = {}
    nodes.forEach(n => {
      const tag = n.diagnostic_tag || 'unlabeled'
      counts[tag] = (counts[tag] || 0) + 1
    })
    return counts
  }, [data, hideNeutral])

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
        <span>Failed to load network data.</span>
      </div>
    )
  }

  const visibleNodeCount = elements.filter(e => 'label' in (e.data || {})).length
  const isLarge = visibleNodeCount > 500

  return (
    <div className="space-y-3">
      {/* Controls */}
      <div className="flex items-center gap-3 flex-wrap text-sm">
        <label className="flex items-center gap-1.5 text-gray-600">
          <input type="checkbox" checked={hideStructOnly}
            onChange={(e) => setHideStructOnly(e.target.checked)} className="rounded" />
          Hide StructOnly
        </label>

        <label className="flex items-center gap-1.5 text-gray-600">
          <input type="checkbox" checked={hideNeutral}
            onChange={(e) => setHideNeutral(e.target.checked)} className="rounded" />
          Hide neutral intermediates
        </label>

        <div className="flex items-center gap-1">
          <Filter size={14} className="text-gray-400" />
          <select value={tagFilter} onChange={(e) => setTagFilter(e.target.value)}
            className="border rounded px-2 py-1 bg-white text-sm">
            {TAG_OPTIONS.map(o => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </div>

        <select value={layout} onChange={(e) => setLayout(e.target.value)}
          className="border rounded px-2 py-1 bg-white text-sm">
          <option value="cose">Force-directed</option>
          <option value="breadthfirst">Breadth-first</option>
          <option value="concentric">Concentric</option>
          <option value="grid">Grid</option>
        </select>

        <span className="text-gray-400 text-xs">
          {visibleNodeCount} nodes, {elements.length - visibleNodeCount} edges
        </span>
      </div>

      {/* Evidence tag chips */}
      <div className="flex flex-wrap gap-2 text-xs">
        {Object.entries(tagCounts).map(([tag, count]) => (
          <button
            key={tag}
            onClick={() => setTagFilter(tagFilter === tag ? '' : tag)}
            className={`px-2 py-0.5 rounded-full transition-colors ${
              tagFilter === tag
                ? 'bg-blue-100 text-blue-700 font-medium'
                : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
            }`}
          >
            {tag.replace(/_/g, ' ')}: {count}
          </button>
        ))}
      </div>

      {isLarge && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-2 text-sm text-amber-700">
          Large network ({visibleNodeCount} nodes). Use tag filters or "Hide neutral intermediates" to reduce. Rendering may be slow.
        </div>
      )}

      {/* Legend */}
      <div className="flex flex-wrap gap-3 text-xs">
        <Legend color="#22c55e" label="ValDiag" />
        <Legend color="#3b82f6" label="ValGen" />
        <Legend color="#f59e0b" label="FeatSupp" />
        <Legend color="#ef4444" label="GenHC" />
        <Legend color="#93c5fd" label="Unlabeled" />
        <Legend color="#60a5fa" label="Parent" shape="■" size="lg" />
      </div>

      {/* Network graph */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden" style={{ height: 650 }}>
        <CytoscapeComponent
          key={`${id}-${tagFilter}-${hideNeutral}-${layout}`}
          elements={elements}
          stylesheet={stylesheet}
          layout={layoutOptions}
          style={{ width: '100%', height: '100%' }}
          wheelSensitivity={0.3}
          autoungrabify={false}
          autounselectify={false}
          minZoom={0.1}
          maxZoom={5}
        />
      </div>
    </div>
  )
}

function Legend({ color, label, shape = 'circle', size = 'md' }: {
  color: string; label: string; shape?: string; size?: string
}) {
  const sizeClass = size === 'lg' ? 'w-4 h-4' : 'w-3 h-3'
  const radius = shape === '■' ? 'rounded-sm' : 'rounded-full'
  return (
    <div className="flex items-center gap-1">
      <span className={`${sizeClass} ${radius} inline-block`} style={{ backgroundColor: color }} />
      <span className="text-gray-500">{label}</span>
    </div>
  )
}
