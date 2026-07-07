import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { api, MaterialCard } from '../api/client'
import ReactECharts from 'echarts-for-react'
import { AlertCircle, CheckCircle, Eye, EyeOff, Layers, TrendingUp } from 'lucide-react'

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

  const { global, materials } = data

  // Evidence strategy pie chart
  const strategyPie = {
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: Object.entries(global.strategy_distribution).map(([name, value]) => ({
        name: name.replace(/-/g, ' '),
        value,
      })),
      label: { formatter: '{b}: {c}' },
    }],
  }

  // Material bar chart - val_diag
  const materialBar = {
    tooltip: { trigger: 'axis' },
    grid: { left: 60, right: 20, top: 10, bottom: 80 },
    xAxis: {
      type: 'category',
      data: materials.map(m => m.compound_id),
      axisLabel: { rotate: 45, fontSize: 10 },
    },
    yAxis: { type: 'value' },
    series: [
      {
        name: 'ValDiag',
        type: 'bar',
        data: materials.map(m => m.val_diag),
        itemStyle: { color: '#3b82f6' },
      },
      {
        name: 'ValGen',
        type: 'bar',
        data: materials.map(m => m.val_gen),
        itemStyle: { color: '#22c55e' },
      },
      {
        name: 'FeatSupp',
        type: 'bar',
        data: materials.map(m => m.feat_supp),
        itemStyle: { color: '#f59e0b' },
      },
      {
        name: 'GenHC',
        type: 'bar',
        data: materials.map(m => m.gen_hc),
        itemStyle: { color: '#ef4444' },
      },
    ],
  }

  const getEvidenceColor = (strategy: string) => {
    if (strategy === 'formula-driven') return 'bg-green-100 text-green-800'
    if (strategy === 'pattern-driven') return 'bg-blue-100 text-blue-800'
    if (strategy === 'mixed') return 'bg-yellow-100 text-yellow-800'
    return 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
          <p className="text-sm text-gray-500 mt-1">v3.0 Evidence Integration Overview</p>
        </div>
      </div>

      {/* Global stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
        <StatCard icon={<BeakerIcon />} label="Materials" value={global.total_materials} />
        <StatCard icon={<Layers />} label="Total Formulas" value={global.total_formulas.toLocaleString()} />
        <StatCard icon={<CheckCircle />} label="ValDiag" value={global.total_val_diag} color="text-green-600" />
        <StatCard icon={<CheckCircle />} label="ValGen" value={global.total_val_gen} color="text-blue-600" />
        <StatCard icon={<EyeOff />} label="StructOnly" value={global.total_struct_only.toLocaleString()} color="text-gray-400" />
        <StatCard icon={<Eye />} label="GenHC" value={global.total_gen_hc} color="text-red-500" />
        <StatCard icon={<TrendingUp />} label="Hidden%" value={`${global.hidden_ratio}%`} color="text-orange-500" />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <h3 className="font-semibold text-gray-700 mb-2">Evidence Strategy Distribution</h3>
          <ReactECharts option={strategyPie} style={{ height: 300 }} />
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <h3 className="font-semibold text-gray-700 mb-2">Per-Material Diagnostic Composition</h3>
          <ReactECharts option={materialBar} style={{ height: 350 }} />
        </div>
      </div>

      {/* Material cards */}
      <div>
        <h3 className="font-semibold text-gray-700 mb-3">Material Evidence Summary</h3>
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
              <div className="flex gap-2 mt-3 text-xs">
                <span className="px-1.5 py-0.5 bg-green-100 text-green-700 rounded">VD: {m.val_diag}</span>
                <span className="px-1.5 py-0.5 bg-blue-100 text-blue-700 rounded">VG: {m.val_gen}</span>
                <span className="px-1.5 py-0.5 bg-amber-100 text-amber-700 rounded">FS: {m.feat_supp}</span>
                <span className="px-1.5 py-0.5 bg-gray-100 text-gray-500 rounded">SO: {m.struct_only}</span>
              </div>
              <div className="mt-2 flex items-center gap-1">
                <div className="flex-1 h-1 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full"
                    style={{
                      width: `${Math.min(m.match_rate || 0, 100)}%`,
                      backgroundColor: (m.match_rate || 0) >= 80 ? '#22c55e' : (m.match_rate || 0) >= 50 ? '#f59e0b' : '#ef4444',
                    }}
                  />
                </div>
                <span className="text-xs text-gray-500 w-10 text-right">{m.match_rate || 0}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function StatCard({ icon, label, value, color = 'text-gray-700' }: {
  icon: React.ReactNode
  label: string
  value: string | number
  color?: string
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-3 text-center">
      <div className="flex justify-center mb-1 text-gray-400">{icon}</div>
      <div className={`text-lg font-bold ${color}`}>{value}</div>
      <div className="text-xs text-gray-400">{label}</div>
    </div>
  )
}

function BeakerIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M8 3h8M10 3v6.3a4 4 0 0 0-1.2 2.7H7a1 1 0 0 0 0 2h10a1 1 0 0 0 0-2h-1.8a4 4 0 0 0-1.2-2.7V3" />
      <path d="M6 21h12a1 1 0 0 0 1-1v-1a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v1a1 1 0 0 0 1 1z" />
    </svg>
  )
}
