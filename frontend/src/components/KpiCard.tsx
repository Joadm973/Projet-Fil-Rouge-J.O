interface Props {
  value: string | number
  label: string
  sub?: string
}

export default function KpiCard({ value, label, sub }: Props) {
  return (
    <div className="card" style={{ padding: '20px 22px' }}>
      <div className="stat-number">{value}</div>
      <div className="label" style={{ marginTop: '8px' }}>{label}</div>
      {sub && <div style={{ fontSize: '0.72rem', color: 'var(--text-3)', marginTop: '4px' }}>{sub}</div>}
    </div>
  )
}
