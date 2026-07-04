import type { ReactNode } from 'react'

const BASE: React.CSSProperties = {
  borderRadius: 'var(--r-md)',
  padding: '12px 16px',
  fontSize: '0.82rem',
  lineHeight: '1.55',
  margin: '16px 0',
}

export function Insight({ children }: { children: ReactNode }) {
  return (
    <div style={{
      ...BASE,
      background: 'var(--gold-bg)',
      border: '1px solid var(--gold-border)',
      color: '#6b5820',
    }}>
      {children}
    </div>
  )
}

export function Warning({ children }: { children: ReactNode }) {
  return (
    <div style={{
      ...BASE,
      background: 'var(--surface-2)',
      border: '1px solid var(--border)',
      color: 'var(--text-2)',
    }}>
      {children}
    </div>
  )
}
