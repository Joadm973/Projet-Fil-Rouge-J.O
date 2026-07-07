import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchJSON } from '../lib/api'
import type { Data } from 'plotly.js'
import SectionHeader from '../components/SectionHeader'
import PlotlyChart from '../components/PlotlyChart'
import Spinner from '../components/Spinner'
import { Insight, Warning } from '../components/InsightBox'
import Tabs from '../components/Tabs'
import PageHeader from '../components/PageHeader'

type Tab = 'classement' | 'historique' | 'cotes' | 'domination' | 'recommandations' | 'timeline'

const TABS = [
  { id: 'classement' as Tab,      label: 'Classement 2028' },
  { id: 'historique' as Tab,      label: 'Historique pays' },
  { id: 'cotes' as Tab,           label: 'Cotes athlètes' },
  { id: 'domination' as Tab,      label: 'Domination pays' },
  { id: 'recommandations' as Tab, label: 'Recommandations' },
  { id: 'timeline' as Tab,        label: 'Timeline' },
]

const MODELS = [
  { id: 'linear',            label: 'Régression Linéaire' },
  { id: 'ridge',             label: 'Ridge régularisé' },
  { id: 'gradient_boosting', label: 'Gradient Boosting' },
  { id: 'polynomial',        label: 'Polynomiale deg. 2' },
]

const select: React.CSSProperties = {
  fontSize: '0.8rem', fontFamily: 'inherit',
  border: '1px solid var(--border)', borderRadius: 'var(--r-sm)',
  padding: '6px 10px', background: 'var(--surface)', color: 'var(--text-1)',
  cursor: 'pointer', outline: 'none',
}

export default function Predictions() {
  const [tab, setTab] = useState<Tab>('classement')
  const [model, setModel] = useState('linear')
  const [topN, setTopN] = useState(20)
  const [run, setRun] = useState(false)
  const [selectedCountry, setSelectedCountry] = useState('')

  const { data: predictions, isLoading: lp } = useQuery({
    queryKey: ['predictions', model, topN],
    queryFn: () => fetchJSON<any[]>('/predictions/predict', { model, top_n: topN }),
    // L'onglet Historique a besoin de la liste des pays prédits pour son menu déroulant.
    enabled: run || tab === 'historique',
  })

  const { data: trend } = useQuery({
    queryKey: ['trend', selectedCountry],
    queryFn: () => fetchJSON<any>('/predictions/country-trend', { team: selectedCountry }),
    enabled: !!selectedCountry,
  })

  const { data: ratings } = useQuery({ queryKey: ['ratings'], queryFn: () => fetchJSON<any[]>('/predictions/athlete-ratings') })
  const { data: recs }    = useQuery({ queryKey: ['recs'],    queryFn: () => fetchJSON<any>('/predictions/recommendations') })
  const { data: diversity } = useQuery({ queryKey: ['diversity'], queryFn: () => fetchJSON<any>('/predictions/timeline-diversity') })
  const { data: dominance } = useQuery({ queryKey: ['dominance'], queryFn: () => fetchJSON<any[]>('/predictions/dominance') })
  const [dominanceSport, setDominanceSport] = useState('')

  const handleRun = () => setRun(true)

  const predData = [{
    type: 'bar' as const, orientation: 'h' as const,
    x: (predictions ?? []).map(r => r.predicted),
    y: (predictions ?? []).map(r => r.country),
    marker: { color: '#c9a227', line: { width: 0 } },
    text: (predictions ?? []).map(r => r.predicted), textposition: 'outside' as const,
    customdata: (predictions ?? []).map(r => r.mae),
    hovertemplate: '<b>%{y}</b><br>%{x} médailles prédites<br>MAE du modèle : ±%{customdata}<extra></extra>',
  }]

  const trendData: Data[] = []
  if (trend) {
    trendData.push({ type: 'scatter', mode: 'lines+markers', name: 'Historique', x: trend.history.map((r: any) => r.Year), y: trend.history.map((r: any) => r.total ?? r.medals ?? 0), line: { color: '#374151', width: 1.75 }, marker: { size: 5, color: '#374151' } })
    if (trend.pred2028 != null) {
      const last = trend.history[trend.history.length - 1]
      trendData.push({ type: 'scatter', mode: 'lines+markers', name: 'Projection 2028', x: [last?.Year, 2028], y: [last?.total ?? 0, trend.pred2028], line: { color: '#c9a227', width: 2, dash: 'dot' }, marker: { size: 6, color: '#c9a227' } })
    }
  }

  const ratingsData = [{
    type: 'bar' as const, orientation: 'h' as const,
    x: (ratings ?? []).slice(0, 20).map(r => r.cote),
    y: (ratings ?? []).slice(0, 20).map(r => r.Name),
    marker: { color: '#c9a227', line: { width: 0 } },
    text: (ratings ?? []).slice(0, 20).map(r => r.cote?.toFixed(1)), textposition: 'outside' as const,
  }]

  const dominanceSports = [...new Set((dominance ?? []).map((r: any) => r.Sport))].sort()
  const dominanceRows = (dominance ?? [])
    .filter((r: any) => !dominanceSport || r.Sport === dominanceSport)
    .sort((a: any, b: any) => b.dominance_pct - a.dominance_pct)
    .slice(0, 15)
  const dominanceData = [{
    type: 'bar' as const, orientation: 'h' as const,
    x: dominanceRows.map((r: any) => r.dominance_pct),
    y: dominanceRows.map((r: any) => dominanceSport ? r.Team : `${r.Team} · ${r.Sport}`),
    marker: { color: '#c9a227', line: { width: 0 } },
    text: dominanceRows.map((r: any) => `${r.dominance_pct}%`), textposition: 'outside' as const,
  }]

  const divData: Data[] = diversity ? [
    { type: 'bar', name: 'Pays médaillés', x: diversity.countries_per_year.map((r: any) => r.Year), y: diversity.countries_per_year.map((r: any) => r['Pays médaillés']), marker: { color: 'rgba(201,162,39,0.4)', line: { width: 0 } }, yaxis: 'y' },
    { type: 'scatter', mode: 'lines', name: 'Disciplines', x: diversity.sports_per_year.map((r: any) => r.Year), y: diversity.sports_per_year.map((r: any) => r.Disciplines), line: { color: '#374151', width: 1.75 }, yaxis: 'y2' },
  ] : []

  return (
    <div>
      <PageHeader title="Prédictions JO 2028" sub="Algorithmes ML entraînés sur l'historique complet des médailles par pays." badge="Los Angeles · Machine Learning" />

      {/* Controls */}
      <div className="card" style={{ padding: '16px 20px', marginBottom: '28px', display: 'flex', gap: '24px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
        <div>
          <div className="label" style={{ marginBottom: '6px' }}>Algorithme</div>
          <select value={model} onChange={e => setModel(e.target.value)} style={select}>
            {MODELS.map(m => <option key={m.id} value={m.id}>{m.label}</option>)}
          </select>
        </div>
        <div>
          <div className="label" style={{ marginBottom: '6px' }}>Nombre de pays · {topN}</div>
          <input type="range" min={5} max={30} value={topN} onChange={e => setTopN(+e.target.value)} style={{ accentColor: 'var(--gold)', width: '100px' }} />
        </div>
        <button
          onClick={handleRun}
          style={{ padding: '7px 18px', background: 'var(--text-1)', color: '#fff', border: 'none', borderRadius: 'var(--r-sm)', fontSize: '0.82rem', fontWeight: 600, fontFamily: 'inherit', cursor: 'pointer' }}
        >
          Calculer →
        </button>
      </div>

      {predictions && (
        <div style={{ background: 'var(--gold-bg)', border: '1px solid var(--gold-border)', borderRadius: 'var(--r-sm)', padding: '8px 14px', fontSize: '0.8rem', color: '#6b5820', marginBottom: '20px' }}>
          {predictions.length} pays prédits · <strong>{MODELS.find(m => m.id === model)?.label}</strong>
        </div>
      )}

      <Tabs tabs={TABS} active={tab} onChange={setTab} />

      {tab === 'classement' && (
        !run
          ? <div style={{ padding: '64px 0', textAlign: 'center', color: 'var(--text-3)', fontSize: '0.85rem' }}>Cliquez sur <strong>Calculer →</strong> pour afficher le classement.</div>
          : lp ? <Spinner />
          : <PlotlyChart data={predData} layout={{ yaxis: { categoryorder: 'total ascending' }, margin: { t: 20, r: 52, b: 28, l: 110 } }} height={580} />
      )}

      {tab === 'historique' && (
        <>
          <SectionHeader title="Évolution historique + projection 2028" />
          <div style={{ marginBottom: '16px' }}>
            <div className="label" style={{ marginBottom: '6px' }}>Pays</div>
            <select value={selectedCountry} onChange={e => setSelectedCountry(e.target.value)} style={{ ...select, minWidth: '220px' }}>
              <option value="">Sélectionner…</option>
              {(predictions ?? []).map((p: any) => <option key={p.noc} value={p.country}>{p.country}</option>)}
            </select>
          </div>
          {selectedCountry && trendData.length > 0 && (
            <PlotlyChart data={trendData} layout={{ showlegend: true, legend: { orientation: 'h', y: -0.14 } }} height={380} />
          )}
          <Warning>Tendance statistique uniquement. Seules les nations actives depuis 2016 sont projetées.</Warning>
        </>
      )}

      {tab === 'cotes' && (
        <>
          <SectionHeader title="Cotes athlètes" sub="Score pondéré : Or=3 pts, Argent=2 pts, Bronze=1 pt (+régularité)" />
          <PlotlyChart data={ratingsData} layout={{ yaxis: { categoryorder: 'total ascending' }, margin: { t: 20, r: 52, b: 28, l: 130 } }} height={500} />
          <Insight>Le score intègre le volume de médailles et la régularité entre éditions olympiques (+15% par édition supplémentaire).</Insight>
        </>
      )}

      {tab === 'domination' && (
        <>
          <SectionHeader title="Domination pays par discipline" sub="Part des médailles d'une discipline captée par un pays, depuis 2016" />
          <div style={{ marginBottom: '16px' }}>
            <div className="label" style={{ marginBottom: '6px' }}>Discipline</div>
            <select value={dominanceSport} onChange={e => setDominanceSport(e.target.value)} style={{ ...select, minWidth: '220px' }}>
              <option value="">Toutes disciplines (top 15 global)</option>
              {dominanceSports.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <PlotlyChart data={dominanceData} layout={{ yaxis: { categoryorder: 'total ascending' }, margin: { t: 20, r: 52, b: 28, l: 160 } }} height={560} />
          <Insight>Une dominance proche de 100% signifie qu'un seul pays a remporté quasiment toutes les médailles de la discipline depuis 2016 — un signal fort pour anticiper 2028.</Insight>
        </>
      )}

      {tab === 'recommandations' && recs && (
        <>
          <SectionHeader title="Recommandations stratégiques" />
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="card" style={{ padding: '20px 24px' }}>
              <h3 style={{ marginBottom: '14px' }}>Nations en progression</h3>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem' }}>
                <thead><tr><th style={{ textAlign: 'left', padding: '0 0 8px', color: 'var(--text-3)', fontWeight: 500, fontSize: '0.72rem' }}>Pays</th><th style={{ textAlign: 'right', padding: '0 0 8px', color: 'var(--text-3)', fontWeight: 500, fontSize: '0.72rem' }}>Croissance</th></tr></thead>
                <tbody>{recs.rising_nations.map((r: any, i: number) => (
                  <tr key={i} style={{ borderTop: '1px solid var(--border-soft)' }}>
                    <td style={{ padding: '7px 0', color: 'var(--text-1)' }}>{r.Team}</td>
                    <td style={{ textAlign: 'right', color: 'var(--green)', fontWeight: 600 }}>+{r.growth_pct?.toFixed(0)}%</td>
                  </tr>
                ))}</tbody>
              </table>
            </div>
            <div className="card" style={{ padding: '20px 24px' }}>
              <h3 style={{ marginBottom: '14px' }}>France — top disciplines</h3>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem' }}>
                <thead><tr><th style={{ textAlign: 'left', padding: '0 0 8px', color: 'var(--text-3)', fontWeight: 500, fontSize: '0.72rem' }}>Sport</th><th style={{ textAlign: 'right', padding: '0 0 8px', color: 'var(--text-3)', fontWeight: 500, fontSize: '0.72rem' }}>Médailles</th></tr></thead>
                <tbody>{recs.france_top_sports.map((r: any, i: number) => (
                  <tr key={i} style={{ borderTop: '1px solid var(--border-soft)' }}>
                    <td style={{ padding: '7px 0', color: 'var(--text-1)' }}>{r.Sport}</td>
                    <td style={{ textAlign: 'right', color: 'var(--text-2)', fontWeight: 600 }}>{r.medals_recent}</td>
                  </tr>
                ))}</tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {tab === 'timeline' && (
        <>
          <SectionHeader title="Diversité olympique par édition" />
          <PlotlyChart data={divData} layout={{ showlegend: true, legend: { orientation: 'h', y: -0.14 }, yaxis: { title: { text: 'Pays médaillés' } }, yaxis2: { title: { text: 'Disciplines' }, overlaying: 'y', side: 'right' } }} height={420} />
        </>
      )}

      <div style={{ borderTop: '1px solid var(--border-soft)', paddingTop: '20px', marginTop: '40px', textAlign: 'center', color: 'var(--text-3)', fontSize: '0.72rem' }}>YPerf · Ynov · 2026</div>
    </div>
  )
}
