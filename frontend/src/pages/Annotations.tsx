import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchJSON, api } from '../lib/api'
import SectionHeader from '../components/SectionHeader'
import Spinner from '../components/Spinner'

const TYPES = ['Athlète', 'Pays', 'Sport', 'Édition']

export default function Annotations() {
  const qc = useQueryClient()
  const [type, setType] = useState('Athlète')
  const [target, setTarget] = useState('')
  const [note, setNote] = useState('')
  const [author, setAuthor] = useState('Utilisateur')
  const [tags, setTags] = useState('')
  const [filterType, setFilterType] = useState('')
  const [search, setSearch] = useState('')

  const { data: anns, isLoading } = useQuery({ queryKey: ['annotations', filterType], queryFn: () => fetchJSON<any[]>('/annotations/', filterType ? { type: filterType } : undefined) })
  const { data: targets } = useQuery({ queryKey: ['ann-targets', type], queryFn: () => fetchJSON<string[]>('/annotations/targets', { type }) })

  const addMut = useMutation({
    mutationFn: (body: any) => api.post('/annotations/', body).then(r => r.data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['annotations'] }); setNote(''); setTags(''); setTarget('') },
  })

  const delMut = useMutation({
    mutationFn: (id: string) => api.delete(`/annotations/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['annotations'] }),
  })

  const filtered = (anns ?? []).filter(a => !search || JSON.stringify(a).toLowerCase().includes(search.toLowerCase()))

  return (
    <div>
      <h1 className="text-2xl font-black text-slate-800 mb-1" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>📝 Annotations</h1>
      <p className="text-slate-500 text-sm mb-6">Ajoutez des notes personnelles sur athlètes, pays, sports ou éditions.</p>

      <div className="grid grid-cols-3 gap-6 mb-8">
        {/* Form */}
        <div className="col-span-1 bg-white rounded-2xl border border-slate-100 shadow-sm p-5 flex flex-col gap-3">
          <SectionHeader title="➕ Nouvelle annotation" />
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-slate-500">Type</label>
            <div className="flex gap-2 flex-wrap">
              {TYPES.map(t => (
                <button key={t} onClick={() => setType(t)}
                  className={`px-3 py-1 rounded-lg text-xs font-medium border transition-all ${type === t ? 'bg-blue-600 text-white border-blue-600' : 'border-slate-200 text-slate-600 hover:bg-slate-50'}`}>
                  {t}
                </button>
              ))}
            </div>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-slate-500">Cible</label>
            <select value={target} onChange={e => setTarget(e.target.value)} className="text-sm border border-slate-200 rounded-lg px-3 py-1.5">
              <option value="">Sélectionner…</option>
              {(targets ?? []).map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-slate-500">Auteur</label>
            <input value={author} onChange={e => setAuthor(e.target.value)} className="text-sm border border-slate-200 rounded-lg px-3 py-1.5" />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-slate-500">Tags (virgule)</label>
            <input value={tags} onChange={e => setTags(e.target.value)} placeholder="record, à surveiller" className="text-sm border border-slate-200 rounded-lg px-3 py-1.5" />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-slate-500">Note</label>
            <textarea value={note} onChange={e => setNote(e.target.value)} rows={4} className="text-sm border border-slate-200 rounded-lg px-3 py-2 resize-none" />
          </div>
          <button
            onClick={() => addMut.mutate({ type, target, note, author, tags })}
            disabled={!target || !note || addMut.isPending}
            className="bg-blue-600 disabled:opacity-40 hover:bg-blue-700 text-white font-semibold px-4 py-2 rounded-xl text-sm transition-all"
          >
            {addMut.isPending ? 'Enregistrement…' : '💾 Enregistrer'}
          </button>
        </div>

        {/* List */}
        <div className="col-span-2">
          <div className="flex gap-3 mb-4 flex-wrap">
            <select value={filterType} onChange={e => setFilterType(e.target.value)} className="text-sm border border-slate-200 rounded-lg px-3 py-1.5">
              <option value="">Tous les types</option>
              {TYPES.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
            <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Rechercher…" className="text-sm border border-slate-200 rounded-lg px-3 py-1.5 flex-1" />
          </div>

          {isLoading ? <Spinner /> : filtered.length === 0 ? (
            <div className="text-center py-16 text-slate-400 text-sm">Aucune annotation. Ajoutez-en une !</div>
          ) : (
            <div className="flex flex-col gap-3">
              {filtered.map((a: any) => (
                <div key={a.id} className="bg-white rounded-2xl border border-slate-100 shadow-sm p-4 flex gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="bg-blue-100 text-blue-700 text-xs font-medium px-2 py-0.5 rounded-full">{a.type}</span>
                      <span className="font-semibold text-slate-800 text-sm">{a.target}</span>
                      <span className="text-slate-400 text-xs ml-auto">{a.author} · {new Date(a.created_at).toLocaleDateString('fr-FR')}</span>
                    </div>
                    <p className="text-slate-600 text-sm">{a.note}</p>
                    {a.tags && <div className="flex gap-1 mt-2 flex-wrap">{a.tags.split(',').filter(Boolean).map((tag: string) => (
                      <span key={tag} className="bg-slate-100 text-slate-500 text-xs px-2 py-0.5 rounded-full">{tag.trim()}</span>
                    ))}</div>}
                  </div>
                  <button onClick={() => delMut.mutate(a.id)} className="text-slate-300 hover:text-red-400 transition-colors text-xl leading-none self-start">×</button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="text-center text-slate-400 text-xs mt-4 pb-4">YPerf · Ynov · 2026</div>
    </div>
  )
}
