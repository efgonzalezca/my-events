import { useCallback, useEffect, useMemo, useState, type FormEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { eventsApi } from '../api/events'
import { sessionsApi } from '../api/sessions'
import { speakersApi } from '../api/speakers'
import { registrationsApi } from '../api/registrations'
import { useAuth } from '../auth/AuthContext'
import { Button } from '../components/Button'
import { Input } from '../components/Input'
import { TextArea } from '../components/TextArea'
import { Spinner } from '../components/Spinner'
import { useToast } from '../components/Toast'
import { untrackMyEvent } from '../lib/myEvents'
import { describeError } from '../lib/errors'
import { formatDateRange, fromLocalInput, toLocalInput } from '../lib/datetime'
import type { Event, EventStatus, Session, Speaker } from '../types'

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
  const navigate = useNavigate()
  const { user } = useAuth()
  const toast = useToast()

  const [event, setEvent] = useState<Event | null>(null)
  const [sessions, setSessions] = useState<Session[]>([])
  const [speakers, setSpeakers] = useState<Speaker[]>([])
  const [registeredEventIds, setRegisteredEventIds] = useState<Set<number>>(new Set())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const isOwner = !!user && !!event && (user.id === event.organizer_id || user.role === 'admin')

  const loadAll = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [ev, sess, sps] = await Promise.all([
        eventsApi.get(eventId),
        sessionsApi.listOfEvent(eventId).catch(() => [] as Session[]),
        speakersApi.list({ size: 100 }).catch(() => ({ items: [] as Speaker[], page: 1, size: 100, total: 0 })),
      ])
      setEvent(ev)
      setSessions(sess)
      setSpeakers(sps.items)

      if (user) {
        try {
          const mine = await registrationsApi.mine()
          setRegisteredEventIds(new Set(mine.map((r) => r.event.id)))
        } catch {
          // ignore: detail still renders without registration state
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

  const speakerById = useMemo(() => new Map(speakers.map((s) => [s.id, s])), [speakers])

  if (!Number.isFinite(eventId)) return <p className="p-6 text-red-600">ID de evento inválido.</p>
  if (loading) return <Spinner />
  if (error) return <p className="p-6 text-red-600">{error}</p>
  if (!event) return null

  const isFull = event.registered_count >= event.capacity
  const isRegistered = registeredEventIds.has(event.id)
  const canRegister = !!user && event.status === 'published' && !isFull && !isRegistered

  const runTransition = async (
    fn: () => Promise<void>,
    okMessage: string,
    okKind: 'success' | 'info' = 'success',
  ) => {
    try {
      await fn()
      toast[okKind](okMessage)
    } catch (err) {
      toast.error(describeError(err))
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

          {user && event.status !== 'published' && !isOwner && (
            <p className="text-sm text-slate-500">Este evento no está abierto a inscripciones.</p>
          )}

          {user && event.status === 'published' && isFull && !isRegistered && (
            <Button disabled variant="secondary">Cupo lleno</Button>
          )}

          {canRegister && (
            <Button
              onClick={() =>
                runTransition(async () => {
                  await registrationsApi.register(event.id)
                  await loadAll()
                }, '¡Inscripción confirmada!')
              }
            >
              Inscribirme
            </Button>
          )}

          {user && isRegistered && (
            <Button
              variant="ghost"
              onClick={() => {
                if (!confirm('¿Cancelar tu inscripción?')) return
                runTransition(async () => {
                  await registrationsApi.cancel(event.id)
                  await loadAll()
                }, 'Inscripción cancelada.', 'info')
              }}
            >
              Cancelar inscripción
            </Button>
          )}

          {isOwner && event.status === 'draft' && (
            <>
              <Link to={`/events/${event.id}/edit`}>
                <Button variant="secondary">Editar</Button>
              </Link>
              <Button
                onClick={() =>
                  runTransition(async () => {
                    const updated = await eventsApi.publish(event.id)
                    setEvent(updated)
                  }, 'Evento publicado: borrador → publicado.')
                }
              >
                Publicar
              </Button>
            </>
          )}

          {isOwner && (event.status === 'draft' || event.status === 'published') && (
            <Button
              variant="danger"
              onClick={() => {
                if (!confirm('¿Cancelar este evento? No podrá reabrirse.')) return
                runTransition(async () => {
                  const updated = await eventsApi.cancel(event.id)
                  setEvent(updated)
                }, `Evento cancelado: ${STATUS_LABEL[event.status].toLowerCase()} → cancelado.`, 'info')
              }}
            >
              Cancelar evento
            </Button>
          )}

          {isOwner && (event.status === 'draft' || event.status === 'cancelled') && (
            <Button
              variant="ghost"
              onClick={async () => {
                if (!confirm('¿Eliminar este evento? No se puede deshacer.')) return
                try {
                  await eventsApi.remove(event.id)
                  untrackMyEvent(event.id)
                  toast.info('Evento eliminado.')
                  navigate('/me/events')
                } catch (err) {
                  toast.error(describeError(err))
                }
              }}
            >
              Eliminar
            </Button>
          )}
        </div>
      </div>

      <SessionsBlock
        event={event}
        sessions={sessions}
        speakers={speakers}
        speakerById={speakerById}
        canManage={isOwner}
        onRefresh={loadAll}
      />
    </div>
  )
}

interface SessionsBlockProps {
  event: Event
  sessions: Session[]
  speakers: Speaker[]
  speakerById: Map<number, Speaker>
  canManage: boolean
  onRefresh: () => void
}

function SessionsBlock({ event, sessions, speakers, speakerById, canManage, onRefresh }: SessionsBlockProps) {
  return (
    <section className="mt-6 bg-white border border-slate-200 rounded-lg p-6 shadow-sm">
      <h2 className="text-xl font-semibold text-slate-900">Sesiones</h2>

      {sessions.length === 0 && (
        <p className="text-sm text-slate-500 mt-2">Este evento aún no tiene sesiones programadas.</p>
      )}

      <ul className="mt-3 space-y-3">
        {sessions.map((s) => (
          <SessionItem
            key={s.id}
            session={s}
            speakers={speakers}
            speakerById={speakerById}
            canManage={canManage}
            onRefresh={onRefresh}
          />
        ))}
      </ul>

      {canManage && <NewSessionForm event={event} onCreated={onRefresh} />}
    </section>
  )
}

interface SessionItemProps {
  session: Session
  speakers: Speaker[]
  speakerById: Map<number, Speaker>
  canManage: boolean
  onRefresh: () => void
}

function SessionItem({ session, speakers, speakerById, canManage, onRefresh }: SessionItemProps) {
  const toast = useToast()
  const [pendingSpeakerId, setPendingSpeakerId] = useState<number | ''>('')

  const linkedNames = session.speaker_ids
    .map((id) => speakerById.get(id)?.name ?? `#${id}`)
    .join(', ')

  const availableSpeakers = speakers.filter((sp) => !session.speaker_ids.includes(sp.id))

  return (
    <li className="border border-slate-200 rounded p-3">
      <div className="flex items-start justify-between gap-2 flex-wrap">
        <div>
          <h3 className="font-medium text-slate-900">{session.title}</h3>
          <p className="text-xs text-slate-500">{formatDateRange(session.starts_at, session.ends_at)}</p>
        </div>
        {canManage && (
          <Button
            variant="ghost"
            onClick={async () => {
              if (!confirm('¿Eliminar esta sesión?')) return
              try {
                await sessionsApi.remove(session.id)
                toast.info(`Sesión "${session.title}" eliminada.`)
                onRefresh()
              } catch (err) {
                toast.error(describeError(err))
              }
            }}
          >
            Eliminar
          </Button>
        )}
      </div>
      {session.description && <p className="text-sm text-slate-700 mt-2 whitespace-pre-wrap">{session.description}</p>}
      <p className="text-sm text-slate-600 mt-2">
        <span className="text-slate-500">Ponentes: </span>
        {linkedNames || <span className="italic text-slate-400">ninguno asignado</span>}
      </p>
      {canManage && (
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <select
            className="rounded-md border border-slate-300 px-2 py-1 text-sm"
            value={pendingSpeakerId}
            onChange={(e) => setPendingSpeakerId(e.target.value === '' ? '' : Number(e.target.value))}
          >
            <option value="">Asignar ponente…</option>
            {availableSpeakers.map((sp) => (
              <option key={sp.id} value={sp.id}>{sp.name}</option>
            ))}
          </select>
          <Button
            variant="secondary"
            disabled={pendingSpeakerId === ''}
            onClick={async () => {
              if (pendingSpeakerId === '') return
              const speaker = speakerById.get(pendingSpeakerId)
              try {
                await sessionsApi.linkSpeaker(session.id, pendingSpeakerId)
                setPendingSpeakerId('')
                toast.success(`${speaker?.name ?? 'Ponente'} asignado a "${session.title}".`)
                onRefresh()
              } catch (err) {
                toast.error(describeError(err))
              }
            }}
          >
            Asignar
          </Button>
          {session.speaker_ids.length > 0 && (
            <div className="flex flex-wrap gap-1 ml-2">
              {session.speaker_ids.map((spid) => (
                <button
                  key={spid}
                  type="button"
                  className="text-xs bg-slate-100 hover:bg-red-100 hover:text-red-700 text-slate-700 px-2 py-1 rounded"
                  onClick={async () => {
                    const name = speakerById.get(spid)?.name ?? `#${spid}`
                    try {
                      await sessionsApi.unlinkSpeaker(session.id, spid)
                      toast.info(`${name} retirado de "${session.title}".`)
                      onRefresh()
                    } catch (err) {
                      toast.error(describeError(err))
                    }
                  }}
                >
                  Quitar {speakerById.get(spid)?.name ?? `#${spid}`} ✕
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </li>
  )
}

function NewSessionForm({ event, onCreated }: { event: Event; onCreated: () => void }) {
  const toast = useToast()
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [startsAt, setStartsAt] = useState('')
  const [endsAt, setEndsAt] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const eventStartLocal = toLocalInput(event.starts_at)
  const eventEndLocal = toLocalInput(event.ends_at)

  const validateRange = (): string | null => {
    if (!startsAt || !endsAt) return null
    const sStart = new Date(startsAt).getTime()
    const sEnd = new Date(endsAt).getTime()
    const eStart = new Date(event.starts_at).getTime()
    const eEnd = new Date(event.ends_at).getTime()
    if (sEnd <= sStart) return 'La hora de fin debe ser posterior a la de inicio.'
    if (sStart < eStart || sEnd > eEnd) {
      return `La sesión debe estar entre ${formatDateRange(event.starts_at, event.ends_at)}.`
    }
    return null
  }

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    const rangeErr = validateRange()
    if (rangeErr) {
      setError(rangeErr)
      return
    }
    setSubmitting(true)
    try {
      const created = await sessionsApi.create(event.id, {
        title,
        description,
        starts_at: fromLocalInput(startsAt),
        ends_at: fromLocalInput(endsAt),
      })
      toast.success(`Sesión "${created.title}" creada.`)
      setTitle('')
      setDescription('')
      setStartsAt('')
      setEndsAt('')
      onCreated()
    } catch (err) {
      const msg = describeError(err, 'No pudimos crear la sesión.')
      setError(msg)
      toast.error(msg)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={onSubmit} className="mt-5 border-t border-slate-200 pt-5 grid grid-cols-1 sm:grid-cols-2 gap-3">
      <div className="sm:col-span-2">
        <h3 className="font-medium text-slate-900">Nueva sesión</h3>
        <p className="text-xs text-slate-500">
          Debe estar dentro del rango del evento ({formatDateRange(event.starts_at, event.ends_at)}) y no
          solaparse con otras.
        </p>
      </div>
      <Input
        label="Título"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
        minLength={1}
      />
      <Input
        label="Inicio"
        type="datetime-local"
        value={startsAt}
        onChange={(e) => setStartsAt(e.target.value)}
        required
        min={eventStartLocal}
        max={eventEndLocal}
      />
      <Input
        label="Fin"
        type="datetime-local"
        value={endsAt}
        onChange={(e) => setEndsAt(e.target.value)}
        required
        min={startsAt || eventStartLocal}
        max={eventEndLocal}
      />
      <div className="sm:col-span-2">
        <TextArea
          label="Descripción (opcional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>
      {error && <p className="sm:col-span-2 text-sm text-red-600">{error}</p>}
      <div className="sm:col-span-2">
        <Button type="submit" disabled={submitting}>
          {submitting ? 'Creando…' : 'Crear sesión'}
        </Button>
      </div>
    </form>
  )
}
