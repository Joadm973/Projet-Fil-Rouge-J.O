import Plot from 'react-plotly.js'
import type { Layout } from 'plotly.js'
import { PLOTLY_LAYOUT, PLOTLY_CONFIG } from '../lib/plotly'

interface Props {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data: any[]
  layout?: Partial<Layout>
  height?: number
  className?: string
}

export default function PlotlyChart({ data, layout, height = 400, className }: Props) {
  return (
    <div className={`bg-white rounded-2xl shadow-sm border border-slate-100 p-4 ${className ?? ''}`}>
      <Plot
        data={data}
        layout={{ ...PLOTLY_LAYOUT, height, ...layout }}
        config={PLOTLY_CONFIG}
        style={{ width: '100%' }}
        useResizeHandler
      />
    </div>
  )
}
