export default function SectionHeader({ title }: { title: string }) {
  return (
    <div className="bg-gradient-to-r from-blue-600 to-blue-500 text-white font-semibold text-sm px-4 py-2.5 rounded-xl mb-4 shadow-sm shadow-blue-200">
      {title}
    </div>
  )
}
