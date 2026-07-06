import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchJSON } from '../lib/api'
import { MEDAL_COLORS } from '../lib/plotly'
import SectionHeader from '../components/SectionHeader'
import PlotlyChart from '../components/PlotlyChart'
import Spinner from '../components/Spinner'
import Tabs from '../components/Tabs'
import PageHeader from '../components/PageHeader'

type Tab = 'classement' | 'comparaison' | 'fiche'

const TABS = [
  { id: 'classement' as Tab,  label: 'Classement' },
  { id: 'comparaison' as Tab, label: 'Genre' },
  { id: 'fiche' as Tab,       label: 'Fiche athlète' },
]

const select: React.CSSProperties = {
  fontSize: '0.8rem', fontFamily: 'inherit',
  border: '1px solid var(--border)', borderRadius: 'var(--r-sm)',
  padding: '6px 10px', background: 'var(--surface)', color: 'var(--text-1)',
  cursor: 'pointer', outline: 'none',
}

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
  const { data: searchResults, isLoading: isSearching } = useQuery({ queryKey: ['athlete-search', search], queryFn: () => fetchJSON<any[]>('/athletes/search', { q: search }), enabled: search.trim().length >= 2 })

  const isSearchActive = search.trim().length >= 2
  const filtered = isSearchActive ? (searchResults ?? []) : (top ?? [])

  const topBarData = [{
    type: 'bar' as const, orientation: 'h' as const,
    x: filtered.map(r => r.total), y: filtered.map(r => r.Name),
    marker: { color: '#c9a227', line: { width: 0 } },
    text: filtered.map(r => r.total), textposition: 'outside' as const,
  }]

  const detailBarData = (detail?.by_medal ?? []).map((row: any) => ({
    type: 'bar' as const, name: row.Medal,
    x: [row.Name], y: [row.count],
    marker: { color: MEDAL_COLORS[row.Medal] ?? '#888', line: { width: 0 } },
  }))

  const genderData = ['Gold', 'Silver', 'Bronze'].map(medal => ({
    type: 'bar' as const, name: medal,
    x: ['Hommes', 'Femmes'],
    y: ['M', 'F'].map(s => (genderMedals ?? []).find((r: any) => r.Sex === (s === 'M' ? 'Hommes' : 'Femmes') && r.Medal === medal)?.count ?? 0),
    marker: { color: MEDAL_COLORS[medal], line: { width: 0 } },
  }))

  const top10 = filtered.slice(0, 10)

  return (
    <div>
      <PageHeader title="Tableau de bord athlètes" sub="Palmarès, comparaisons et profils individuels." badge="Athlètes · 1896–2024" />

      {/* Filters */}
      <div className="card" style={{ padding: '16px 20px', marginBottom: '28px', display: 'flex', gap: '16px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
        <div>
          <div className="label" style={{ marginBottom: '6px' }}>Sport</div>
          <select value={sport} onChange={e => setSport(e.target.value)} style={select}>
            <option value="all">Tous</option>
            {filtersMeta?.sports.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
        <div>
          <div className="label" style={{ marginBottom: '6px' }}>Pays</div>
          <select value={country} onChange={e => setCountry(e.target.value)} style={select}>
            <option value="all">Tous</option>
            {filtersMeta?.countries.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div>
          <div className="label" style={{ marginBottom: '6px' }}>Période</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <input type="number" min={1896} max={yearMax} value={yearMin} onChange={e => setYearMin(+e.target.value)} style={{ ...select, width: '68px' }} />
            <span style={{ color: 'var(--text-3)', fontSize: '0.75rem' }}>—</span>
            <input type="number" min={yearMin} max={2024} value={yearMax} onChange={e => setYearMax(+e.target.value)} style={{ ...select, width: '68px' }} />
          </div>
        </div>
        <div style={{ flex: 1 }}>
          <div className="label" style={{ marginBottom: '6px' }}>Rechercher</div>
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Phelps, Bolt, Biles…"
            style={{ ...select, width: '100%', minWidth: '180px' }} />
        </div>
      </div>

      <Tabs tabs={TABS} active={tab} onChange={setTab} />

      {tab === 'classement' && (
        <>
          <SectionHeader title="Palmarès" sub={isSearchActive ? `${filtered.length} résultat(s) pour « ${search} »` : `Top ${filtered.length} athlètes — ${yearMin}–${yearMax}`} />
          {(isSearchActive ? isSearching : isLoading) ? <Spinner /> : (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <PlotlyChart data={topBarData} layout={{ yaxis: { categoryorder: 'total ascending' }, margin: { t: 16, r: 48, b: 28, l: 120 } }} height={560} />
              <PlotlyChart data={genderData} layout={{ barmode: 'group', margin: { t: 16, r: 16, b: 28, l: 40 }, title: { text: 'Par genre' } }} height={560} />
            </div>
          )}
        </>
      )}

      {tab === 'comparaison' && (
        <>
          <SectionHeader title="Médailles par genre" />
          <PlotlyChart data={genderData} layout={{ barmode: 'group', showlegend: true, legend: { orientation: 'h', y: -0.12 } }} height={380} />
        </>
      )}

      {tab === 'fiche' && (
        <>
          <SectionHeader title="Profil athlète" />
          <div style={{ marginBottom: '16px' }}>
            <div className="label" style={{ marginBottom: '6px' }}>Athlète</div>
            <select value={selectedAthlete ?? ''} onChange={e => setSelectedAthlete(e.target.value)} style={{ ...select, minWidth: '240px' }}>
              <option value="">Sélectionner…</option>
              {top10.map((a: any) => <option key={a.Name} value={a.Name}>{a.Name} — {a.Team}</option>)}
            </select>
          </div>
          {selectedAthlete && detail && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <PlotlyChart data={detailBarData} layout={{ barmode: 'group', title: { text: `${selectedAthlete}` } }} height={320} />
              <PlotlyChart data={[{ type: 'scatter', mode: 'lines+markers', x: detail.by_year.map((r: any) => r.Year), y: detail.by_year.map((r: any) => r.medals), line: { color: '#c9a227', width: 2 }, marker: { size: 5 }, fill: 'tozeroy', fillcolor: 'rgba(201,162,39,0.08)' }]} layout={{ title: { text: 'Médailles par édition' } }} height={320} />
            </div>
          )}
        </>
      )}

      <div style={{ borderTop: '1px solid var(--border-soft)', paddingTop: '20px', marginTop: '40px', textAlign: 'center', color: 'var(--text-3)', fontSize: '0.72rem' }}>YPerf · Ynov · 2026</div>
    </div>
  )
}
