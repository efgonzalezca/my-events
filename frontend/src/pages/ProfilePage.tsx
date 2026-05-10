import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { registrationsApi } from '../api/registrations'
import { useAuth } from '../auth/AuthContext'
import { Button } from '../components/Button'
import { Spinner } from '../components/Spinner'
import { describeError } from '../lib/errors'
import { formatDateRange } from '../lib/datetime'
import type { MyRegistrationItem } from '../types'

const ROLE_LABEL: Record<string, string> = {
  admin: 'Administrador',
  organizer: 'Organizador',
  attendee: 'Asistente',
}

export function ProfilePage() {
  const { user } = useAuth()
  const [items, setItems] = useState<MyRegistrationItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const list = await registrationsApi.mine()
      setItems(list)
      setError(null)
    } catch (err) {
      setError(describeError(err, 'No pudimos cargar tus inscripciones.'))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  if (!user) return null

  return (
    <div className="max-w-3xl mx-auto px-4 py-6">
      <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm">
        <h1 className="text-2xl font-bold text-slate-900">Mi perfil</h1>
        <dl className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
          <div>
            <dt className="text-slate-500">Nombre</dt>
            <dd className="text-slate-900">{user.full_name}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Correo</dt>
            <dd className="text-slate-900">{user.email}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Rol</dt>
            <dd className="text-slate-900">{ROLE_LABEL[user.role] ?? user.role}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Estado</dt>
            <dd className={user.is_active ? 'text-emerald-700' : 'text-red-700'}>
              {user.is_active ? 'Activo' : 'Inactivo'}
            </dd>
          </div>
        </dl>
      </div>

      <h2 className="mt-8 text-xl font-semibold text-slate-900">Mis inscripciones</h2>
      {loading && <Spinner />}
      {error && <p className="text-sm text-red-600">{error}</p>}
      {actionError && <p className="text-sm text-red-600 mt-2">{actionError}</p>}
      {!loading && !error && items.length === 0 && (
        <p className="text-sm text-slate-500 mt-3">
          Aún no estás inscrito a ningún evento.{' '}
          <Link to="/events" className="text-indigo-600 hover:underline">Explora eventos</Link>.
        </p>
      )}
      {!loading && items.length > 0 && (
        <ul className="mt-3 space-y-2">
          {items.map((it) => (
            <li
              key={it.registration_id}
              className="bg-white border border-slate-200 rounded-lg p-4 flex items-start justify-between gap-3 flex-wrap"
            >
              <div>
                <Link to={`/events/${it.event.id}`} className="font-medium text-slate-900 hover:text-indigo-700">
                  {it.event.name}
                </Link>
                <p className="text-xs text-slate-500">{it.event.location || 'Sin ubicación'}</p>
                <p className="text-sm text-slate-700 mt-1">{formatDateRange(it.event.starts_at, it.event.ends_at)}</p>
              </div>
              <Button
                variant="ghost"
                onClick={async () => {
                  if (!confirm('¿Cancelar tu inscripción?')) return
                  setActionError(null)
                  try {
                    await registrationsApi.cancel(it.event.id)
                    await load()
                  } catch (err) {
                    setActionError(describeError(err, 'No pudimos cancelar la inscripción.'))
                  }
                }}
              >
                Cancelar
              </Button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
