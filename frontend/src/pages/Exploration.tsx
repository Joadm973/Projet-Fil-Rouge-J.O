import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchJSON } from '../lib/api'
import { MEDAL_COLORS } from '../lib/plotly'
import SectionHeader from '../components/SectionHeader'
import PlotlyChart from '../components/PlotlyChart'
import Spinner from '../components/Spinner'
import { Insight } from '../components/InsightBox'

type Tab = 'pays' | 'sports' | 'tendances' | 'heatmap'

export default function Exploration() {
  const { data: meta } = useQuery({ queryKey: ['exp-meta'], queryFn: () => fetchJSON<{ year_min: number; year_max: number }>('/exploration/meta') })
  const [yearMin, setYearMin] = useState(1896)
  const [yearMax, setYearMax] = useState(2024)
  const [gender, setGender] = useState('all')
  const [tab, setTab] = useState<Tab>('pays')
  const [topN, setTopN] = useState(15)

  const params = { year_min: yearMin, year_max: yearMax, gender, top_n: topN }

  const { data: countries, isLoading: lc } = useQuery({ queryKey: ['top-countries', params], queryFn: () => fetchJSON<any[]>('/exploration/top-countries', params) })
  const { data: sports, isLoading: ls } = useQuery({ queryKey: ['top-sports', params], queryFn: () => fetchJSON<any[]>('/exploration/top-sports', params) })
  const { data: trends, isLoading: lt } = useQuery({ queryKey: ['trends', params], queryFn: () => fetchJSON<any>('/exploration/trends', params) })
  const { data: heatmap, isLoading: lh } = useQuery({ queryKey: ['heatmap', { year_min: yearMin, year_max: yearMax, top_n: topN }], queryFn: () => fetchJSON<any[]>('/exploration/heatmap', { year_min: yearMin, year_max: yearMax, top_n: topN }) })
  const { data: choropleth } = useQuery({ queryKey: ['choropleth', params], queryFn: () => fetchJSON<any[]>('/exploration/choropleth', params) })

  const TABS: { id: Tab; label: string }[] = [
    { id: 'pays', label: '🏆 Pays' },
    { id: 'sports', label: '🏋️ Sports' },
    { id: 'tendances', label: '📈 Tendances' },
    { id: 'heatmap', label: '🔥 Heatmap' },
  ]

  // Top countries stacked bar
  const medalTypes = ['Gold', 'Silver', 'Bronze']
  const topTeams = [...new Set((countries ?? []).map(r => r.Team))].slice(0, topN)
  const countryData = medalTypes.map(medal => ({
    type: 'bar' as const,
    name: medal,
    x: topTeams,
    y: topTeams.map(t => (countries ?? []).find(r => r.Team === t && r.Medal === medal)?.count ?? 0),
    marker: { color: MEDAL_COLORS[medal] },
  }))

  // Top sports
  const sportNames = [...new Set((sports ?? []).map(r => r.Sport))].slice(0, 20)
  const sportsData = ['Hommes', 'Femmes'].map(sex => ({
    type: 'bar' as const, name: sex,
    x: sportNames,
    y: sportNames.map(s => (sports ?? []).find(r => r.Sport === s && r.Sex === sex)?.count ?? 0),
    marker: { color: sex === 'Hommes' ? '#3b82f6' : '#ec4899' },
  }))

  // Trends
  const goldData = [{
    type: 'scatter' as const, mode: 'lines+markers' as const, name: 'Or',
    x: trends?.gold_by_year?.map((r: any) => r.Year) ?? [],
    y: trends?.gold_by_year?.map((r: any) => r.gold) ?? [],
    line: { color: '#f59e0b', width: 2.5 },
  }]

  // Heatmap
  const heatTeams = [...new Set((heatmap ?? []).map(r => r.Team))]
  const heatYears = [...new Set((heatmap ?? []).map(r => r.Year))].sort()
  const heatMatrix = heatTeams.map(team =>
    heatYears.map(year => (heatmap ?? []).find(r => r.Team === team && r.Year === year)?.gold ?? 0)
  )
  const heatData = [{
    type: 'heatmap' as const,
    x: heatYears, y: heatTeams, z: heatMatrix,
    colorscale: 'Blues', showscale: true,
  }]

  return (
    <div>
      <h1 className="text-2xl font-black text-slate-800 mb-1" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
        🔍 Exploration des Données
      </h1>
      <p className="text-slate-500 text-sm mb-6">Analysez les performances olympiques selon vos critères.</p>

      {/* Filters */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5 mb-6 flex gap-6 flex-wrap items-end">
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-slate-500">Période : {yearMin} – {yearMax}</label>
          <div className="flex gap-2">
            <input type="range" min={meta?.year_min ?? 1896} max={yearMax} value={yearMin} onChange={e => setYearMin(+e.target.value)} className="accent-blue-500" />
            <input type="range" min={yearMin} max={meta?.year_max ?? 2024} value={yearMax} onChange={e => setYearMax(+e.target.value)} className="accent-blue-500" />
          </div>
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-slate-500">Genre</label>
          <select value={gender} onChange={e => setGender(e.target.value)} className="text-sm border border-slate-200 rounded-lg px-3 py-1.5">
            <option value="all">Tous</option>
            <option value="m">Hommes</option>
            <option value="f">Femmes</option>
          </select>
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-slate-500">Top N : {topN}</label>
          <input type="range" min={5} max={30} value={topN} onChange={e => setTopN(+e.target.value)} className="accent-blue-500" />
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-100 p-1 rounded-xl mb-6 w-fit">
        {TABS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${tab === t.id ? 'bg-white shadow-sm text-blue-600' : 'text-slate-500 hover:text-slate-700'}`}>
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'pays' && (
        <div>
          <SectionHeader title="🏆 Classement des pays" />
          {lc ? <Spinner /> : (
            <div className="grid grid-cols-2 gap-4">
              <PlotlyChart
                data={countryData}
                layout={{ barmode: 'stack', xaxis: { tickangle: -30 }, title: { text: `Top ${topN} pays — ${yearMin}–${yearMax}` } }}
                height={400}
              />
              <PlotlyChart
                data={[{ type: 'choropleth', locations: choropleth?.map(r => r.NOC) ?? [], z: choropleth?.map(r => r.total) ?? [], text: choropleth?.map(r => r.Team) ?? [], colorscale: 'YlOrRd' }]}
                layout={{ geo: { showframe: false, bgcolor: 'rgba(0,0,0,0)' }, margin: { t: 44, r: 0, b: 0, l: 0 } }}
                height={400}
              />
            </div>
          )}
        </div>
      )}

      {tab === 'sports' && (
        <div>
          <SectionHeader title="🏋️ Top disciplines" />
          {ls ? <Spinner /> : (
            <PlotlyChart
              data={sportsData}
              layout={{ barmode: 'group', xaxis: { tickangle: -30 }, title: { text: `Médailles par discipline — ${yearMin}–${yearMax}` } }}
              height={440}
            />
          )}
        </div>
      )}

      {tab === 'tendances' && (
        <div>
          <SectionHeader title="📈 Évolution des médailles d'or" />
          {lt ? <Spinner /> : (
            <PlotlyChart data={goldData} layout={{ title: { text: "Médailles d'or par édition" } }} height={400} />
          )}
          <Insight>La progression du nombre de médailles d'or reflète l'augmentation du nombre d'épreuves au programme olympique.</Insight>
        </div>
      )}

      {tab === 'heatmap' && (
        <div>
          <SectionHeader title="🔥 Heatmap — Médailles d'or par pays et édition" />
          {lh ? <Spinner /> : (
            <PlotlyChart
              data={heatData}
              layout={{ title: { text: `Heatmap or — Top ${topN} pays` }, margin: { t: 44, r: 16, b: 60, l: 120 } }}
              height={480}
            />
          )}
        </div>
      )}

      <div className="text-center text-slate-400 text-xs mt-10 pb-4">YPerf · Ynov · 2026</div>
    </div>
  )
}
