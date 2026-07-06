import type { Layout, Config } from 'plotly.js'

export const PLOTLY_LAYOUT: Partial<Layout> = {
  paper_bgcolor: 'transparent',
  plot_bgcolor:  'transparent',
  font: { family: "'Space Grotesk', system-ui, sans-serif", size: 12, color: '#6b6763' },
  margin: { t: 36, r: 12, b: 36, l: 44 },
  hoverlabel: {
    bgcolor: '#ffffff',
    bordercolor: '#e5e1d8',
    font: { size: 12, family: "'Space Grotesk', system-ui, sans-serif", color: '#111010' },
  },
  xaxis: {
    gridcolor: '#f0ede6',
    linecolor: '#e5e1d8',
    zeroline: false,
    tickfont: { size: 11, color: '#9e9993' },
    title: { font: { size: 11, color: '#6b6763' } },
  },
  yaxis: {
    gridcolor: '#f0ede6',
    linecolor: '#e5e1d8',
    zeroline: false,
    tickfont: { size: 11, color: '#9e9993' },
    title: { font: { size: 11, color: '#6b6763' } },
  },
  legend: {
    font: { size: 11, color: '#6b6763' },
    bgcolor: 'transparent',
    borderwidth: 0,
  },
  title: {
    font: { size: 13, color: '#111010', family: "'Space Grotesk', system-ui, sans-serif" },
  },
}

export const PLOTLY_CONFIG: Partial<Config> = {
  displayModeBar: false,
  responsive: true,
}

export const MEDAL_COLORS: Record<string, string> = {
  Gold:   '#c9a227',
  Silver: '#a3a3a3',
  Bronze: '#92664a',
}

export const PALETTE = ['#c9a227', '#374151', '#6b7280', '#d1cdc7', '#9e9993', '#f0ede6']

export const REGION_COLORS = [
  '#c9a227','#374151','#92664a','#6b7280','#a3a3a3','#d1cdc7','#9e9993',
]
