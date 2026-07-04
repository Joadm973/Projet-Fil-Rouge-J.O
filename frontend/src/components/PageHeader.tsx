interface Props {
  title: string
  sub?: string
  badge?: string
}

export default function PageHeader({ title, sub, badge }: Props) {
  return (
    <div style={{ marginBottom: '32px' }}>
      {badge && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
          <span style={{ width: '5px', height: '5px', borderRadius: '50%', background: 'var(--gold)', display: 'inline-block' }} />
          <span className="label">{badge}</span>
        </div>
      )}
      <h1 style={{ fontSize: '1.6rem', letterSpacing: '-0.03em', marginBottom: sub ? '6px' : 0 }}>{title}</h1>
      {sub && <p style={{ fontSize: '0.85rem', color: 'var(--text-2)' }}>{sub}</p>}
    </div>
  )
}
