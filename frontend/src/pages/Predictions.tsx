import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchJSON } from '../lib/api'
import type { Data } from 'plotly.js'
import SectionHeader from '../components/SectionHeader'
import PlotlyChart from '../components/PlotlyChart'
import Spinner from '../components/Spinner'
import { Insight, Warning } from '../components/InsightBox'

type Tab = 'classement' | 'historique' | 'cotes' | 'recommandations' | 'timeline'

const MODELS = [
  { id: 'linear', label: '📐 Régression Linéaire' },
  { id: 'ridge', label: '📉 Ridge (régularisé)' },
  { id: 'gradient_boosting', label: '🌳 Gradient Boosting' },
  { id: 'polynomial', label: '🔁 Polynomiale (deg 2)' },
]

export default function Predictions() {
  const [tab, setTab] = useState<Tab>('classement')
  const [model, setModel] = useState('linear')
  const [topN, setTopN] = useState(20)
  const [run, setRun] = useState(false)
  const [selectedCountry, setSelectedCountry] = useState('')

  const { data: predictions, isLoading: lp, refetch } = useQuery({
    queryKey: ['predictions', model, topN],
    queryFn: () => fetchJSON<any[]>('/predictions/predict', { model, top_n: topN }),
    enabled: run,
  })

  const { data: trend } = useQuery({
    queryKey: ['trend', selectedCountry],
    queryFn: () => fetchJSON<any>('/predictions/country-trend', { team: selectedCountry }),
    enabled: !!selectedCountry,
  })

  const { data: ratings } = useQuery({ queryKey: ['ratings'], queryFn: () => fetchJSON<any[]>('/predictions/athlete-ratings') })
  const { data: recs } = useQuery({ queryKey: ['recs'], queryFn: () => fetchJSON<any>('/predictions/recommendations') })
  const { data: diversity } = useQuery({ queryKey: ['diversity'], queryFn: () => fetchJSON<any>('/predictions/timeline-diversity') })

  const handleRun = () => { setRun(true); refetch() }

  const predData = [{
    type: 'bar' as const, orientation: 'h' as const,
    x: (predictions ?? []).map(r => r.predicted),
    y: (predictions ?? []).map(r => r.country),
    marker: { color: (predictions ?? []).map(r => r.predicted), colorscale: 'RdYlGn', showscale: false },
    text: (predictions ?? []).map(r => r.predicted), textposition: 'outside' as const,
  }]

  // Trend chart
  const trendData: Data[] = []
  if (trend) {
    trendData.push({
      type: 'scatter', mode: 'lines+markers',
      name: 'Historique',
      x: trend.history.map((r: any) => r.Year),
      y: trend.history.map((r: any) => r.total ?? r.medals ?? 0),
      line: { color: '#3b82f6', width: 2 },
    })
    if (trend.pred2028) {
      const lastYear = trend.history[trend.history.length - 1]?.Year
      const lastVal = trend.history[trend.history.length - 1]?.total ?? 0
      trendData.push({
        type: 'scatter', mode: 'lines+markers',
        name: 'Projection 2028',
        x: [lastYear, 2028], y: [lastVal, trend.pred2028],
        line: { color: '#f59e0b', width: 2, dash: 'dash' },
        marker: { size: 8, color: '#f59e0b' },
      })
    }
  }

  const ratingsData = [{
    type: 'bar' as const, orientation: 'h' as const,
    x: (ratings ?? []).slice(0, 20).map(r => r.cote),
    y: (ratings ?? []).slice(0, 20).map(r => r.Name),
    marker: { color: '#f59e0b' },
    text: (ratings ?? []).slice(0, 20).map(r => r.cote?.toFixed(1)),
    textposition: 'outside' as const,
  }]

  const divData: Data[] = diversity ? [
    {
      type: 'bar', name: 'Pays médaillés',
      x: diversity.countries_per_year.map((r: any) => r.Year),
      y: diversity.countries_per_year.map((r: any) => r['Pays médaillés']),
      marker: { color: 'rgba(59,130,246,0.5)' },
      yaxis: 'y',
    },
    {
      type: 'scatter', mode: 'lines', name: 'Disciplines',
      x: diversity.sports_per_year.map((r: any) => r.Year),
      y: diversity.sports_per_year.map((r: any) => r.Disciplines),
      line: { color: '#ef4444', width: 2, dash: 'dash' },
      yaxis: 'y2',
    },
  ] : []

  const TABS = [
    { id: 'classement' as Tab, label: '🏆 Classement 2028' },
    { id: 'historique' as Tab, label: '📈 Historique pays' },
    { id: 'cotes' as Tab, label: '🎯 Côtes athlètes' },
    { id: 'recommandations' as Tab, label: '💡 Recommandations' },
    { id: 'timeline' as Tab, label: '⏱️ Timeline' },
  ]

  return (
    <div>
      <h1 className="text-2xl font-black text-slate-800 mb-1" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>🔮 Prédictions JO 2028 — Los Angeles</h1>
      <p className="text-slate-500 text-sm mb-6">Algorithmes ML entraînés sur l'historique complet des médailles par pays.</p>

      {/* Controls */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5 mb-6 flex gap-4 flex-wrap items-end">
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-slate-500">Algorithme</label>
          <select value={model} onChange={e => setModel(e.target.value)} className="text-sm border border-slate-200 rounded-lg px-3 py-1.5">
            {MODELS.map(m => <option key={m.id} value={m.id}>{m.label}</option>)}
          </select>
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-slate-500">Nombre de pays : {topN}</label>
          <input type="range" min={5} max={30} value={topN} onChange={e => setTopN(+e.target.value)} className="accent-blue-500" />
        </div>
        <button onClick={handleRun} className="bg-red-600 hover:bg-red-700 text-white font-semibold px-6 py-2 rounded-xl shadow-sm transition-all text-sm">
          🚀 Calculer les prédictions
        </button>
      </div>

      {predictions && (
        <div className="bg-green-50 border border-green-100 rounded-xl px-4 py-2 text-sm text-green-700 mb-4">
          ✅ {predictions.length} pays prédits avec <strong>{MODELS.find(m => m.id === model)?.label}</strong>
        </div>
      )}

      <div className="flex gap-1 bg-slate-100 p-1 rounded-xl mb-6 w-fit flex-wrap">
        {TABS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${tab === t.id ? 'bg-white shadow-sm text-blue-600' : 'text-slate-500 hover:text-slate-700'}`}>
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'classement' && (
        !run ? <div className="text-slate-400 py-16 text-center">Cliquez sur <strong>Calculer les prédictions</strong> pour afficher le classement.</div> :
        lp ? <Spinner /> : (
          <PlotlyChart
            data={predData}
            layout={{ yaxis: { categoryorder: 'total ascending' }, title: { text: `Prédictions JO 2028 — Top ${topN} pays` } }}
            height={620}
          />
        )
      )}

      {tab === 'historique' && (
        <div>
          <SectionHeader title="📈 Évolution historique + projection 2028" />
          <div className="mb-4">
            <select value={selectedCountry} onChange={e => setSelectedCountry(e.target.value)} className="text-sm border border-slate-200 rounded-lg px-3 py-1.5 w-72">
              <option value="">Sélectionner un pays…</option>
              {(predictions ?? []).map((p: any) => <option key={p.noc} value={p.country}>{p.country}</option>)}
            </select>
          </div>
          {selectedCountry && trendData.length > 0 && (
            <PlotlyChart data={trendData} layout={{ title: { text: `${selectedCountry} — historique + projection` }, legend: { orientation: 'h' } }} height={400} />
          )}
          <Warning>Les prédictions représentent une tendance statistique, pas une certitude. Seules les nations actives depuis 2016 sont projetées.</Warning>
        </div>
      )}

      {tab === 'cotes' && (
        <div>
          <SectionHeader title="🎯 Côtes athlètes — score pondéré (Or=3, Argent=2, Bronze=1)" />
          <PlotlyChart data={ratingsData} layout={{ yaxis: { categoryorder: 'total ascending' }, title: { text: 'Top 20 athlètes — côte de performance 2016+' } }} height={520} />
          <Insight>Le score pondéré intègre le volume de médailles et la régularité inter-éditions (+15% par édition supplémentaire).</Insight>
        </div>
      )}

      {tab === 'recommandations' && recs && (
        <div>
          <SectionHeader title="💡 Recommandations stratégiques" />
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
              <h3 className="font-semibold text-slate-700 mb-3">🌱 Nations en progression</h3>
              <table className="w-full text-sm">
                <thead><tr className="text-slate-400 text-xs border-b"><th className="text-left pb-2">Pays</th><th className="text-right pb-2">Croissance %</th></tr></thead>
                <tbody>{recs.rising_nations.map((r: any, i: number) => (
                  <tr key={i} className="border-b border-slate-50"><td className="py-1.5">{r.Team}</td><td className="text-right text-emerald-600 font-medium">+{r.growth_pct?.toFixed(0)}%</td></tr>
                ))}</tbody>
              </table>
            </div>
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
              <h3 className="font-semibold text-slate-700 mb-3">🏋️ France — top disciplines</h3>
              <table className="w-full text-sm">
                <thead><tr className="text-slate-400 text-xs border-b"><th className="text-left pb-2">Sport</th><th className="text-right pb-2">Médailles</th></tr></thead>
                <tbody>{recs.france_top_sports.map((r: any, i: number) => (
                  <tr key={i} className="border-b border-slate-50"><td className="py-1.5">{r.Sport}</td><td className="text-right font-medium">{r.medals_recent}</td></tr>
                ))}</tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {tab === 'timeline' && (
        <div>
          <SectionHeader title="⏱️ Diversité olympique par édition" />
          <PlotlyChart
            data={divData}
            layout={{
              title: { text: 'Pays médaillés & Disciplines par édition' },
              yaxis: { title: { text: 'Pays médaillés' } },
              yaxis2: { title: { text: 'Disciplines' }, overlaying: 'y', side: 'right' },
              legend: { orientation: 'h' },
            }}
            height={440}
          />
        </div>
      )}

      <div className="text-center text-slate-400 text-xs mt-10 pb-4">YPerf · Ynov · 2026</div>
    </div>
  )
}
