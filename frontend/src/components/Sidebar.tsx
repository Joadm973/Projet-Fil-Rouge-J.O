import { NavLink } from 'react-router-dom'
import {
  Home, BarChart2, Users, TrendingUp, MessageSquare, Sprout, Globe
} from 'lucide-react'

const NAV = [
  { to: '/', icon: Home, label: 'Accueil' },
  { to: '/exploration', icon: BarChart2, label: 'Exploration' },
  { to: '/athletes', icon: Users, label: 'Athlètes' },
  { to: '/predictions', icon: TrendingUp, label: 'Prédictions 2028' },
  { to: '/annotations', icon: MessageSquare, label: 'Annotations' },
  { to: '/generations', icon: Sprout, label: 'Générations' },
  { to: '/multisource', icon: Globe, label: 'Multi-sources' },
]

export default function Sidebar() {
  return (
    <aside style={{ width: 'var(--sidebar-w)', background: 'var(--sidebar-bg)' }}
      className="fixed top-0 left-0 h-full flex flex-col z-50">

      {/* Custom Logo & Wordmark */}
      <div className="px-5 pt-24 pb-8 text-center flex flex-col items-center flex-shrink-0">
        <div style={{ marginBottom: '16px' }}>
          <svg width="130" height="74" viewBox="0 0 100 55" fill="none" xmlns="http://www.w3.org/2000/svg">
            {/* 5 Olympic Rings in Gold */}
            <circle cx="28" cy="28" r="13" stroke="#D4AF37" strokeWidth="2.5" fill="none" />
            <circle cx="50" cy="28" r="13" stroke="#D4AF37" strokeWidth="2.5" fill="none" />
            <circle cx="72" cy="28" r="13" stroke="#D4AF37" strokeWidth="2.5" fill="none" />
            <circle cx="39" cy="39" r="13" stroke="#D4AF37" strokeWidth="2.5" fill="none" />
            <circle cx="61" cy="39" r="13" stroke="#D4AF37" strokeWidth="2.5" fill="none" />
          </svg>
        </div>
        <span style={{ color: '#ffffff', fontSize: '1.75rem', fontWeight: 800, letterSpacing: '-0.02em', lineHeight: 1 }}>
          YPerf
        </span>
        <div style={{ color: 'rgba(255,255,255,0.35)', fontSize: '0.78rem', marginTop: '6px', letterSpacing: '0.02em', fontWeight: 500 }}>
          JO · Los Angeles 2028
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-2 overflow-y-auto flex flex-col justify-center">
        <div style={{ color: 'rgba(255,255,255,0.22)', fontSize: '0.62rem', fontWeight: 600, letterSpacing: '0.1em', textTransform: 'uppercase', padding: '0 10px 8px', textAlign: 'center' }}>
          Navigation
        </div>
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className="block"
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: '9px',
              padding: '7px 10px',
              borderRadius: '6px',
              marginBottom: '12px',
              fontSize: '0.82rem',
              fontWeight: isActive ? 600 : 400,
              color: isActive ? '#ffffff' : 'rgba(255,255,255,0.45)',
              background: isActive ? 'rgba(255,255,255,0.08)' : 'transparent',
              textDecoration: 'none',
              transition: 'all 0.12s',
            })}
            onMouseEnter={e => {
              const t = e.currentTarget
              if (!t.getAttribute('aria-current')) t.style.color = 'rgba(255,255,255,0.75)'
            }}
            onMouseLeave={e => {
              const t = e.currentTarget
              if (!t.getAttribute('aria-current')) t.style.color = 'rgba(255,255,255,0.45)'
            }}
          >
            <Icon size={14} strokeWidth={1.75} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Gold accent bar + footer */}
      <div>
        <div style={{ height: '1px', background: 'rgba(255,255,255,0.06)', margin: '0 16px' }} />
        <div style={{ padding: '16px', color: 'rgba(255,255,255,0.2)', fontSize: '0.65rem' }}>
          Ynov B3 · Data & IA · 2026
        </div>
      </div>
    </aside>
  )
}
