interface Props {
  title: string
  sub?: string
}

export default function SectionHeader({ title, sub }: Props) {
  return (
    <div style={{ marginBottom: '20px', marginTop: '44px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div style={{ width: '3px', height: '18px', background: 'var(--gold)', borderRadius: '2px', flexShrink: 0 }} />
        <h2 style={{ margin: 0 }}>{title}</h2>
      </div>
      {sub && <p style={{ marginTop: '4px', marginLeft: '13px', fontSize: '0.8rem' }}>{sub}</p>}
    </div>
  )
}
