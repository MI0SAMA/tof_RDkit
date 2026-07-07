import { Outlet, NavLink, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import { ArrowLeft, Share2, GitGraph, Table2, FileText, Crosshair } from 'lucide-react'

export default function MaterialLayout() {
  const { id } = useParams<{ id: string }>()
  const { data: material } = useQuery({
    queryKey: ['material', id],
    queryFn: () => api.getMaterial(id!),
    enabled: !!id,
  })

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-3">
        <NavLink to="/materials" className="text-gray-400 hover:text-gray-600">
          <ArrowLeft size={20} />
        </NavLink>
        <div>
          <h2 className="text-xl font-bold text-gray-900">
            {material?.compound_id || id}
          </h2>
          {material && (
            <p className="text-sm text-gray-500">{material.name}</p>
          )}
        </div>
        {material?.formula && (
          <code className="ml-auto text-sm bg-gray-100 px-3 py-1 rounded-lg text-gray-600">
            {material.formula}
          </code>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 rounded-lg p-1 w-fit">
        <TabLink to={`/materials/${id}/network`} icon={<Share2 size={14} />} label="Network" />
        <TabLink to={`/materials/${id}/formulas`} icon={<Table2 size={14} />} label="Formulas" />
        <TabLink to={`/materials/${id}/evidence`} icon={<FileText size={14} />} label="Evidence" />
        <TabLink to={`/materials/${id}/match-peaks`} icon={<Crosshair size={14} />} label="Match Peaks" />
      </div>

      {/* Tab content */}
      <Outlet />
    </div>
  )
}

function TabLink({ to, icon, label }: { to: string; icon: React.ReactNode; label: string }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-colors ${
          isActive ? 'bg-white text-blue-700 shadow-sm font-medium' : 'text-gray-500 hover:text-gray-700'
        }`
      }
    >
      {icon}
      {label}
    </NavLink>
  )
}
