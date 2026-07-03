import { NavLink } from 'react-router-dom'
import {
  Home, BarChart2, Users, TrendingUp, MessageSquare, Sprout, Globe
} from 'lucide-react'

const NAV = [
  { to: '/',            icon: Home,          label: 'Accueil' },
  { to: '/exploration', icon: BarChart2,      label: 'Exploration' },
  { to: '/athletes',    icon: Users,          label: 'Athlètes' },
  { to: '/predictions', icon: TrendingUp,     label: 'Prédictions 2028' },
  { to: '/annotations', icon: MessageSquare,  label: 'Annotations' },
  { to: '/generations', icon: Sprout,         label: 'Nouvelles générations' },
  { to: '/multisource', icon: Globe,          label: 'Multi-sources' },
]

export default function Sidebar() {
  return (
    <aside className="fixed top-0 left-0 h-full w-[220px] bg-[#0a0f2e] flex flex-col z-50 shadow-2xl">
      {/* Logo */}
      <div className="flex flex-col items-center py-7 border-b border-white/10">
        <div className="text-4xl mb-1">🏅</div>
        <div className="text-white font-bold text-lg tracking-tight" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
          YPerf
        </div>
        <div className="text-white/40 text-[11px] mt-0.5">Los Angeles 2028</div>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 overflow-y-auto">
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 mx-2 my-0.5 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                isActive
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/30'
                  : 'text-white/60 hover:bg-white/8 hover:text-white'
              }`
            }
          >
            <Icon size={16} strokeWidth={2} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="border-t border-white/10 py-4 px-4 text-center text-white/30 text-[10px]">
        Ynov Bachelor 3 · Data &amp; IA · 2026
      </div>
    </aside>
  )
}
