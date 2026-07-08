import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import { useState } from 'react'
import SankeyChart from '../components/SankeyChart'
import PathTree from '../components/PathTree'
import { AlertCircle, GitBranch, Network, Hexagon } from 'lucide-react'

type ViewMode = 'tree' | 'sankey'

export default function NetworkPage() {
  const { id } = useParams<{ id: string }>()
  const [viewMode, setViewMode] = useState<ViewMode>('tree')

  const { data: material } = useQuery({
    queryKey: ['material', id],
    queryFn: () => api.getMaterial(id!),
    enabled: !!id,
  })

  const { data: treeData, isLoading: treeLoading } = useQuery({
    queryKey: ['network-tree', id],
    queryFn: async () => {
      const res = await fetch(`/api/materials/${id}/network-tree?max_depth=5&max_children=15`)
      if (!res.ok) throw new Error('Failed')
      return res.json()
    },
    enabled: !!id,
  })

  const { data: sankeyData, isLoading: sankeyLoading } = useQuery({
    queryKey: ['network-sankey', id],
    queryFn: async () => {
      const res = await fetch(`/api/materials/${id}/network-sankey`)
      if (!res.ok) throw new Error('Failed')
      return res.json()
    },
    enabled: !!id && viewMode === 'sankey',
  })

  const isLoading = treeLoading || (viewMode === 'sankey' && sankeyLoading)

  if (isLoading) {
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
            onClick={() => setViewMode('tree')}
            className={`flex items-center gap-1 px-3 py-1.5 rounded-md text-sm transition-colors ${
              viewMode === 'tree' ? 'bg-white text-blue-700 shadow-sm font-medium' : 'text-gray-500'
            }`}
          >
            <Network size={14} /> Path Tree
          </button>
          <button
            onClick={() => setViewMode('sankey')}
            className={`flex items-center gap-1 px-3 py-1.5 rounded-md text-sm transition-colors ${
              viewMode === 'sankey' ? 'bg-white text-blue-700 shadow-sm font-medium' : 'text-gray-500'
            }`}
          >
            <GitBranch size={14} /> Flow Sankey
          </button>
        </div>
      </div>

      <div className="flex gap-4">
        {/* Parent molecule sidebar */}
        {material && (
          <div className="w-48 shrink-0">
            <div className="bg-white rounded-xl border border-gray-200 p-4 sticky top-4">
              <div className="flex items-center gap-2 mb-3">
                <Hexagon size={16} className="text-blue-600" />
                <span className="text-xs font-semibold text-gray-500 uppercase">Parent</span>
              </div>
              <div className="space-y-2">
                <div>
                  <div className="text-xs text-gray-400">Material</div>
                  <div className="text-sm font-semibold text-gray-800">{material.compound_id}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-400">Name</div>
                  <div className="text-xs text-gray-600 leading-tight">{material.name}</div>
                </div>
                {material.formula && (
                  <div>
                    <div className="text-xs text-gray-400">Formula</div>
                    <code className="text-sm font-mono text-blue-700">{material.formula}</code>
                  </div>
                )}
                {material.smiles && (
                  <div>
                    <div className="text-xs text-gray-400">SMILES</div>
                    <code className="text-xs font-mono text-gray-500 break-all leading-tight line-clamp-3">{material.smiles}</code>
                  </div>
                )}
                {material.group && (
                  <div>
                    <div className="text-xs text-gray-400">Group</div>
                    <div className="text-xs text-gray-600 capitalize">{material.group.replace(/_/g, ' ')}</div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Visualization */}
        <div className="flex-1 bg-white rounded-xl border border-gray-200 p-4 min-w-0">
          {viewMode === 'tree' && treeData && (
            <PathTree data={treeData} />
          )}
          {viewMode === 'tree' && !treeData?.children?.length && (
            <div className="flex items-center justify-center h-64 text-gray-400">
              <AlertCircle size={24} className="mr-2" /> No tree data available
            </div>
          )}
          {viewMode === 'sankey' && sankeyData && (
            <SankeyChart
              nodes={sankeyData.nodes}
              links={sankeyData.links}
              totalFormulas={sankeyData.total_formulas}
            />
          )}
        </div>
      </div>
    </div>
  )
}
