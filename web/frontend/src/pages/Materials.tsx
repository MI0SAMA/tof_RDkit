import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { Beaker, ChevronRight } from 'lucide-react'

export default function Materials() {
  const navigate = useNavigate()
  const { data: materials, isLoading } = useQuery({
    queryKey: ['materials'],
    queryFn: api.getMaterials,
  })

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
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Materials</h2>
        <p className="text-sm text-gray-500 mt-1">{materials?.length || 0} materials in database</p>
      </div>

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
