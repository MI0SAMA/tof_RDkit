import { useMemo } from 'react'
import ReactECharts from 'echarts-for-react'

interface TreeNode {
  name: string
  edge?: boolean
  formula?: string
  ion_mode?: string
  generation_type?: string
  score?: number
  children?: TreeNode[]
  total_nodes?: number
  total_edges?: number
}

interface Props {
  data: TreeNode
}

export default function PathTree({ data }: Props) {
  const option = useMemo(() => {
    return {
      tooltip: {
        trigger: 'item',
        formatter: (p: { data?: { name?: string; formula?: string; ion_mode?: string; score?: number; edge?: boolean } }) => {
          const d = p.data || {}
          if (d.edge) return `<b>${d.name}</b>`
          const parts = [d.formula || d.name || '']
          if (d.ion_mode && d.ion_mode !== 'neutral') parts.push(`[${d.ion_mode}]`)
          if (d.score !== undefined) parts.push(`score: ${d.score}`)
          return parts.join('<br/>')
        },
      },
      series: [
        {
          type: 'tree',
          data: [data],
          top: '2%',
          left: '2%',
          bottom: '2%',
          right: '15%',
          symbol: 'circle',
          symbolSize: (value: unknown, params: { data?: { edge?: boolean; generation_type?: string; formula?: string; score?: number } }) => {
            const d = params?.data || {}
            if (d.edge) return 0
            if (d.generation_type === 'parent') return 16
            if (d.score !== undefined && d.score >= 0.8) return 10
            return 6
          },
          orient: 'LR',
          expandAndCollapse: true,
          animationDuration: 300,
          animationDurationUpdate: 200,
          label: {
            position: 'right',
            verticalAlign: 'middle',
            align: 'left',
            fontSize: 9,
            formatter: (p: { data?: { edge?: boolean; name?: string; formula?: string } }) => {
              const d = p.data || {}
              if (d.edge) return `— ${d.name} —`
              return d.formula || d.name || ''
            },
          },
          leaves: {
            label: {
              position: 'right',
              verticalAlign: 'middle',
              align: 'left',
              fontSize: 10,
            },
          },
          itemStyle: {
            color: (p: { data?: { edge?: boolean; generation_type?: string; ion_mode?: string; score?: number } }) => {
              const d = p.data || {}
              if (d.edge) return 'transparent'
              if (d.generation_type === 'parent') return '#1e40af'
              if (d.ion_mode === 'positive') return '#2563eb'
              if (d.ion_mode === 'negative') return '#dc2626'
              if (d.score !== undefined && d.score >= 0.8) return '#22c55e'
              return '#93c5fd'
            },
          },
          lineStyle: {
            color: '#d1d5db',
            width: 1,
            curveness: 0.5,
          },
          emphasis: {
            focus: 'descendant',
            lineStyle: { color: '#3b82f6', width: 2 },
          },
        },
      ],
    }
  }, [data])

  if (!data.children?.length) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400 text-sm">
        No tree data available
      </div>
    )
  }

  return (
    <div>
      <div className="text-xs text-gray-400 mb-1">
        Path tree: parent → edge → fragment. Click ⦿ to expand/collapse.
        {data.total_nodes && ` (${data.total_nodes} nodes, ${data.total_edges} edges total)`}
      </div>
      <ReactECharts
        option={option}
        style={{ height: 600, width: '100%' }}
        opts={{ renderer: 'svg' }}
      />
    </div>
  )
}
