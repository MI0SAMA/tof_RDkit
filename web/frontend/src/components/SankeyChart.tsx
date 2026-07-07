import { useMemo } from 'react'
import ReactECharts from 'echarts-for-react'

interface SankeyNode {
  name: string
  label?: string
  itemStyle?: { color: string }
}

interface SankeyLink {
  source: string
  target: string
  value: number
}

interface Props {
  nodes: SankeyNode[]
  links: SankeyLink[]
  totalFormulas: number
}

export default function SankeyChart({ nodes, links, totalFormulas }: Props) {
  const option = useMemo(() => {
    // Map node names to display labels
    const labelMap: Record<string, string> = {}
    nodes.forEach((n) => {
      labelMap[n.name] = n.label || n.name
    })

    // Aggregate tag totals for right-side summary
    const tagTotals: Record<string, number> = {}
    links.forEach((l) => {
      if (l.target.startsWith('tag:')) {
        const tag = l.target.replace('tag:', '')
        tagTotals[tag] = (tagTotals[tag] || 0) + l.value
      }
    })

    return {
      tooltip: {
        trigger: 'item',
        triggerOn: 'mousemove',
        formatter: (params: { data?: { source?: string; target?: string; value?: number }; name?: string; value?: number }) => {
          if (params.data && 'source' in params.data) {
            const d = params.data as { source: string; target: string; value: number }
            const src = labelMap[d.source] || d.source
            const tgt = labelMap[d.target] || d.target
            return `${src} → ${tgt}<br/>Formulas: <b>${d.value}</b>`
          }
          return `${params.name}: <b>${params.value}</b> formulas`
        },
      },
      series: [
        {
          type: 'sankey',
          layout: 'none',
          emphasis: { focus: 'adjacency' },
          nodeAlign: 'left',
          layoutIterations: 0,
          data: nodes.map((n) => ({
            name: n.name,
            itemStyle: n.itemStyle || { color: '#93c5fd' },
            label: {
              show: true,
              position: n.name.startsWith('gen:') ? 'left' : n.name.startsWith('tag:') ? 'right' : 'inside',
              fontSize: 11,
              formatter: (p: { name: string }) => {
                const label = labelMap[p.name] || p.name
                const val = n.name.startsWith('tag:')
                  ? tagTotals[n.name.replace('tag:', '')] || 0
                  : undefined
                return val !== undefined ? `${label}\n(${val})` : label
              },
            },
          })),
          links: links.map((l) => ({
            source: l.source,
            target: l.target,
            value: l.value,
            lineStyle: {
              color: 'gradient',
              curveness: 0.5,
              opacity: 0.4,
            },
          })),
        },
      ],
    }
  }, [nodes, links])

  if (!nodes.length) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400 text-sm">
        No data available for Sankey diagram
      </div>
    )
  }

  return (
    <div>
      <div className="text-xs text-gray-400 mb-1">
        {totalFormulas} unique ionized formulas. Band width = formula count. Hover for details.
      </div>
      <ReactECharts
        option={option}
        style={{ height: 500, width: '100%' }}
        opts={{ renderer: 'svg' }}
      />
    </div>
  )
}
