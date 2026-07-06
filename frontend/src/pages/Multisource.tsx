import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchJSON } from '../lib/api'
import type { Data } from 'plotly.js'
import { REGION_COLORS } from '../lib/plotly'
import SectionHeader from '../components/SectionHeader'
import PlotlyChart from '../components/PlotlyChart'
import { Insight, Warning } from '../components/InsightBox'
import Tabs from '../components/Tabs'
import PageHeader from '../components/PageHeader'

type Tab = 'percapita' | 'region' | 'gdp' | 'table'

const TABS = [
  { id: 'percapita' as Tab, label: 'Par habitant' },
  { id: 'region' as Tab,    label: 'Régions' },
  { id: 'gdp' as Tab,       label: 'PIB × Médailles' },
  { id: 'table' as Tab,     label: 'Tableau' },
]

const select: React.CSSProperties = {
  fontSize: '0.8rem', fontFamily: 'inherit',
  border: '1px solid var(--border)', borderRadius: 'var(--r-sm)',
  padding: '6px 10px', background: 'var(--surface)', color: 'var(--text-1)',
  cursor: 'pointer', outline: 'none',
}

export default function Multisource() {
  const [tab, setTab] = useState<Tab>('percapita')
  const [minMedals, setMinMedals] = useState(10)
  const [topN, setTopN] = useState(20)

  const { data: overview }    = useQuery({ queryKey: ['ms-overview'],         queryFn: () => fetchJSON<any>('/multisource/overview') })
  const { data: perCap }      = useQuery({ queryKey: ['per-capita', minMedals, topN], queryFn: () => fetchJSON<any[]>('/multisource/per-capita', { min_medals: minMedals, top_n: topN }) })
  const { data: byRegion }    = useQuery({ queryKey: ['by-region'],           queryFn: () => fetchJSON<any[]>('/multisource/by-region') })
  const { data: regionTrend } = useQuery({ queryKey: ['region-trend'],        queryFn: () => fetchJSON<any[]>('/multisource/region-trend') })
  const { data: gdp }         = useQuery({ queryKey: ['gdp-scatter'],         queryFn: () => fetchJSON<any[]>('/multisource/gdp-scatter') })
  const { data: table }       = useQuery({ queryKey: ['ms-table'],            queryFn: () => fetchJSON<any[]>('/multisource/table') })

  const perCapData = [{
    type: 'bar' as const, orientation: 'h' as const,
    x: (perCap ?? []).map(r => r.medals_per_million),
    y: (perCap ?? []).map(r => r.Team),
    marker: { color: '#c9a227', line: { width: 0 } },
    text: (perCap ?? []).map(r => r.medals_per_million?.toFixed(2)), textposition: 'outside' as const,
  }]

  const regions = [...new Set((byRegion ?? []).map((r: any) => r.region))]
  const pieValues = regions.map(reg => (byRegion ?? []).find((r: any) => r.region === reg)?.medals ?? 0)
  const pieTotal = pieValues.reduce((a, b) => a + b, 0)
  const pieData = [{
    type: 'pie' as const,
    labels: regions,
    values: pieValues,
    marker: { colors: REGION_COLORS, line: { color: '#ffffff', width: 1.5 } },
    hole: 0.5,
    text: pieValues.map(v => (pieTotal && v / pieTotal >= 0.05) ? `${Math.round((v / pieTotal) * 100)}%` : ''),
    textinfo: 'text' as const,
    textposition: 'inside' as const,
    insidetextorientation: 'horizontal' as const,
    textfont: { size: 12, color: '#ffffff' },
    hovertemplate: '<b>%{label}</b><br>%{percent}<extra></extra>',
  }]

  const regionYears = [...new Set((regionTrend ?? []).map((r: any) => r.Year))].sort()
  const trendData: Data[] = regions.slice(0, 6).map((reg, i) => ({
    type: 'scatter', mode: 'lines', name: reg,
    x: regionYears,
    y: regionYears.map(y => (regionTrend ?? []).find((r: any) => r.region === reg && r.Year === y)?.medals ?? 0),
    line: { color: REGION_COLORS[i], width: 1.75 },
  }))

  const gdpData = [{
    type: 'scatter' as const, mode: 'markers' as const,
    x: (gdp ?? []).map(r => r.gdp_per_capita),
    y: (gdp ?? []).map(r => r.medals_per_million),
    text: (gdp ?? []).map(r => r.Team),
    marker: { color: '#c9a227', size: 7, opacity: 0.75, line: { color: '#b8911e', width: 1 } },
    hovertemplate: '<b>%{text}</b><br>PIB/hab : %{x:,.0f}$<br>Méd./M : %{y:.2f}<extra></extra>',
  }]

  const tableSlice = (table ?? []).slice(0, 50)

  return (
    <div>
      <PageHeader title="Multi-sources" sub="Fusion données JO × World Bank (PIB, population, régions)." badge="JO × World Bank API" />

      {overview && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '28px' }}>
          {[
            { v: overview.countries_with_data, l: 'pays couplés' },
            { v: overview.coverage_pct?.toFixed(0) + '%', l: 'couverture' },
            { v: overview.total_medals?.toLocaleString(), l: 'médailles' },
            { v: overview.regions, l: 'régions' },
          ].map(({ v, l }) => (
            <div key={l} className="card" style={{ padding: '16px 18px' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, letterSpacing: '-0.03em', color: 'var(--text-1)', marginBottom: '4px' }}>{v}</div>
              <div className="label">{l}</div>
            </div>
          ))}
        </div>
      )}

      {/* Filters */}
      <div className="card" style={{ padding: '14px 20px', marginBottom: '24px', display: 'flex', gap: '24px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
        <div>
          <div className="label" style={{ marginBottom: '6px' }}>Min. médailles · {minMedals}</div>
          <input type="range" min={1} max={50} value={minMedals} onChange={e => setMinMedals(+e.target.value)} style={{ accentColor: 'var(--gold)', width: '120px' }} />
        </div>
        <div>
          <div className="label" style={{ marginBottom: '6px' }}>Top pays · {topN}</div>
          <input type="range" min={5} max={50} value={topN} onChange={e => setTopN(+e.target.value)} style={{ accentColor: 'var(--gold)', width: '120px' }} />
        </div>
      </div>

      <Tabs tabs={TABS} active={tab} onChange={setTab} />

      {tab === 'percapita' && (
        <>
          <SectionHeader title="Médailles par million d'habitants" sub="Performance olympique ramenée à la population" />
          <PlotlyChart data={perCapData} layout={{ yaxis: { categoryorder: 'total ascending' }, margin: { t: 16, r: 72, b: 28, l: 110 } }} height={520} />
          <Insight>Les petites nations peuvent dominer ce classement grâce à leur efficacité, malgré un nombre absolu de médailles plus faible.</Insight>
        </>
      )}

      {tab === 'region' && (
        <>
          <SectionHeader title="Répartition par région du monde" />
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '16px' }}>
            <PlotlyChart data={pieData} layout={{ showlegend: true, legend: { orientation: 'h', y: -0.1, x: 0.5, xanchor: 'center' }, margin: { t: 8, r: 8, b: 8, l: 8 } }} height={420} />
            <PlotlyChart data={trendData} layout={{ showlegend: true, legend: { orientation: 'h', y: -0.14 } }} height={380} />
          </div>
        </>
      )}

      {tab === 'gdp' && (
        <>
          <SectionHeader title="PIB/habitant × Médailles/million" sub="Corrélation entre richesse économique et performance olympique" />
          <PlotlyChart data={gdpData} layout={{ xaxis: { title: { text: 'PIB/habitant ($)' }, type: 'log' }, yaxis: { title: { text: 'Médailles/million hab.' }, type: 'log' } }} height={440} />
          <Warning>La corrélation est positive mais non linéaire. Des petits États hyper-spécialisés dépassent des pays très riches.</Warning>
        </>
      )}

      {tab === 'table' && (
        <>
          <SectionHeader title="Données complètes" sub={`${tableSlice.length} nations avec données World Bank`} />
          <div className="card" style={{ overflow: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--border)' }}>
                  {['Pays', 'NOC', 'Région', 'Médailles', 'PIB/hab.', 'Population', 'Méd./M hab.'].map(h => (
                    <th key={h} style={{ padding: '10px 12px', textAlign: h === 'Pays' || h === 'NOC' || h === 'Région' ? 'left' : 'right', fontWeight: 600, fontSize: '0.72rem', letterSpacing: '0.04em', color: 'var(--text-3)', textTransform: 'uppercase', whiteSpace: 'nowrap' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {tableSlice.map((r: any, i: number) => (
                  <tr key={i} style={{ borderBottom: '1px solid var(--border-soft)' }}>
                    <td style={{ padding: '8px 12px', color: 'var(--text-1)', fontWeight: 500 }}>{r.Team}</td>
                    <td style={{ padding: '8px 12px', color: 'var(--text-3)' }}>{r.NOC}</td>
                    <td style={{ padding: '8px 12px', color: 'var(--text-2)' }}>{r.region}</td>
                    <td style={{ padding: '8px 12px', textAlign: 'right', fontWeight: 600, color: 'var(--text-1)' }}>{r.medals}</td>
                    <td style={{ padding: '8px 12px', textAlign: 'right', color: 'var(--text-2)' }}>{r.gdp_per_capita ? '$' + r.gdp_per_capita.toLocaleString() : '—'}</td>
                    <td style={{ padding: '8px 12px', textAlign: 'right', color: 'var(--text-2)' }}>{r.population ? (r.population / 1e6).toFixed(1) + 'M' : '—'}</td>
                    <td style={{ padding: '8px 12px', textAlign: 'right', color: r.medals_per_million > 1 ? 'var(--gold)' : 'var(--text-2)', fontWeight: r.medals_per_million > 1 ? 600 : 400 }}>{r.medals_per_million?.toFixed(2) ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      <div style={{ borderTop: '1px solid var(--border-soft)', paddingTop: '20px', marginTop: '40px', textAlign: 'center', color: 'var(--text-3)', fontSize: '0.72rem' }}>YPerf · Ynov · 2026</div>
    </div>
  )
}
