import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchJSON } from '../lib/api'
import SectionHeader from '../components/SectionHeader'
import PlotlyChart from '../components/PlotlyChart'
import Spinner from '../components/Spinner'
import { Insight } from '../components/InsightBox'

type Tab = 'talents' | 'breakouts' | 'renouvellement' | 'nations'

export default function Generations() {
  const [tab, setTab] = useState<Tab>('talents')

  const { data: newGen, isLoading: lg } = useQuery({ queryKey: ['new-gen'], queryFn: () => fetchJSON<any[]>('/generations/new-gen') })
  const { data: breakouts, isLoading: lb } = useQuery({ queryKey: ['breakouts'], queryFn: () => fetchJSON<any[]>('/generations/breakouts') })
  const { data: shift, isLoading: ls } = useQuery({ queryKey: ['gen-shift'], queryFn: () => fetchJSON<any[]>('/generations/generation-shift') })
  const { data: nations, isLoading: ln } = useQuery({ queryKey: ['new-nations'], queryFn: () => fetchJSON<any[]>('/generations/new-nations') })

  const top20 = (newGen ?? []).slice(0, 20)
  const genColors = top20.map((r: any) => r.debut_year >= 2024 ? '#ef4444' : r.debut_year >= 2020 ? '#10b981' : '#3b82f6')

  const newGenData = [{
    type: 'bar' as const, orientation: 'h' as const,
    x: top20.map(r => r.score), y: top20.map(r => r.Name),
    marker: { color: genColors },
    text: top20.map(r => r.score?.toFixed(1)), textposition: 'outside' as const,
  }]

  const boByYear = (breakouts ?? []).reduce((acc: Record<number, number>, r: any) => {
    acc[r.debut_year] = (acc[r.debut_year] ?? 0) + 1
    return acc
  }, {})
  const boYears = Object.keys(boByYear).sort().map(Number)
  const boData = [{
    type: 'bar' as const, x: boYears, y: boYears.map(y => boByYear[y]),
    marker: { color: '#8b5cf6' },
  }]

  const top15Shift = (shift ?? []).slice(0, 15)
  const shiftData = [{
    type: 'bar' as const, orientation: 'h' as const,
    x: top15Shift.map(r => (r.renewal_rate * 100).toFixed(0)),
    y: top15Shift.map(r => r.Sport),
    marker: { color: '#10b981' },
    text: top15Shift.map(r => `${(r.renewal_rate * 100).toFixed(0)}%`),
    textposition: 'outside' as const,
  }]

  const nationsData = [{
    type: 'choropleth' as const,
    locations: (nations ?? []).map(r => r.NOC),
    z: (nations ?? []).map(() => 1),
    text: (nations ?? []).map(r => `${r.Team} — 1ère médaille : ${r.first_medal_year}`),
    colorscale: [[0, '#10b981'], [1, '#10b981']],
    showscale: false,
  }]

  const TABS = [
    { id: 'talents' as Tab, label: '🚀 Talents 2016+' },
    { id: 'breakouts' as Tab, label: '⚡ Breakouts 2020+' },
    { id: 'renouvellement' as Tab, label: '🔄 Renouvellement' },
    { id: 'nations' as Tab, label: '🌍 Nouvelles nations' },
  ]

  return (
    <div>
      <h1 className="text-2xl font-black text-slate-800 mb-1" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>🌱 Nouvelles générations</h1>
      <p className="text-slate-500 text-sm mb-6">Talents émergents, breakouts récents et renouvellement par discipline.</p>

      {/* KPIs */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Athlètes nouvelle gen (2016+)', value: newGen?.length ?? '…', icon: '🚀' },
          { label: 'Breakouts 2020+', value: breakouts?.length ?? '…', icon: '⚡' },
          { label: 'Sports avec renouvellement total', value: (shift ?? []).filter((r: any) => r.renewal_rate >= 1).length, icon: '🔄' },
          { label: 'Nouvelles nations depuis 2016', value: nations?.length ?? '…', icon: '🌍' },
        ].map((k, i) => (
          <div key={i} className="bg-white rounded-2xl border border-slate-100 shadow-sm p-4">
            <div className="text-2xl mb-1">{k.icon}</div>
            <div className="text-2xl font-bold text-slate-800">{k.value}</div>
            <div className="text-xs text-slate-500 mt-0.5">{k.label}</div>
          </div>
        ))}
      </div>

      <div className="flex gap-1 bg-slate-100 p-1 rounded-xl mb-6 w-fit">
        {TABS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${tab === t.id ? 'bg-white shadow-sm text-blue-600' : 'text-slate-500 hover:text-slate-700'}`}>
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'talents' && (
        <div>
          <SectionHeader title="🚀 Top 20 talents émergents — score pondéré (Or=3, Argent=2, Bronze=1)" />
          {lg ? <Spinner /> : (
            <>
              <PlotlyChart data={newGenData} layout={{ yaxis: { categoryorder: 'total ascending' }, title: { text: 'Top 20 — Bleu=2016, Vert=2020, Rouge=2024' } }} height={520} />
              <Insight>Le score pondéré récompense le volume de médailles et la régularité entre éditions.</Insight>
            </>
          )}
        </div>
      )}

      {tab === 'breakouts' && (
        <div>
          <SectionHeader title="⚡ Athlètes en percée — 1ère médaille à partir de 2020" />
          {lb ? <Spinner /> : (
            <div className="grid grid-cols-2 gap-4">
              <PlotlyChart data={boData} layout={{ title: { text: 'Breakouts par année de début' }, xaxis: { tickmode: 'linear' } }} height={400} />
              <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
                <h3 className="font-semibold text-slate-700 mb-3 text-sm">Top breakouts récents</h3>
                <div className="flex flex-col gap-2 max-h-[340px] overflow-y-auto">
                  {(breakouts ?? []).slice(0, 20).map((a: any, i: number) => (
                    <div key={i} className="flex items-center gap-3 py-1.5 border-b border-slate-50">
                      <span className="text-slate-400 text-xs w-5">{i + 1}</span>
                      <div className="flex-1">
                        <div className="text-sm font-medium text-slate-800">{a.Name}</div>
                        <div className="text-xs text-slate-400">{a.Team} · {a.Sport}</div>
                      </div>
                      <span className="text-xs font-semibold text-purple-600">{a.score?.toFixed(1)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {tab === 'renouvellement' && (
        <div>
          <SectionHeader title="🔄 Taux de renouvellement des dominants par sport (2008–2016 → 2020–2024)" />
          {ls ? <Spinner /> : (
            <PlotlyChart data={shiftData} layout={{ yaxis: { categoryorder: 'total ascending' }, title: { text: 'Renouvellement (%) — 100% = aucun dominant commun' } }} height={520} />
          )}
        </div>
      )}

      {tab === 'nations' && (
        <div>
          <SectionHeader title="🌍 Pays remportant leur 1ère médaille depuis 2016" />
          {ln ? <Spinner /> : (
            <div className="grid grid-cols-2 gap-4">
              <PlotlyChart
                data={nationsData}
                layout={{ geo: { showframe: false, bgcolor: 'rgba(0,0,0,0)' }, margin: { t: 44, r: 0, b: 0, l: 0 } }}
                height={380}
              />
              <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
                <h3 className="font-semibold text-slate-700 mb-3 text-sm">Nouvelles nations médaillées ({nations?.length})</h3>
                <div className="flex flex-col gap-2 max-h-[320px] overflow-y-auto">
                  {(nations ?? []).map((n: any, i: number) => (
                    <div key={i} className="flex items-center gap-3 py-1.5 border-b border-slate-50">
                      <span className="text-slate-400 text-xs w-5">{i + 1}</span>
                      <div className="flex-1">
                        <div className="text-sm font-medium text-slate-800">{n.Team}</div>
                        <div className="text-xs text-slate-400">{n.Sport}</div>
                      </div>
                      <span className="text-xs font-semibold text-emerald-600">{n.first_medal_year}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="text-center text-slate-400 text-xs mt-10 pb-4">YPerf · Ynov · 2026</div>
    </div>
  )
}
