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
  const { data: kpis, isLoading: k } = useQuery({ queryKey: ['home-kpis'], queryFn: () => fetchJSON<Kpis>('/home/kpis') })
  const { data: mby } = useQuery({ queryKey: ['medals-by-year'], queryFn: () => fetchJSON<any[]>('/home/medals-by-year') })
  const { data: gender } = useQuery({ queryKey: ['gender-participation'], queryFn: () => fetchJSON<any[]>('/home/gender-participation') })
  const { data: byCountry } = useQuery({ queryKey: ['medals-by-country'], queryFn: () => fetchJSON<any[]>('/home/medals-by-country') })
  const { data: part } = useQuery({ queryKey: ['participation'], queryFn: () => fetchJSON<any[]>('/home/participation') })
  const { data: bySport } = useQuery({ queryKey: ['medals-by-sport'], queryFn: () => fetchJSON<any[]>('/home/medals-by-sport') })

  if (k) return <Spinner />

  // Medals by year stacked bar
  const medalTypes = ['Gold', 'Silver', 'Bronze']
  const mbyData = medalTypes.map(medal => ({
    type: 'bar' as const,
    name: medal,
    x: mby?.filter(r => r.Medal === medal).map(r => r.Year) ?? [],
    y: mby?.filter(r => r.Medal === medal).map(r => r.Count) ?? [],
    marker: { color: MEDAL_COLORS[medal] },
  }))

  // Gender area
  const sexes = ['Hommes', 'Femmes']
  const genderData = sexes.map((s, i) => ({
    type: 'scatter' as const,
    fill: 'tozeroy' as const,
    mode: 'lines' as const,
    name: s,
    x: gender?.filter(r => r.sex === s).map(r => r.year) ?? [],
    y: gender?.filter(r => r.sex === s).map(r => r.count) ?? [],
    line: { color: i === 0 ? '#3b82f6' : '#ec4899', width: 2 },
    fillcolor: i === 0 ? 'rgba(59,130,246,0.15)' : 'rgba(236,72,153,0.15)',
  }))

  // Choropleth
  const choroplethData = [{
    type: 'choropleth' as const,
    locations: byCountry?.map(r => r.NOC) ?? [],
    z: byCountry?.map(r => r.total) ?? [],
    text: byCountry?.map(r => r.Team) ?? [],
    colorscale: 'YlOrRd',
    showscale: true,
    colorbar: { title: { text: 'Médailles' }, thickness: 12 },
  }]

  // Top 10 bar
  const top10 = [...(byCountry ?? [])].sort((a, b) => b.total - a.total).slice(0, 10)
  const top10Data = [{
    type: 'bar' as const,
    orientation: 'h' as const,
    x: top10.map(r => r.total),
    y: top10.map(r => r.Team),
    marker: { color: top10.map(r => r.total), colorscale: 'Blues', showscale: false },
  }]

  // Participation lines
  const partKeys = ['Athlètes', 'Pays', 'Sports']
  const partColors = ['#3b82f6', '#10b981', '#ef4444']
  const partData = partKeys.map((k, i) => ({
    type: 'scatter' as const, mode: 'lines+markers' as const,
    name: k,
    x: part?.map(r => r.Year) ?? [],
    y: part?.map((r: any) => r[k]) ?? [],
    line: { color: partColors[i], width: 2.5 },
    marker: { size: 4 },
  }))

  // Treemap sports
  const treemapData = [{
    type: 'treemap' as const,
    labels: bySport?.map(r => r.Sport) ?? [],
    parents: bySport?.map(() => '') ?? [],
    values: bySport?.map(r => r.medals) ?? [],
    marker: { colorscale: 'Blues' },
  }]

  return (
    <div>
      {/* Hero */}
      <div className="bg-gradient-to-r from-[#0a0f2e] to-[#1a2560] rounded-3xl p-8 mb-8 relative overflow-hidden">
        <div className="text-4xl mb-2">⭕🔵🟡⚫🟢🔴</div>
        <h1 className="text-3xl font-black text-white mb-2" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
          YPerf — Performances Olympiques
        </h1>
        <p className="text-white/60 text-sm max-w-xl">
          Explorez 60 ans d'histoire olympique et découvrez les prédictions pour Los Angeles 2028 🇺🇸
        </p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-5 gap-4 mb-8">
        <KpiCard icon="📅" value={kpis!.editions} label="Éditions des JO" color="blue" />
        <KpiCard icon="🏃" value={kpis!.athletes.toLocaleString()} label="Athlètes uniques" color="green" />
        <KpiCard icon="🌍" value={kpis!.countries} label="Pays représentés" color="red" />
        <KpiCard icon="🏋️" value={kpis!.sports} label="Sports différents" color="slate" />
        <KpiCard icon="🥇" value={kpis!.gold_medals.toLocaleString()} label="Médailles d'or" color="gold" />
      </div>

      {/* Row 1 */}
      <SectionHeader title="📊 Vue d'ensemble historique" />
      <div className="grid grid-cols-5 gap-4 mb-6">
        <div className="col-span-3">
          <PlotlyChart
            data={mbyData}
            layout={{ barmode: 'stack', title: { text: 'Médailles par édition' }, legend: { orientation: 'h' } }}
            height={360}
          />
        </div>
        <div className="col-span-2">
          <PlotlyChart
            data={genderData}
            layout={{ title: { text: 'Parité hommes / femmes' }, legend: { orientation: 'h' } }}
            height={360}
          />
        </div>
      </div>

      <Insight>
        Les JO de Tokyo 2020 ont enregistré le plus grand nombre d'athlètes. La parité hommes/femmes a spectaculairement progressé : les femmes représentent aujourd'hui près de <strong>50 %</strong> des participations.
      </Insight>

      {/* Row 2 */}
      <SectionHeader title="🌍 Rayonnement mondial" />
      <div className="grid grid-cols-5 gap-4 mb-6">
        <div className="col-span-3">
          <PlotlyChart
            data={choroplethData}
            layout={{
              title: { text: 'Total des médailles par pays' },
              geo: { showframe: false, showcoastlines: true, coastlinecolor: '#ddd', bgcolor: 'rgba(0,0,0,0)' },
              margin: { t: 44, r: 0, b: 0, l: 0 },
            }}
            height={360}
          />
        </div>
        <div className="col-span-2">
          <PlotlyChart
            data={top10Data}
            layout={{
              title: { text: 'Top 10 pays (1896–2024)' },
              yaxis: { categoryorder: 'total ascending' },
            }}
            height={360}
          />
        </div>
      </div>

      {/* Row 3 */}
      <SectionHeader title="📈 Tendances & Sports" />
      <div className="grid grid-cols-2 gap-4 mb-6">
        <PlotlyChart
          data={partData}
          layout={{ title: { text: 'Évolution de la participation' }, legend: { orientation: 'h', y: 1.1 } }}
          height={340}
        />
        <PlotlyChart
          data={treemapData}
          layout={{ title: { text: 'Médailles par sport' }, margin: { t: 44, r: 0, b: 0, l: 0 } }}
          height={340}
        />
      </div>

      <Insight>
        Le pays le plus lauréat en médailles d'or toutes éditions confondues est <strong>{kpis?.top_country}</strong>. L'édition {kpis?.last_year} a vu la participation de <strong>{kpis?.last_year_countries}</strong> pays.
      </Insight>

      <div className="text-center text-slate-400 text-xs mt-10 pb-4">
        YPerf · Projet fil rouge Bachelor 3 · Ynov Informatique · 2026
      </div>
    </div>
  )
}
