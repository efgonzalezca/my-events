import { Button } from './Button'

interface Props {
  page: number
  total: number
  size: number
  onChange: (page: number) => void
}

export function Pager({ page, total, size, onChange }: Props) {
  const pages = Math.max(1, Math.ceil(total / size))
  if (pages <= 1) return null
  return (
    <div className="flex items-center justify-center gap-3 py-4">
      <Button
        variant="ghost"
        disabled={page <= 1}
        onClick={() => onChange(page - 1)}
      >
        ‹ Anterior
      </Button>
      <span className="text-sm text-slate-600">
        Página {page} de {pages}
      </span>
      <Button
        variant="ghost"
        disabled={page >= pages}
        onClick={() => onChange(page + 1)}
      >
        Siguiente ›
      </Button>
    </div>
  )
}
