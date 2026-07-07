import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import SankeyChart from '../components/SankeyChart'
import { AlertCircle, GitBranch, Hexagon } from 'lucide-react'

export default function NetworkPage() {
  const { id } = useParams<{ id: string }>()

  // Material info for parent display
  const { data: material } = useQuery({
    queryKey: ['material', id],
    queryFn: () => api.getMaterial(id!),
    enabled: !!id,
  })

  // Sankey data
  const { data: sankeyData, isLoading } = useQuery({
    queryKey: ['network-sankey', id],
    queryFn: async () => {
      const res = await fetch(`/api/materials/${id}/network-sankey`)
      if (!res.ok) throw new Error('Failed')
      return res.json()
    },
    enabled: !!id,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    )
  }

  if (!sankeyData?.nodes?.length) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400">
        <AlertCircle size={24} className="mx-auto mb-2" />
        No network data available for this material
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {/* Parent molecule card + Sankey */}
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

        {/* Sankey diagram */}
        <div className="flex-1 bg-white rounded-xl border border-gray-200 p-4 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <GitBranch size={14} className="text-gray-400" />
            <span className="text-xs text-gray-500">
              Flow: generation type → ion mode → evidence tag
            </span>
            <span className="text-xs text-gray-400 ml-auto">
              {sankeyData.total_formulas} ionized formulas
            </span>
          </div>
          <SankeyChart
            nodes={sankeyData.nodes}
            links={sankeyData.links}
            totalFormulas={sankeyData.total_formulas}
          />
        </div>
      </div>
    </div>
  )
}
