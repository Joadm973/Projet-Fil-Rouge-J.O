import Plot from 'react-plotly.js'
import type { Layout } from 'plotly.js'
import { PLOTLY_LAYOUT, PLOTLY_CONFIG } from '../lib/plotly'

interface Props {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data: any[]
  layout?: Partial<Layout>
  height?: number
  style?: React.CSSProperties
}

export default function PlotlyChart({ data, layout, height = 380, style }: Props) {
  return (
    <div className="card" style={{ padding: '4px', overflow: 'hidden', ...style }}>
      <Plot
        data={data}
        layout={{
          ...PLOTLY_LAYOUT,
          ...layout,
          height,
          xaxis: { ...PLOTLY_LAYOUT.xaxis, ...layout?.xaxis },
          yaxis: { ...PLOTLY_LAYOUT.yaxis, ...layout?.yaxis },
          hoverlabel: { ...PLOTLY_LAYOUT.hoverlabel, ...layout?.hoverlabel },
          legend: { ...PLOTLY_LAYOUT.legend, ...layout?.legend },
          title: { ...PLOTLY_LAYOUT.title, ...layout?.title },
        }}
        config={PLOTLY_CONFIG}
        style={{ width: '100%' }}
        useResizeHandler
      />
    </div>
  )
}
