import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchJSON } from '../lib/api'
import { MEDAL_COLORS } from '../lib/plotly'
import SectionHeader from '../components/SectionHeader'
import PlotlyChart from '../components/PlotlyChart'
import Spinner from '../components/Spinner'

type Tab = 'classement' | 'comparaison' | 'fiche'

export default function Athletes() {
  const [tab, setTab] = useState<Tab>('classement')
  const [sport, setSport] = useState('all')
  const [country, setCountry] = useState('all')
  const [medals] = useState('Gold,Silver,Bronze')
  const [yearMin, setYearMin] = useState(1896)
  const [yearMax, setYearMax] = useState(2024)
  const [search, setSearch] = useState('')
  const [selectedAthlete, setSelectedAthlete] = useState<string | null>(null)

  const { data: filtersMeta } = useQuery({ queryKey: ['athletes-meta'], queryFn: () => fetchJSON<{ sports: string[]; countries: string[] }>('/athletes/filters-meta') })

  const params = { sport, country, medals, year_min: yearMin, year_max: yearMax, top_n: 30 }
  const { data: top, isLoading } = useQuery({ queryKey: ['top-athletes', params], queryFn: () => fetchJSON<any[]>('/athletes/top', params) })
  const { data: genderMedals } = useQuery({ queryKey: ['gender-medals', { year_min: yearMin, year_max: yearMax, medals }], queryFn: () => fetchJSON<any[]>('/athletes/gender-medals', { year_min: yearMin, year_max: yearMax, medals }) })
  const { data: detail } = useQuery({ queryKey: ['athlete-detail', selectedAthlete], queryFn: () => fetchJSON<any>('/athletes/detail', { name: selectedAthlete, year_min: yearMin, year_max: yearMax, medals }), enabled: !!selectedAthlete })

  const filtered = (top ?? []).filter(a => !search || a.Name?.toLowerCase().includes(search.toLowerCase()))
  const top10 = filtered.slice(0, 10)

  const topBarData = [{
    type: 'bar' as const, orientation: 'h' as const,
    x: filtered.map(r => r.total), y: filtered.map(r => r.Name),
    marker: { color: '#3b82f6' }, text: filtered.map(r => r.total), textposition: 'outside' as const,
  }]

  const detailBarData = (detail?.by_medal ?? []).map((row: any) => ({
    type: 'bar' as const, name: row.Medal,
    x: [row.Name], y: [row.count],
    marker: { color: MEDAL_COLORS[row.Medal] ?? '#888' },
  }))

  const genderData = ['Gold', 'Silver', 'Bronze'].map(medal => ({
    type: 'bar' as const, name: medal,
    x: ['Hommes', 'Femmes'],
    y: ['M', 'F'].map(s => (genderMedals ?? []).find((r: any) => r.Sex === (s === 'M' ? 'Hommes' : 'Femmes') && r.Medal === medal)?.count ?? 0),
    marker: { color: MEDAL_COLORS[medal] },
  }))

  const TABS = [
    { id: 'classement' as Tab, label: '🥇 Classement' },
    { id: 'comparaison' as Tab, label: '📊 Comparaison' },
    { id: 'fiche' as Tab, label: '🔎 Fiche athlète' },
  ]

  return (
    <div>
      <h1 className="text-2xl font-black text-slate-800 mb-1" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>🏃 Tableau de bord Athlètes</h1>
      <p className="text-slate-500 text-sm mb-6">Recherchez, comparez et explorez les profils des athlètes olympiques.</p>

      {/* Filters */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5 mb-6 flex gap-4 flex-wrap items-end">
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-slate-500">Sport</label>
          <select value={sport} onChange={e => setSport(e.target.value)} className="text-sm border border-slate-200 rounded-lg px-3 py-1.5">
            <option value="all">Tous</option>
            {filtersMeta?.sports.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-slate-500">Pays</label>
          <select value={country} onChange={e => setCountry(e.target.value)} className="text-sm border border-slate-200 rounded-lg px-3 py-1.5">
            <option value="all">Tous</option>
            {filtersMeta?.countries.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-slate-500">Période : {yearMin}–{yearMax}</label>
          <div className="flex gap-2">
            <input type="range" min={1896} max={yearMax} value={yearMin} onChange={e => setYearMin(+e.target.value)} className="accent-blue-500" />
            <input type="range" min={yearMin} max={2024} value={yearMax} onChange={e => setYearMax(+e.target.value)} className="accent-blue-500" />
          </div>
        </div>
        <div className="flex flex-col gap-1 flex-1">
          <label className="text-xs font-medium text-slate-500">Rechercher</label>
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Ex: Phelps, Bolt…" className="text-sm border border-slate-200 rounded-lg px-3 py-1.5" />
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

      {tab === 'classement' && (
        <div>
          <SectionHeader title="🥇 Top athlètes les plus médaillés" />
          {isLoading ? <Spinner /> : (
            <div className="grid grid-cols-2 gap-4">
              <PlotlyChart
                data={topBarData}
                layout={{ yaxis: { categoryorder: 'total ascending' }, title: { text: `Top athlètes — ${yearMin}–${yearMax}` } }}
                height={600}
              />
              <PlotlyChart
                data={detailBarData.length ? detailBarData : genderData}
                layout={{ barmode: 'group', title: { text: detailBarData.length ? `${selectedAthlete} — médailles` : 'Médailles par genre' } }}
                height={600}
              />
            </div>
          )}
        </div>
      )}

      {tab === 'comparaison' && (
        <div>
          <SectionHeader title="⚤ Médailles par genre" />
          <PlotlyChart data={genderData} layout={{ barmode: 'group', title: { text: 'Médailles par genre' } }} height={400} />
        </div>
      )}

      {tab === 'fiche' && (
        <div>
          <SectionHeader title="🔎 Fiche athlète" />
          <div className="mb-4">
            <select value={selectedAthlete ?? ''} onChange={e => setSelectedAthlete(e.target.value)} className="text-sm border border-slate-200 rounded-lg px-3 py-1.5 w-72">
              <option value="">Sélectionner un athlète…</option>
              {top10.map((a: any) => <option key={a.Name} value={a.Name}>{a.Name} ({a.Team})</option>)}
            </select>
          </div>
          {selectedAthlete && detail && (
            <div className="grid grid-cols-2 gap-4">
              <PlotlyChart
                data={detailBarData}
                layout={{ barmode: 'group', title: { text: `${selectedAthlete} — décomposition` } }}
                height={340}
              />
              <PlotlyChart
                data={[{ type: 'scatter', mode: 'lines+markers', x: detail.by_year.map((r: any) => r.Year), y: detail.by_year.map((r: any) => r.medals), line: { color: '#f59e0b', width: 2.5 }, marker: { size: 6 } }]}
                layout={{ title: { text: `${selectedAthlete} — médailles par édition` } }}
                height={340}
              />
            </div>
          )}
        </div>
      )}

      <div className="text-center text-slate-400 text-xs mt-10 pb-4">YPerf · Ynov · 2026</div>
    </div>
  )
}
