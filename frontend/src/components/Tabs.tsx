interface Tab<T extends string> {
  id: T
  label: string
}

interface Props<T extends string> {
  tabs: Tab<T>[]
  active: T
  onChange: (id: T) => void
}

export default function Tabs<T extends string>({ tabs, active, onChange }: Props<T>) {
  return (
    <div style={{
      display: 'flex', gap: '2px',
      background: 'var(--surface-3)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--r-md)',
      padding: '3px',
      width: 'fit-content',
      marginBottom: '24px',
    }}>
      {tabs.map(t => (
        <button
          key={t.id}
          onClick={() => onChange(t.id)}
          style={{
            padding: '6px 14px',
            borderRadius: '7px',
            border: 'none',
            cursor: 'pointer',
            fontSize: '0.8rem',
            fontWeight: active === t.id ? 600 : 400,
            fontFamily: 'inherit',
            color: active === t.id ? 'var(--text-1)' : 'var(--text-3)',
            background: active === t.id ? 'var(--surface)' : 'transparent',
            boxShadow: active === t.id ? 'var(--shadow-xs)' : 'none',
            transition: 'all 0.1s',
            whiteSpace: 'nowrap',
          }}
        >
          {t.label}
        </button>
      ))}
    </div>
  )
}
