import { useEffect, useState, type FormEvent } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { eventsApi, type EventCreatePayload, type EventUpdatePayload } from '../api/events'
import { Button } from '../components/Button'
import { Input } from '../components/Input'
import { TextArea } from '../components/TextArea'
import { Spinner } from '../components/Spinner'
import { fromLocalInput, toLocalInput } from '../lib/datetime'
import { describeError } from '../lib/errors'
import { trackMyEvent } from '../lib/myEvents'

export function EventFormPage() {
  const { id } = useParams<{ id: string }>()
  const isEdit = !!id
  const eventId = id ? Number(id) : null
  const navigate = useNavigate()

  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [location, setLocation] = useState('')
  const [startsAt, setStartsAt] = useState('')
  const [endsAt, setEndsAt] = useState('')
  const [capacity, setCapacity] = useState<number>(50)
  const [loading, setLoading] = useState(isEdit)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [info, setInfo] = useState<string | null>(null)

  useEffect(() => {
    if (!isEdit || eventId === null) return
    eventsApi
      .get(eventId)
      .then((ev) => {
        setName(ev.name)
        setDescription(ev.description)
        setLocation(ev.location)
        setStartsAt(toLocalInput(ev.starts_at))
        setEndsAt(toLocalInput(ev.ends_at))
        setCapacity(ev.capacity)
      })
      .catch((err) => setError(describeError(err, 'No pudimos cargar el evento.')))
      .finally(() => setLoading(false))
  }, [isEdit, eventId])

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setInfo(null)
    if (new Date(endsAt) <= new Date(startsAt)) {
      setError('La fecha de fin debe ser posterior a la de inicio.')
      return
    }
    setSubmitting(true)
    try {
      const payload: EventCreatePayload = {
        name,
        description,
        location,
        starts_at: fromLocalInput(startsAt),
        ends_at: fromLocalInput(endsAt),
        capacity,
      }
      if (isEdit && eventId !== null) {
        const partial: EventUpdatePayload = payload
        await eventsApi.update(eventId, partial)
        setInfo('Cambios guardados.')
      } else {
        const created = await eventsApi.create(payload)
        trackMyEvent(created.id)
        navigate(`/events/${created.id}`)
      }
    } catch (err) {
      setError(describeError(err, 'No pudimos guardar el evento.'))
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <Spinner />

  return (
    <div className="max-w-2xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold text-slate-900 mb-1">
        {isEdit ? 'Editar evento' : 'Nuevo evento'}
      </h1>
      <p className="text-sm text-slate-500 mb-5">
        {isEdit
          ? 'Solo se pueden editar eventos en estado borrador.'
          : 'El evento se crea en estado borrador. Publícalo cuando esté listo.'}
      </p>
      <form onSubmit={onSubmit} className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm flex flex-col gap-4">
        <Input
          label="Nombre"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          minLength={1}
          maxLength={255}
        />
        <TextArea
          label="Descripción"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          maxLength={4000}
        />
        <Input
          label="Ubicación"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          maxLength={255}
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <Input
            label="Inicio"
            type="datetime-local"
            value={startsAt}
            onChange={(e) => setStartsAt(e.target.value)}
            required
          />
          <Input
            label="Fin"
            type="datetime-local"
            value={endsAt}
            onChange={(e) => setEndsAt(e.target.value)}
            required
          />
        </div>
        <Input
          label="Capacidad"
          type="number"
          value={capacity}
          onChange={(e) => setCapacity(Number(e.target.value))}
          min={1}
          max={1_000_000}
          required
        />
        {error && <p className="text-sm text-red-600">{error}</p>}
        {info && <p className="text-sm text-emerald-700">{info}</p>}
        <div className="flex gap-2">
          <Button type="submit" disabled={submitting}>
            {submitting ? 'Guardando…' : isEdit ? 'Guardar cambios' : 'Crear evento'}
          </Button>
          <Button type="button" variant="ghost" onClick={() => navigate(-1)}>
            Cancelar
          </Button>
        </div>
      </form>
    </div>
  )
}
