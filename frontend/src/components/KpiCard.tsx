interface Props {
  icon: string
  value: string | number
  label: string
  color?: 'blue' | 'gold' | 'green' | 'red' | 'slate'
}

const COLORS = {
  blue:  'from-blue-500/10 to-blue-600/5 border-blue-200 text-blue-600',
  gold:  'from-amber-400/15 to-amber-500/5 border-amber-200 text-amber-600',
  green: 'from-emerald-500/10 to-emerald-600/5 border-emerald-200 text-emerald-600',
  red:   'from-red-500/10 to-red-600/5 border-red-200 text-red-600',
  slate: 'from-slate-400/10 to-slate-500/5 border-slate-200 text-slate-600',
}

export default function KpiCard({ icon, value, label, color = 'blue' }: Props) {
  return (
    <div className={`bg-gradient-to-br ${COLORS[color]} border rounded-2xl p-5 flex flex-col gap-1 hover:scale-[1.02] transition-transform`}>
      <div className="text-2xl">{icon}</div>
      <div className="text-2xl font-bold text-slate-800 mt-1">{value}</div>
      <div className="text-xs font-medium uppercase tracking-wider text-slate-500">{label}</div>
    </div>
  )
}
