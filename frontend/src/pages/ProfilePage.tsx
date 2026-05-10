import { useAuth } from '../auth/AuthContext'

const ROLE_LABEL: Record<string, string> = {
  admin: 'Administrador',
  organizer: 'Organizador',
  attendee: 'Asistente',
}

export function ProfilePage() {
  const { user } = useAuth()
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
    </div>
  )
}
