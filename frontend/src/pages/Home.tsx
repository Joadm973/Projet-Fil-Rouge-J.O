import { useQuery } from '@tanstack/react-query'
import { fetchJSON } from '../lib/api'
import { MEDAL_COLORS } from '../lib/plotly'
import KpiCard from '../components/KpiCard'
import SectionHeader from '../components/SectionHeader'
import PlotlyChart from '../components/PlotlyChart'
import { Insight } from '../components/InsightBox'
import Spinner from '../components/Spinner'

interface Kpis {
  editions: number; athletes: number; countries: number
  sports: number; gold_medals: number; top_country: string
  last_year: number; last_year_countries: number
}

export default function Home() {
  const { data: kpis, isLoading } = useQuery({ queryKey: ['home-kpis'], queryFn: () => fetchJSON<Kpis>('/home/kpis') })
  const { data: mby }       = useQuery({ queryKey: ['medals-by-year'],       queryFn: () => fetchJSON<any[]>('/home/medals-by-year') })
  const { data: gender }    = useQuery({ queryKey: ['gender-participation'],  queryFn: () => fetchJSON<any[]>('/home/gender-participation') })
  const { data: byCountry } = useQuery({ queryKey: ['medals-by-country'],     queryFn: () => fetchJSON<any[]>('/home/medals-by-country') })
  const { data: part }      = useQuery({ queryKey: ['participation'],          queryFn: () => fetchJSON<any[]>('/home/participation') })
  const { data: bySport }   = useQuery({ queryKey: ['medals-by-sport'],        queryFn: () => fetchJSON<any[]>('/home/medals-by-sport') })

  if (isLoading) return <Spinner />
  if (!kpis) return null

  // ── Chart data ─────────────────────────────────────────────────────
  const medalTypes = ['Gold', 'Silver', 'Bronze']
  const mbyData = medalTypes.map(medal => ({
    type: 'bar' as const, name: medal,
    x: mby?.filter(r => r.Medal === medal).map(r => r.Year) ?? [],
    y: mby?.filter(r => r.Medal === medal).map(r => r.Count) ?? [],
    marker: { color: MEDAL_COLORS[medal], line: { width: 0 } },
  }))

  const genderData = ['Hommes', 'Femmes'].map((s, i) => ({
    type: 'scatter' as const, fill: 'tozeroy' as const, mode: 'lines' as const, name: s,
    x: gender?.filter(r => r.sex === s).map(r => r.year) ?? [],
    y: gender?.filter(r => r.sex === s).map(r => r.count) ?? [],
    line: { color: i === 0 ? '#374151' : '#c9a227', width: 1.75 },
    fillcolor: i === 0 ? 'rgba(55,65,81,0.08)' : 'rgba(201,162,39,0.08)',
  }))

  const top10 = [...(byCountry ?? [])].sort((a, b) => b.total - a.total).slice(0, 10)
  const top10Data = [{
    type: 'bar' as const, orientation: 'h' as const,
    x: top10.map(r => r.total), y: top10.map(r => r.Team),
    marker: { color: '#c9a227' },
    text: top10.map(r => r.total), textposition: 'outside' as const,
  }]

  const choroplethData = [{
    type: 'choropleth' as const,
    locations: byCountry?.map(r => r.NOC) ?? [],
    z: byCountry?.map(r => r.total) ?? [],
    text: byCountry?.map(r => r.Team) ?? [],
    colorscale: [['0', '#f5f3ee'], ['0.5', '#e8c96b'], ['1', '#92641a']],
    showscale: false,
  }]

  const partColors = ['#c9a227', '#374151', '#3d7a9e']
  const partData = ['Athlètes', 'Pays', 'Sports'].map((k, i) => ({
    type: 'scatter' as const, mode: 'lines' as const, name: k,
    x: part?.map(r => r.Year) ?? [],
    y: part?.map((r: any) => r[k]) ?? [],
    line: { color: partColors[i], width: 1.75 },
  }))

  const treemapData = [{
    type: 'treemap' as const,
    labels: bySport?.map(r => r.Sport) ?? [],
    parents: bySport?.map(() => '') ?? [],
    values: bySport?.map(r => r.medals) ?? [],
    marker: { colorscale: [['0', '#f5f3ee'], ['1', '#c9a227']] },
    textfont: { size: 11 },
  }]

  return (
    <div>
      {/* ── Hero ─────────────────────────────────────────────────────── */}
      <div style={{ marginBottom: '48px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--gold)', display: 'inline-block' }} />
          <span style={{ fontSize: '0.72rem', fontWeight: 600, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--text-3)' }}>
            Projet fil rouge · Ynov Bachelor 3
          </span>
        </div>

        <h1 style={{ maxWidth: '560px', marginBottom: '16px' }}>
          60 ans de JO,<br />
          <span style={{ color: 'var(--gold)' }}>une prédiction</span><br />
          pour 2028.
        </h1>

        <p style={{ maxWidth: '440px', fontSize: '0.95rem', lineHeight: '1.6', color: 'var(--text-2)' }}>
          Analyse complète des performances olympiques 1896–2024.
          Prédictions ML pour Los Angeles, nouvelles générations, données World Bank.
        </p>

        {/* Méta-stats en ligne */}
        <div style={{ display: 'flex', gap: '32px', marginTop: '28px', paddingTop: '28px', borderTop: '1px solid var(--border-soft)' }}>
          {[
            { v: kpis?.editions, l: 'éditions' },
            { v: kpis?.athletes?.toLocaleString(), l: 'athlètes' },
            { v: kpis?.countries, l: 'pays' },
            { v: kpis?.sports, l: 'sports' },
          ].map(({ v, l }) => (
            <div key={l}>
              <div style={{ fontSize: '1.35rem', fontWeight: 700, letterSpacing: '-0.03em', color: 'var(--text-1)' }}>{v ?? '—'}</div>
              <div className="label">{l}</div>
            </div>
          ))}
        </div>
      </div>

      {/* ── KPIs row ─────────────────────────────────────────────────── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '48px' }}>
        <KpiCard value={kpis!.gold_medals.toLocaleString()} label="Médailles d'or distribuées" />
        <KpiCard value={kpis!.top_country} label="Nation la plus titrée" />
        <KpiCard value={kpis!.last_year} label="Dernière édition" />
        <KpiCard value={kpis!.last_year_countries} label="Pays représentés en 2024" />
      </div>

      {/* ── Section 1 : Historique ───────────────────────────────────── */}
      <SectionHeader title="Historique des médailles" sub="Distribution par édition et évolution de la parité" />

      <div style={{ display: 'grid', gridTemplateColumns: '3fr 2fr', gap: '16px', marginBottom: '16px' }}>
        <PlotlyChart
          data={mbyData}
          layout={{ barmode: 'stack', showlegend: true, legend: { orientation: 'h', y: -0.12, x: 0 } }}
          height={340}
        />
        <PlotlyChart
          data={genderData}
          layout={{ showlegend: true, legend: { orientation: 'h', y: -0.12, x: 0 } }}
          height={340}
        />
      </div>

      <Insight>
        Les femmes représentent aujourd'hui près de <strong>50 %</strong> des participations olympiques — une progression spectaculaire depuis 1900 où elles n'étaient que 23.
      </Insight>

      {/* ── Section 2 : Rayonnement ─────────────────────────────────── */}
      <SectionHeader title="Rayonnement mondial" sub="Répartition géographique de toutes les médailles" />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gap: '16px', marginBottom: '16px' }}>
        <PlotlyChart
          data={choroplethData}
          layout={{
            geo: { showframe: false, showcoastlines: true, coastlinecolor: '#e5e1d8', bgcolor: 'transparent', showland: true, landcolor: '#f5f3ee', showocean: true, oceancolor: '#edeae3' },
            margin: { t: 8, r: 0, b: 8, l: 0 },
          }}
          height={340}
        />
        <PlotlyChart
          data={top10Data}
          layout={{ yaxis: { categoryorder: 'total ascending' }, margin: { t: 16, r: 52, b: 28, l: 90 } }}
          height={340}
        />
      </div>

      {/* ── Section 3 : Tendances ───────────────────────────────────── */}
      <SectionHeader title="Tendances & disciplines" sub="Croissance de la participation et poids des sports" />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '32px' }}>
        <PlotlyChart
          data={partData}
          layout={{ showlegend: true, legend: { orientation: 'h', y: -0.14, x: 0 } }}
          height={300}
        />
        <PlotlyChart
          data={treemapData}
          layout={{ margin: { t: 8, r: 0, b: 8, l: 0 } }}
          height={300}
        />
      </div>

      <div style={{ borderTop: '1px solid var(--border-soft)', paddingTop: '20px', textAlign: 'center', color: 'var(--text-3)', fontSize: '0.72rem' }}>
        YPerf · Projet fil rouge Bachelor 3 · Ynov Informatique · 2026
      </div>
    </div>
  )
}
