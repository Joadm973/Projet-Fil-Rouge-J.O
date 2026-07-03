import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchJSON } from '../lib/api'
import type { Data } from 'plotly.js'
import { REGION_COLORS } from '../lib/plotly'
import SectionHeader from '../components/SectionHeader'
import PlotlyChart from '../components/PlotlyChart'
import { Insight, Warning } from '../components/InsightBox'

type Tab = 'percapita' | 'region' | 'gdp' | 'table'

export default function Multisource() {
  const [tab, setTab] = useState<Tab>('percapita')
  const [minMedals, setMinMedals] = useState(10)
  const [topN, setTopN] = useState(20)

  const { data: overview } = useQuery({ queryKey: ['ms-overview'], queryFn: () => fetchJSON<any>('/multisource/overview') })
  const { data: perCap } = useQuery({ queryKey: ['per-capita', minMedals, topN], queryFn: () => fetchJSON<any[]>('/multisource/per-capita', { min_medals: minMedals, top_n: topN }) })
  const { data: scatter } = useQuery({ queryKey: ['ms-scatter'], queryFn: () => fetchJSON<any[]>('/multisource/scatter') })
  const { data: byRegion } = useQuery({ queryKey: ['by-region'], queryFn: () => fetchJSON<any[]>('/multisource/by-region') })
  const { data: regionTrend } = useQuery({ queryKey: ['region-trend'], queryFn: () => fetchJSON<any[]>('/multisource/region-trend') })
  const { data: gdp } = useQuery({ queryKey: ['gdp-scatter'], queryFn: () => fetchJSON<any[]>('/multisource/gdp-scatter') })
  const { data: table } = useQuery({ queryKey: ['ms-table'], queryFn: () => fetchJSON<any[]>('/multisource/table') })

  // Per capita bar
  const perCapData = [{
    type: 'bar' as const, orientation: 'h' as const,
    x: (perCap ?? []).map(r => r.medals_per_million),
    y: (perCap ?? []).map(r => r.Team),
    marker: { color: (perCap ?? []).map(r => r.medals_per_million), colorscale: 'YlOrRd', showscale: false },
    text: (perCap ?? []).map(r => r.medals_per_million?.toFixed(2)), textposition: 'outside' as const,
  }]

  // Scatter pop vs medals
  const regions = [...new Set((scatter ?? []).map((r: any) => r.region))].filter(Boolean)
  const scatterData: Data[] = regions.map((reg, i) => ({
    type: 'scatter', mode: 'markers',
    name: reg as string,
    x: (scatter ?? []).filter((r: any) => r.region === reg).map((r: any) => r.population),
    y: (scatter ?? []).filter((r: any) => r.region === reg).map((r: any) => r.medals),
    text: (scatter ?? []).filter((r: any) => r.region === reg).map((r: any) => r.Team),
    marker: { size: 8, color: REGION_COLORS[i % REGION_COLORS.length], opacity: 0.7 },
  }))

  // Region pie
  const pieData = [{
    type: 'pie' as const,
    labels: (byRegion ?? []).map(r => r.region),
    values: (byRegion ?? []).map(r => r.medals),
    hole: 0.35,
    marker: { colors: REGION_COLORS },
  }]

  // Region trend area
  const trendRegions = [...new Set((regionTrend ?? []).map((r: any) => r.region))].filter(Boolean)
  const trendData: Data[] = trendRegions.map((reg, i) => ({
    type: 'scatter', fill: 'tonexty', mode: 'lines',
    name: reg as string,
    x: (regionTrend ?? []).filter((r: any) => r.region === reg).map((r: any) => r.Year),
    y: (regionTrend ?? []).filter((r: any) => r.region === reg).map((r: any) => r.share_pct),
    line: { color: REGION_COLORS[i % REGION_COLORS.length], width: 1.5 },
    fillcolor: `${REGION_COLORS[i % REGION_COLORS.length]}30`,
  }))

  // GDP scatter
  const gdpRegions = [...new Set((gdp ?? []).map((r: any) => r.region))].filter(Boolean)
  const gdpData: Data[] = gdpRegions.map((reg, i) => ({
    type: 'scatter', mode: 'markers',
    name: reg as string,
    x: (gdp ?? []).filter((r: any) => r.region === reg).map((r: any) => r.gdp_per_capita),
    y: (gdp ?? []).filter((r: any) => r.region === reg).map((r: any) => r.medals_per_million),
    text: (gdp ?? []).filter((r: any) => r.region === reg).map((r: any) => r.Team),
    marker: { size: 7, color: REGION_COLORS[i % REGION_COLORS.length], opacity: 0.75 },
  }))

  const overPerformers = [...(gdp ?? [])].sort((a: any, b: any) => b.overperformance - a.overperformance).slice(0, 12)
  const overData = [{
    type: 'bar' as const, orientation: 'h' as const,
    x: overPerformers.map(r => r.overperformance), y: overPerformers.map(r => r.Team),
    marker: { color: overPerformers.map(r => r.overperformance > 0 ? '#10b981' : '#ef4444') },
    text: overPerformers.map(r => `${r.overperformance > 0 ? '+' : ''}${r.overperformance?.toFixed(2)}`),
    textposition: 'outside' as const,
  }]

  const TABS = [
    { id: 'percapita' as Tab, label: '🏅 Médailles / habitant' },
    { id: 'region' as Tab, label: '🌍 Par région' },
    { id: 'gdp' as Tab, label: '💰 Médailles vs PIB' },
    { id: 'table' as Tab, label: '📊 Données fusionnées' },
  ]

  return (
    <div>
      <h1 className="text-2xl font-black text-slate-800 mb-1" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>🌐 Analyse multi-sources</h1>
      <p className="text-slate-500 text-sm mb-6">Données JO (Kaggle) enrichies avec la <strong>World Bank API</strong> (population, PIB, région).</p>

      {/* Source cards */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 border border-blue-100 rounded-2xl p-4">
          <div className="text-xs text-blue-500 font-medium mb-1">Source 1 — CSV Kaggle</div>
          <div className="font-bold text-slate-800">Données JO</div>
          <div className="text-xs text-slate-500 mt-0.5">252 565 participations · 1896–2024</div>
        </div>
        <div className="bg-emerald-50 border border-emerald-100 rounded-2xl p-4">
          <div className="text-xs text-emerald-500 font-medium mb-1">Source 2 — World Bank API</div>
          <div className="font-bold text-slate-800">Métadonnées pays</div>
          <div className="text-xs text-slate-500 mt-0.5">250+ pays · Population, PIB, région</div>
        </div>
        <div className="bg-white border border-slate-100 rounded-2xl p-4 shadow-sm">
          <div className="text-xs text-slate-400 font-medium mb-1">Couverture</div>
          <div className="font-bold text-slate-800">{overview ? `${overview.matched} / ${overview.total_countries}` : '…'}</div>
          <div className="text-xs text-slate-500 mt-0.5">Pays avec données World Bank</div>
        </div>
      </div>

      <div className="flex gap-1 bg-slate-100 p-1 rounded-xl mb-6 w-fit">
        {TABS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${tab === t.id ? 'bg-white shadow-sm text-blue-600' : 'text-slate-500 hover:text-slate-700'}`}>
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'percapita' && (
        <div>
          <div className="flex gap-4 mb-4 flex-wrap items-end">
            <div className="flex flex-col gap-1">
              <label className="text-xs font-medium text-slate-500">Médailles min : {minMedals}</label>
              <input type="range" min={1} max={50} value={minMedals} onChange={e => setMinMedals(+e.target.value)} className="accent-blue-500" />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-xs font-medium text-slate-500">Top N : {topN}</label>
              <input type="range" min={10} max={30} value={topN} onChange={e => setTopN(+e.target.value)} className="accent-blue-500" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <PlotlyChart data={perCapData} layout={{ yaxis: { categoryorder: 'total ascending' }, title: { text: 'Top pays — médailles / million hab.' } }} height={480} />
            <PlotlyChart data={scatterData} layout={{ xaxis: { type: 'log', title: { text: 'Population (log)' } }, yaxis: { title: { text: 'Médailles totales' } }, title: { text: 'Population vs médailles' }, legend: { orientation: 'h', y: -0.2 } }} height={480} />
          </div>
          <Insight>La <strong>médaille par habitant</strong> corrige le biais de taille. Des petits pays comme la Finlande ou la Jamaïque se distinguent bien plus qu'avec le classement brut.</Insight>
        </div>
      )}

      {tab === 'region' && (
        <div>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <PlotlyChart data={pieData} layout={{ title: { text: 'Part des médailles par région' } }} height={380} />
            <PlotlyChart data={[{
              type: 'bar', orientation: 'h',
              x: (byRegion ?? []).map(r => r.medals_per_million), y: (byRegion ?? []).map(r => r.region),
              marker: { color: '#10b981' },
              text: (byRegion ?? []).map(r => r.medals_per_million?.toFixed(2)), textposition: 'outside',
            }]} layout={{ yaxis: { categoryorder: 'total ascending' }, title: { text: 'Médailles / million — par région' } }} height={380} />
          </div>
          <PlotlyChart data={trendData} layout={{ title: { text: 'Part de chaque région (1992–2024)' }, yaxis: { title: { text: 'Part (%)' } }, legend: { orientation: 'h', y: -0.2 } }} height={400} />
          <Insight>La progression de l'Asie de l'Est est nette depuis 1992. L'Europe reste dominante mais son poids relatif décline progressivement.</Insight>
        </div>
      )}

      {tab === 'gdp' && (
        <div>
          <PlotlyChart data={gdpData} layout={{ xaxis: { type: 'log', title: { text: 'PIB/hab. (USD, log)' } }, yaxis: { title: { text: 'Médailles / million hab.' } }, title: { text: 'Richesse vs performance olympique' }, legend: { orientation: 'h', y: -0.2 } }} height={460} />
          <SectionHeader title="Sur / sous-performers" />
          <PlotlyChart data={overData} layout={{ yaxis: { categoryorder: 'total ascending' }, title: { text: 'Score de sur-performance (rang médailles − rang PIB)' } }} height={420} />
          <Warning>La corrélation PIB–médailles est réelle mais imparfaite. Tradition sportive et disciplines pratiquées jouent un rôle crucial.</Warning>
        </div>
      )}

      {tab === 'table' && (
        <div>
          <SectionHeader title="📊 Données fusionnées CSV × World Bank" />
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
            <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-slate-50 border-b border-slate-100">
                  <tr>{['NOC', 'Pays', 'Médailles', 'Médailles/M hab.', 'Population', 'PIB/hab.', 'Région', 'Revenu'].map(h => (
                    <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">{h}</th>
                  ))}</tr>
                </thead>
                <tbody>
                  {(table ?? []).slice(0, 100).map((r: any, i: number) => (
                    <tr key={i} className={`border-b border-slate-50 hover:bg-slate-50/50 transition-colors ${i % 2 ? 'bg-slate-50/30' : ''}`}>
                      <td className="px-4 py-2 font-mono text-xs text-slate-400">{r.NOC}</td>
                      <td className="px-4 py-2 font-medium text-slate-800">{r.Team}</td>
                      <td className="px-4 py-2 text-right font-semibold text-blue-600">{r.medals?.toLocaleString()}</td>
                      <td className="px-4 py-2 text-right text-emerald-600">{r.medals_per_million?.toFixed(2)}</td>
                      <td className="px-4 py-2 text-right text-slate-500">{r.population ? (r.population / 1e6).toFixed(1) + 'M' : '—'}</td>
                      <td className="px-4 py-2 text-right text-slate-500">{r.gdp_per_capita ? '$' + Math.round(r.gdp_per_capita).toLocaleString() : '—'}</td>
                      <td className="px-4 py-2 text-slate-500">{r.region ?? '—'}</td>
                      <td className="px-4 py-2 text-slate-400 text-xs">{r.income_level ?? '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          <button
            onClick={() => {
              const csv = ['NOC,Team,medals,medals_per_million,population,gdp_per_capita,region,income_level']
                .concat((table ?? []).map((r: any) => `${r.NOC},${r.Team},${r.medals},${r.medals_per_million},${r.population},${r.gdp_per_capita},${r.region},${r.income_level}`))
                .join('\n')
              const a = document.createElement('a')
              a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }))
              a.download = 'jo_world_bank_enriched.csv'
              a.click()
            }}
            className="mt-3 bg-slate-800 hover:bg-slate-700 text-white text-sm font-medium px-4 py-2 rounded-xl transition-all"
          >
            ⬇️ Télécharger CSV
          </button>
        </div>
      )}

      <div className="text-center text-slate-400 text-xs mt-10 pb-4">YPerf · Ynov · 2026</div>
    </div>
  )
}
