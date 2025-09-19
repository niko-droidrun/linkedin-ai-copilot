interface HeaderProps {
  title: string
  onBack?: () => void
}

export default function Header({ title, onBack }: HeaderProps) {
  return (
    <div className="w-full bg-blue-600 text-white font-bold text-lg flex items-center justify-center h-12 px-4 relative">
      {onBack && (
        <button
          onClick={onBack}
          className="absolute left-4 bg-white text-blue-600 px-3 py-1 rounded hover:bg-gray-200"
        >
          ←
        </button>
      )}
      <span className="text-center">{title}</span>
    </div>
  )
}

