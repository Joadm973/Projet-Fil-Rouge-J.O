import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchJSON, api } from '../lib/api'
import PageHeader from '../components/PageHeader'
import Spinner from '../components/Spinner'

const TYPES = ['Athlète', 'Pays', 'Sport', 'Édition']

const typeMap: Record<string, string> = {
  'Athlète': 'athlete',
  'Pays': 'pays',
  'Sport': 'sport',
  'Édition': 'edition'
}

const typeLabels: Record<string, string> = {
  'athlete': 'Athlète',
  'pays': 'Pays',
  'sport': 'Sport',
  'edition': 'Édition'
}

const input: React.CSSProperties = {
  fontSize: '0.82rem', fontFamily: 'inherit', width: '100%',
  border: '1px solid var(--border)', borderRadius: 'var(--r-sm)',
  padding: '7px 10px', background: 'var(--surface)', color: 'var(--text-1)',
  outline: 'none', transition: 'border-color 0.1s',
}

export default function Annotations() {
  const qc = useQueryClient()
  const [type, setType] = useState('Athlète')
  const [target, setTarget] = useState('')
  const [note, setNote] = useState('')
  const [author, setAuthor] = useState('Utilisateur')
  const [tags, setTags] = useState('')
  const [filterType, setFilterType] = useState('')
  const [search, setSearch] = useState('')

  const { data: anns, isLoading } = useQuery({ queryKey: ['annotations', filterType], queryFn: () => fetchJSON<any[]>('/annotations/', filterType ? { type: typeMap[filterType] } : undefined) })
  const { data: targets } = useQuery({ queryKey: ['ann-targets', type], queryFn: () => fetchJSON<string[]>('/annotations/targets', { type: typeMap[type] }) })

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
      <PageHeader title="Annotations" sub="Notes personnelles sur athlètes, pays, sports et éditions." badge="Annotations utilisateur" />

      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '20px' }}>
        {/* Form */}
        <div className="card" style={{ padding: '20px', height: 'fit-content', position: 'sticky', top: '20px' }}>
          <h3 style={{ marginBottom: '16px' }}>Nouvelle annotation</h3>

          <div style={{ marginBottom: '14px' }}>
            <div className="label" style={{ marginBottom: '8px' }}>Type</div>
            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
              {TYPES.map(t => (
                <button key={t} onClick={() => setType(t)} style={{
                  padding: '4px 12px', borderRadius: 'var(--r-sm)', fontSize: '0.78rem', fontFamily: 'inherit', cursor: 'pointer',
                  border: type === t ? '1px solid var(--gold)' : '1px solid var(--border)',
                  background: type === t ? 'var(--gold-bg)' : 'transparent',
                  color: type === t ? '#6b5820' : 'var(--text-2)', fontWeight: type === t ? 600 : 400,
                }}>
                  {t}
                </button>
              ))}
            </div>
          </div>

          <div style={{ marginBottom: '12px' }}>
            <div className="label" style={{ marginBottom: '6px' }}>Cible</div>
            <select value={target} onChange={e => setTarget(e.target.value)} style={{ ...input }}>
              <option value="">Sélectionner…</option>
              {(targets ?? []).map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>

          <div style={{ marginBottom: '12px' }}>
            <div className="label" style={{ marginBottom: '6px' }}>Auteur</div>
            <input value={author} onChange={e => setAuthor(e.target.value)} style={input} />
          </div>

          <div style={{ marginBottom: '12px' }}>
            <div className="label" style={{ marginBottom: '6px' }}>Tags</div>
            <input value={tags} onChange={e => setTags(e.target.value)} placeholder="record, à surveiller" style={input} />
          </div>

          <div style={{ marginBottom: '16px' }}>
            <div className="label" style={{ marginBottom: '6px' }}>Note</div>
            <textarea value={note} onChange={e => setNote(e.target.value)} rows={4}
              style={{ ...input, resize: 'none', lineHeight: '1.5' }} />
          </div>

          <button
            onClick={() => addMut.mutate({ type: typeMap[type], target, note, author, tags })}
            disabled={!target || !note || addMut.isPending}
            style={{
              width: '100%', padding: '8px', fontSize: '0.82rem', fontWeight: 600, fontFamily: 'inherit',
              background: (!target || !note) ? 'var(--border)' : 'var(--text-1)',
              color: (!target || !note) ? 'var(--text-3)' : '#fff',
              border: 'none', borderRadius: 'var(--r-sm)', cursor: (!target || !note) ? 'default' : 'pointer',
            }}
          >
            {addMut.isPending ? 'Enregistrement…' : 'Enregistrer →'}
          </button>
        </div>

        {/* List */}
        <div>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '16px' }}>
            <select value={filterType} onChange={e => setFilterType(e.target.value)} style={{ ...input, width: 'auto' }}>
              <option value="">Tous les types</option>
              {TYPES.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
            <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Rechercher…" style={{ ...input }} />
          </div>

          {isLoading ? <Spinner /> : filtered.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '64px 0', color: 'var(--text-3)', fontSize: '0.85rem' }}>
              Aucune annotation. Ajoutez-en une à gauche.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {filtered.map((a: any) => (
                <div key={a.id} className="card" style={{ padding: '14px 16px', display: 'flex', gap: '12px' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                      <span style={{ fontSize: '0.68rem', fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase', background: 'var(--surface-3)', border: '1px solid var(--border)', borderRadius: '4px', padding: '2px 7px', color: 'var(--text-2)' }}>{typeLabels[a.type] || a.type}</span>
                      <span style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--text-1)' }}>{a.target}</span>
                      <span style={{ marginLeft: 'auto', fontSize: '0.72rem', color: 'var(--text-3)' }}>{a.author} · {new Date(a.timestamp).toLocaleDateString('fr-FR')}</span>
                    </div>
                    <p style={{ fontSize: '0.82rem', color: 'var(--text-2)', lineHeight: '1.5' }}>{a.note}</p>
                    {a.tags && (
                      <div style={{ display: 'flex', gap: '5px', marginTop: '8px', flexWrap: 'wrap' }}>
                        {(Array.isArray(a.tags) ? a.tags : a.tags.split(',')).filter(Boolean).map((tag: string) => (
                          <span key={tag} style={{ fontSize: '0.68rem', background: 'var(--surface-3)', color: 'var(--text-3)', border: '1px solid var(--border)', borderRadius: '4px', padding: '1px 7px' }}>{tag.trim()}</span>
                        ))}
                      </div>
                    )}
                  </div>
                  <button onClick={() => delMut.mutate(a.id)}
                    style={{ color: 'var(--border)', background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.1rem', alignSelf: 'flex-start', lineHeight: 1, padding: '2px', transition: 'color 0.1s' }}
                    onMouseEnter={e => (e.currentTarget.style.color = 'var(--red)')}
                    onMouseLeave={e => (e.currentTarget.style.color = 'var(--border)')}>×</button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div style={{ borderTop: '1px solid var(--border-soft)', paddingTop: '20px', marginTop: '40px', textAlign: 'center', color: 'var(--text-3)', fontSize: '0.72rem' }}>YPerf · Ynov · 2026</div>
    </div>
  )
}
