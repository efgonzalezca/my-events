import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { eventsApi } from '../api/events'
import { sessionsApi } from '../api/sessions'
import { registrationsApi } from '../api/registrations'
import { useAuth } from '../auth/AuthContext'
import { Button } from '../components/Button'
import { Spinner } from '../components/Spinner'
import { describeError } from '../lib/errors'
import { formatDateRange } from '../lib/datetime'
import type { Event, EventStatus, Session } from '../types'

const STATUS_LABEL: Record<EventStatus, string> = {
  draft: 'Borrador',
  published: 'Publicado',
  cancelled: 'Cancelado',
}

const STATUS_STYLE: Record<EventStatus, string> = {
  draft: 'bg-amber-100 text-amber-800',
  published: 'bg-emerald-100 text-emerald-800',
  cancelled: 'bg-slate-200 text-slate-600',
}

export function EventDetailPage() {
  const { id } = useParams<{ id: string }>()
  const eventId = Number(id)
  const { user } = useAuth()

  const [event, setEvent] = useState<Event | null>(null)
  const [sessions, setSessions] = useState<Session[]>([])
  const [registeredEventIds, setRegisteredEventIds] = useState<Set<number>>(new Set())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)

  const loadAll = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [ev, sess] = await Promise.all([
        eventsApi.get(eventId),
        sessionsApi.listOfEvent(eventId).catch(() => [] as Session[]),
      ])
      setEvent(ev)
      setSessions(sess)

      if (user) {
        try {
          const mine = await registrationsApi.mine()
          setRegisteredEventIds(new Set(mine.map((r) => r.event.id)))
        } catch {
          // silently ignore: detail still renders without registration state
        }
      } else {
        setRegisteredEventIds(new Set())
      }
    } catch (err) {
      setError(describeError(err, 'No pudimos cargar el evento.'))
    } finally {
      setLoading(false)
    }
  }, [eventId, user])

  useEffect(() => {
    if (Number.isFinite(eventId)) loadAll()
  }, [eventId, loadAll])

  if (!Number.isFinite(eventId)) return <p className="p-6 text-red-600">ID de evento inválido.</p>
  if (loading) return <Spinner />
  if (error) return <p className="p-6 text-red-600">{error}</p>
  if (!event) return null

  const isFull = event.registered_count >= event.capacity
  const isRegistered = registeredEventIds.has(event.id)
  const canRegister = !!user && event.status === 'published' && !isFull && !isRegistered

  const onRegister = async () => {
    setActionError(null)
    try {
      await registrationsApi.register(event.id)
      await loadAll()
    } catch (err) {
      setActionError(describeError(err, 'No pudimos registrar tu inscripción.'))
    }
  }

  const onCancel = async () => {
    if (!confirm('¿Cancelar tu inscripción?')) return
    setActionError(null)
    try {
      await registrationsApi.cancel(event.id)
      await loadAll()
    } catch (err) {
      setActionError(describeError(err, 'No pudimos cancelar tu inscripción.'))
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-6">
      <Link to="/events" className="text-sm text-indigo-600 hover:underline">← Volver a eventos</Link>
      <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm mt-3">
        <div className="flex items-start justify-between gap-3 flex-wrap">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">{event.name}</h1>
            <p className="text-sm text-slate-500 mt-1">{event.location || 'Sin ubicación'}</p>
          </div>
          <span className={`text-sm font-medium px-2 py-1 rounded ${STATUS_STYLE[event.status]}`}>
            {STATUS_LABEL[event.status]}
          </span>
        </div>

        <p className="text-slate-700 mt-3 whitespace-pre-wrap">{event.description || 'Sin descripción.'}</p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4 text-sm">
          <div className="bg-slate-50 rounded p-3">
            <div className="text-slate-500">Fecha</div>
            <div className="text-slate-900">{formatDateRange(event.starts_at, event.ends_at)}</div>
          </div>
          <div className="bg-slate-50 rounded p-3">
            <div className="text-slate-500">Cupo</div>
            <div className={`font-medium ${isFull ? 'text-red-600' : 'text-slate-900'}`}>
              {event.registered_count} / {event.capacity}
            </div>
          </div>
        </div>

        <div className="mt-5 flex flex-wrap gap-2 items-center">
          {!user && (
            <Link to="/login" className="text-sm text-indigo-600 hover:underline">
              Inicia sesión para inscribirte
            </Link>
          )}

          {user && event.status !== 'published' && (
            <p className="text-sm text-slate-500">Este evento no está abierto a inscripciones.</p>
          )}

          {user && event.status === 'published' && isFull && !isRegistered && (
            <Button disabled variant="secondary">Cupo lleno</Button>
          )}

          {canRegister && <Button onClick={onRegister}>Inscribirme</Button>}

          {user && isRegistered && (
            <Button variant="ghost" onClick={onCancel}>
              Cancelar inscripción
            </Button>
          )}
        </div>

        {actionError && <p className="mt-3 text-sm text-red-600">{actionError}</p>}
      </div>

      <section className="mt-6 bg-white border border-slate-200 rounded-lg p-6 shadow-sm">
        <h2 className="text-xl font-semibold text-slate-900">Sesiones</h2>
        {sessions.length === 0 ? (
          <p className="text-sm text-slate-500 mt-2">Este evento aún no tiene sesiones programadas.</p>
        ) : (
          <ul className="mt-3 space-y-3">
            {sessions.map((s) => (
              <li key={s.id} className="border border-slate-200 rounded p-3">
                <h3 className="font-medium text-slate-900">{s.title}</h3>
                <p className="text-xs text-slate-500">{formatDateRange(s.starts_at, s.ends_at)}</p>
                {s.description && (
                  <p className="text-sm text-slate-700 mt-2 whitespace-pre-wrap">{s.description}</p>
                )}
                <p className="text-sm text-slate-600 mt-2">
                  <span className="text-slate-500">Ponentes: </span>
                  {s.speaker_ids.length > 0
                    ? s.speaker_ids.map((spid) => `#${spid}`).join(', ')
                    : <span className="italic text-slate-400">ninguno asignado</span>}
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
