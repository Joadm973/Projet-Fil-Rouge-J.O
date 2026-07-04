import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchJSON } from '../lib/api'
import SectionHeader from '../components/SectionHeader'
import PlotlyChart from '../components/PlotlyChart'
import Spinner from '../components/Spinner'
import { Insight } from '../components/InsightBox'
import Tabs from '../components/Tabs'
import PageHeader from '../components/PageHeader'

type Tab = 'talents' | 'breakouts' | 'renouvellement' | 'nations'

const TABS = [
  { id: 'talents' as Tab,       label: 'Nouveaux talents' },
  { id: 'breakouts' as Tab,     label: 'Révélations' },
  { id: 'renouvellement' as Tab, label: 'Renouvellement' },
  { id: 'nations' as Tab,       label: 'Nouvelles nations' },
]

export default function Generations() {
  const [tab, setTab] = useState<Tab>('talents')

  const { data: newGen, isLoading: lg } = useQuery({ queryKey: ['new-gen'],    queryFn: () => fetchJSON<any[]>('/generations/new-gen') })
  const { data: breakouts }             = useQuery({ queryKey: ['breakouts'],   queryFn: () => fetchJSON<any[]>('/generations/breakouts') })
  const { data: shift }                 = useQuery({ queryKey: ['gen-shift'],   queryFn: () => fetchJSON<any[]>('/generations/generation-shift') })
  const { data: nations }               = useQuery({ queryKey: ['new-nations'], queryFn: () => fetchJSON<any[]>('/generations/new-nations') })

  const top20 = (newGen ?? []).slice(0, 20)

  const newGenData = [{
    type: 'bar' as const, orientation: 'h' as const,
    x: top20.map(r => r.score), y: top20.map(r => r.Name),
    marker: {
      color: top20.map((r: any) => r.debut_year >= 2024 ? '#c9a227' : r.debut_year >= 2020 ? '#374151' : '#9e9993'),
      line: { width: 0 },
    },
    text: top20.map(r => r.score?.toFixed(1)), textposition: 'outside' as const,
  }]

  const boByYear = (breakouts ?? []).reduce((acc: Record<number, number>, r: any) => {
    acc[r.debut_year] = (acc[r.debut_year] ?? 0) + 1
    return acc
  }, {})
  const boYears = Object.keys(boByYear).sort()
  const boData = [{
    type: 'bar' as const,
    x: boYears, y: boYears.map(y => boByYear[+y]),
    marker: { color: '#c9a227', line: { width: 0 } },
    text: boYears.map(y => boByYear[+y]), textposition: 'outside' as const,
  }]

  // Taux de renouvellement des athlètes dominants par discipline (2008-2016 vs 2020-2024)
  const shiftTop = [...(shift ?? [])]
    .sort((a: any, b: any) => b.renewal_rate - a.renewal_rate)
    .slice(0, 20)
  const shiftData = [{
    type: 'bar' as const, orientation: 'h' as const,
    x: shiftTop.map((r: any) => Math.round(r.renewal_rate * 100)),
    y: shiftTop.map((r: any) => r.Sport),
    marker: { color: '#c9a227', line: { width: 0 } },
    text: shiftTop.map((r: any) => `${Math.round(r.renewal_rate * 100)}%`),
    textposition: 'outside' as const,
  }]

  const nationsTop = (nations ?? []).slice(0, 20)
  const nationsData = [{
    type: 'bar' as const, orientation: 'h' as const,
    x: nationsTop.map(r => r.debut_editions), y: nationsTop.map(r => r.Team),
    marker: { color: '#374151', line: { width: 0 } },
    text: nationsTop.map(r => r.debut_editions), textposition: 'outside' as const,
  }]

  return (
    <div>
      <PageHeader title="Nouvelles générations" sub="Détection des talents émergents et renouvellement des nations olympiques." badge="Analyse · 2016–2024" />

      <Tabs tabs={TABS} active={tab} onChange={setTab} />

      {tab === 'talents' && (
        <>
          <SectionHeader title="Talents émergents" sub="Score pondéré : Or=3, Arg=2, Bro=1 × récence" />
          {lg ? <Spinner /> : (
            <>
              <PlotlyChart data={newGenData} layout={{ yaxis: { categoryorder: 'total ascending' }, margin: { t: 16, r: 52, b: 28, l: 140 } }} height={560} />
              <div style={{ display: 'flex', gap: '16px', marginTop: '12px', fontSize: '0.78rem', color: 'var(--text-3)' }}>
                {[{ color: '#c9a227', label: 'Débuts 2024' }, { color: '#374151', label: 'Débuts 2020–2023' }, { color: '#9e9993', label: 'Antérieurs' }].map(({ color, label }) => (
                  <div key={label} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ width: '10px', height: '10px', borderRadius: '2px', background: color, display: 'inline-block' }} />
                    {label}
                  </div>
                ))}
              </div>
            </>
          )}
          <Insight>Les athlètes de la cohorte 2024 avec plusieurs podiums sont les favoris à surveiller pour Los Angeles 2028.</Insight>
        </>
      )}

      {tab === 'breakouts' && (
        <>
          <SectionHeader title="Révélations par édition" sub="Nombre d'athlètes ayant décroché leur premier podium" />
          <PlotlyChart data={boData} layout={{ margin: { t: 16, r: 52, b: 36, l: 48 } }} height={380} />
        </>
      )}

      {tab === 'renouvellement' && (
        <>
          <SectionHeader title="Renouvellement par discipline" sub="Part des athlètes dominants remplacés entre 2008–2016 et 2020–2024" />
          <PlotlyChart data={shiftData} layout={{ yaxis: { categoryorder: 'total ascending' }, xaxis: { title: { text: 'Taux de renouvellement (%)' }, range: [0, 110] }, margin: { t: 16, r: 52, b: 48, l: 140 } }} height={560} />
          <Insight>Un taux élevé indique que la plupart des athlètes qui dominaient une discipline ont été remplacés par une nouvelle vague — un signal fort de transition générationnelle vers 2028.</Insight>
        </>
      )}

      {tab === 'nations' && (
        <>
          <SectionHeader title="Nouvelles nations médaillées" sub="Pays ayant décroché leur première médaille récemment" />
          <PlotlyChart data={nationsData} layout={{ yaxis: { categoryorder: 'total ascending' }, margin: { t: 16, r: 52, b: 28, l: 120 } }} height={440} />
        </>
      )}

      <div style={{ borderTop: '1px solid var(--border-soft)', paddingTop: '20px', marginTop: '40px', textAlign: 'center', color: 'var(--text-3)', fontSize: '0.72rem' }}>YPerf · Ynov · 2026</div>
    </div>
  )
}
