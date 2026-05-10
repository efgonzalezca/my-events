import { useEffect, useState, type FormEvent } from 'react'
import { eventsApi } from '../api/events'
import { Button } from '../components/Button'
import { EventCard } from '../components/EventCard'
import { Input } from '../components/Input'
import { Pager } from '../components/Pager'
import { Spinner } from '../components/Spinner'
import { describeError } from '../lib/errors'
import type { Event, Page } from '../types'

const PAGE_SIZE = 12

export function EventsListPage() {
  const [data, setData] = useState<Page<Event> | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [q, setQ] = useState('')
  const [activeQ, setActiveQ] = useState('')
  const [page, setPage] = useState(1)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    eventsApi
      .list({ q: activeQ || undefined, page, size: PAGE_SIZE })
      .then((res) => {
        if (!cancelled) {
          setData(res)
          setError(null)
        }
      })
      .catch((err) => {
        if (!cancelled) setError(describeError(err, 'No pudimos cargar los eventos.'))
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [activeQ, page])

  const onSearch = (e: FormEvent) => {
    e.preventDefault()
    setPage(1)
    setActiveQ(q.trim())
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      <div className="flex items-center justify-between gap-3 flex-wrap mb-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Eventos</h1>
          <p className="text-sm text-slate-500">Eventos abiertos a inscripciones.</p>
        </div>
      </div>

      <form onSubmit={onSearch} className="flex items-end gap-2 mb-6">
        <div className="flex-1">
          <Input
            label="Buscar"
            placeholder="Nombre del evento…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </div>
        <Button type="submit" variant="secondary">Buscar</Button>
        {activeQ && (
          <Button
            type="button"
            variant="ghost"
            onClick={() => {
              setQ('')
              setActiveQ('')
              setPage(1)
            }}
          >
            Limpiar
          </Button>
        )}
      </form>

      {loading && <Spinner />}
      {error && <p className="text-red-600 text-sm">{error}</p>}

      {!loading && !error && data && (
        <>
          {data.items.length === 0 ? (
            <p className="text-slate-500 text-sm py-12 text-center">
              {activeQ ? `No hay eventos que coincidan con "${activeQ}".` : 'Aún no hay eventos publicados.'}
            </p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {data.items.map((ev) => (
                <EventCard key={ev.id} event={ev} />
              ))}
            </div>
          )}
          <Pager page={data.page} size={data.size} total={data.total} onChange={setPage} />
        </>
      )}
    </div>
  )
}
