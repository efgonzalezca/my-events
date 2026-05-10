import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { eventsApi } from '../api/events'
import { Button } from '../components/Button'
import { EventCard } from '../components/EventCard'
import { Spinner } from '../components/Spinner'
import { getMyEventIds, untrackMyEvent } from '../lib/myEvents'
import type { Event } from '../types'

export function MyEventsPage() {
  const [events, setEvents] = useState<Event[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const ids = getMyEventIds()
    if (ids.length === 0) {
      setEvents([])
      setLoading(false)
      return
    }
    Promise.allSettled(ids.map((id) => eventsApi.get(id)))
      .then((results) => {
        const ok: Event[] = []
        results.forEach((r, i) => {
          if (r.status === 'fulfilled') ok.push(r.value)
          else if (axios.isAxiosError(r.reason) && r.reason.response?.status === 404) {
            untrackMyEvent(ids[i])
          }
        })
        setEvents(ok.sort((a, b) => b.id - a.id))
      })
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      <div className="flex items-center justify-between gap-3 flex-wrap mb-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Mis eventos</h1>
          <p className="text-sm text-slate-500">Eventos creados desde este navegador (incluyendo borradores y cancelados).</p>
        </div>
        <Link to="/events/new"><Button>Crear evento</Button></Link>
      </div>

      {loading && <Spinner />}

      {!loading && events.length === 0 && (
        <p className="text-sm text-slate-500 py-12 text-center">
          Aún no has creado eventos. <Link to="/events/new" className="text-indigo-600 hover:underline">Crea el primero</Link>.
        </p>
      )}

      {!loading && events.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {events.map((ev) => (
            <EventCard key={ev.id} event={ev} />
          ))}
        </div>
      )}
    </div>
  )
}
