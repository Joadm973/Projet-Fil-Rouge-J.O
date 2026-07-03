export function Insight({ children }: { children: React.ReactNode }) {
  return (
    <div className="bg-blue-50 border border-blue-100 rounded-xl px-4 py-3 text-sm text-blue-800 flex gap-2 items-start my-4">
      <span className="text-lg leading-none">💡</span>
      <span dangerouslySetInnerHTML={typeof children === 'string' ? { __html: children } : undefined}>
        {typeof children !== 'string' ? children : undefined}
      </span>
    </div>
  )
}

export function Warning({ children }: { children: React.ReactNode }) {
  return (
    <div className="bg-amber-50 border border-amber-100 rounded-xl px-4 py-3 text-sm text-amber-800 flex gap-2 items-start my-4">
      <span className="text-lg leading-none">⚠️</span>
      <span dangerouslySetInnerHTML={typeof children === 'string' ? { __html: children } : undefined}>
        {typeof children !== 'string' ? children : undefined}
      </span>
    </div>
  )
}
