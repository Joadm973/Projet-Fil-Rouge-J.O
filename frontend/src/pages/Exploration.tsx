import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchJSON } from '../lib/api'
import { MEDAL_COLORS } from '../lib/plotly'
import SectionHeader from '../components/SectionHeader'
import PlotlyChart from '../components/PlotlyChart'
import Spinner from '../components/Spinner'
import { Insight } from '../components/InsightBox'
import Tabs from '../components/Tabs'
import PageHeader from '../components/PageHeader'

type Tab = 'pays' | 'sports' | 'tendances' | 'heatmap'

const TABS = [
  { id: 'pays' as Tab,      label: 'Pays' },
  { id: 'sports' as Tab,    label: 'Sports' },
  { id: 'tendances' as Tab, label: 'Tendances' },
  { id: 'heatmap' as Tab,   label: 'Heatmap or' },
]

const select: React.CSSProperties = {
  fontSize: '0.8rem', fontFamily: 'inherit',
  border: '1px solid var(--border)', borderRadius: 'var(--r-sm)',
  padding: '5px 10px', background: 'var(--surface)', color: 'var(--text-1)',
  cursor: 'pointer', outline: 'none',
}

export default function Exploration() {
  const { data: meta } = useQuery({ queryKey: ['exp-meta'], queryFn: () => fetchJSON<{ year_min: number; year_max: number }>('/exploration/meta') })
  const [yearMin, setYearMin] = useState(1896)
  const [yearMax, setYearMax] = useState(2024)
  const [gender, setGender] = useState('all')
  const [tab, setTab] = useState<Tab>('pays')
  const [topN, setTopN] = useState(15)

  const params = { year_min: yearMin, year_max: yearMax, gender, top_n: topN }

  const { data: countries, isLoading: lc } = useQuery({ queryKey: ['top-countries', params], queryFn: () => fetchJSON<any[]>('/exploration/top-countries', params) })
  const { data: sports } = useQuery({ queryKey: ['top-sports', params], queryFn: () => fetchJSON<any[]>('/exploration/top-sports', params) })
  const { data: trends } = useQuery({ queryKey: ['trends', params], queryFn: () => fetchJSON<any>('/exploration/trends', params) })
  const { data: heatmap } = useQuery({ queryKey: ['heatmap', { year_min: yearMin, year_max: yearMax, top_n: topN }], queryFn: () => fetchJSON<any[]>('/exploration/heatmap', { year_min: yearMin, year_max: yearMax, top_n: topN }) })
  const { data: choropleth } = useQuery({ queryKey: ['choropleth', params], queryFn: () => fetchJSON<any[]>('/exploration/choropleth', params) })

  // ── Chart data ─────────────────────────────────────────────────────
  const teamTotals = new Map<string, number>()
  for (const r of countries ?? []) teamTotals.set(r.Team, (teamTotals.get(r.Team) ?? 0) + r.count)
  const topTeams = [...teamTotals.keys()].sort((a, b) => teamTotals.get(b)! - teamTotals.get(a)!).slice(0, topN)
  const countryData = ['Gold', 'Silver', 'Bronze'].map(medal => ({
    type: 'bar' as const, name: medal,
    x: topTeams, y: topTeams.map(t => (countries ?? []).find(r => r.Team === t && r.Medal === medal)?.count ?? 0),
    marker: { color: MEDAL_COLORS[medal], line: { width: 0 } },
  }))

  const sportTotals = new Map<string, number>()
  for (const r of sports ?? []) sportTotals.set(r.Sport, (sportTotals.get(r.Sport) ?? 0) + r.count)
  const sportNames = [...sportTotals.keys()].sort((a, b) => sportTotals.get(b)! - sportTotals.get(a)!).slice(0, 20)
  const sportsData = ['Hommes', 'Femmes'].map((sex, i) => ({
    type: 'bar' as const, name: sex,
    x: sportNames, y: sportNames.map(s => (sports ?? []).find(r => r.Sport === s && r.Sex === sex)?.count ?? 0),
    marker: { color: i === 0 ? '#374151' : '#c9a227', line: { width: 0 } },
  }))

  const goldData = [{
    type: 'scatter' as const, mode: 'lines' as const, name: "Médailles d'or",
    x: trends?.gold_by_year?.map((r: any) => r.Year) ?? [],
    y: trends?.gold_by_year?.map((r: any) => r.gold) ?? [],
    line: { color: '#c9a227', width: 2 },
    fill: 'tozeroy' as const, fillcolor: 'rgba(201,162,39,0.07)',
  }]

  const heatTeams = [...new Set((heatmap ?? []).map(r => r.Team))]
  const heatYears = [...new Set((heatmap ?? []).map(r => r.Year))].sort()
  const heatMatrix = heatTeams.map(team => heatYears.map(year => (heatmap ?? []).find(r => r.Team === team && r.Year === year)?.gold ?? 0))
  const heatData = [{
    type: 'heatmap' as const, x: heatYears, y: heatTeams, z: heatMatrix,
    colorscale: [['0', '#f5f3ee'], ['1', '#c9a227']], showscale: false,
  }]

  return (
    <div>
      <PageHeader title="Exploration des données" sub="Analysez les performances olympiques par pays, sport et période." badge="Données · 1896–2024" />

      {/* Filters */}
      <div className="card" style={{ padding: '16px 20px', marginBottom: '28px', display: 'flex', gap: '24px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
        <div>
          <div className="label" style={{ marginBottom: '6px' }}>Période</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <input type="number" min={meta?.year_min ?? 1896} max={yearMax} value={yearMin}
              onChange={e => setYearMin(+e.target.value)} style={{ ...select, width: '72px' }} />
            <span style={{ color: 'var(--text-3)', fontSize: '0.75rem' }}>—</span>
            <input type="number" min={yearMin} max={meta?.year_max ?? 2024} value={yearMax}
              onChange={e => setYearMax(+e.target.value)} style={{ ...select, width: '72px' }} />
          </div>
        </div>
        <div>
          <div className="label" style={{ marginBottom: '6px' }}>Genre</div>
          <select value={gender} onChange={e => setGender(e.target.value)} style={select}>
            <option value="all">Tous</option>
            <option value="m">Hommes</option>
            <option value="f">Femmes</option>
          </select>
        </div>
        <div>
          <div className="label" style={{ marginBottom: '6px' }}>Top {topN} pays</div>
          <input type="range" min={5} max={30} value={topN} onChange={e => setTopN(+e.target.value)}
            style={{ accentColor: 'var(--gold)', width: '100px' }} />
        </div>
      </div>

      <Tabs tabs={TABS} active={tab} onChange={setTab} />

      {tab === 'pays' && (
        <>
          <SectionHeader title="Classement des pays" sub={`Top ${topN} nations médaillées — ${yearMin}–${yearMax}`} />
          {lc ? <Spinner /> : (
            <div style={{ display: 'grid', gridTemplateColumns: '3fr 2fr', gap: '16px' }}>
              <PlotlyChart data={countryData} layout={{ barmode: 'stack', xaxis: { tickangle: -30 }, showlegend: true, legend: { orientation: 'h', y: -0.18 } }} height={400} />
              <PlotlyChart data={[{ type: 'choropleth', locations: choropleth?.map(r => r.NOC) ?? [], z: choropleth?.map(r => r.total) ?? [], text: choropleth?.map(r => r.Team) ?? [], colorscale: [['0', '#f5f3ee'], ['1', '#c9a227']], showscale: false }]} layout={{ geo: { showframe: false, bgcolor: 'transparent', showland: true, landcolor: '#f5f3ee' }, margin: { t: 8, r: 0, b: 8, l: 0 } }} height={400} />
            </div>
          )}
        </>
      )}

      {tab === 'sports' && (
        <>
          <SectionHeader title="Top disciplines" sub="Répartition des médailles par sport et genre" />
          <PlotlyChart data={sportsData} layout={{ barmode: 'group', xaxis: { tickangle: -30 }, showlegend: true, legend: { orientation: 'h', y: -0.18 } }} height={440} />
        </>
      )}

      {tab === 'tendances' && (
        <>
          <SectionHeader title="Évolution des médailles d'or" />
          <PlotlyChart data={goldData} height={400} />
          <Insight>La progression reflète l'augmentation du nombre d'épreuves au programme olympique à chaque édition.</Insight>
        </>
      )}

      {tab === 'heatmap' && (
        <>
          <SectionHeader title="Heatmap — Médailles d'or par nation et édition" />
          <PlotlyChart data={heatData} layout={{ margin: { t: 16, r: 16, b: 40, l: 110 } }} height={480} />
        </>
      )}

      <div style={{ borderTop: '1px solid var(--border-soft)', paddingTop: '20px', marginTop: '40px', textAlign: 'center', color: 'var(--text-3)', fontSize: '0.72rem' }}>
        YPerf · Ynov · 2026
      </div>
    </div>
  )
}
