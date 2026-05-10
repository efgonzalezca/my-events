import { useCallback, useEffect, useState } from 'react'
import { adminApi } from '../api/admin'
import { useAuth } from '../auth/AuthContext'
import { Pager } from '../components/Pager'
import { Spinner } from '../components/Spinner'
import { useToast } from '../components/Toast'
import { describeError } from '../lib/errors'
import { formatDateTime } from '../lib/datetime'
import type { AdminUser, Page, UserRole } from '../types'

const PAGE_SIZE = 20

const ROLES: UserRole[] = ['attendee', 'organizer', 'admin']

const ROLE_LABEL: Record<UserRole, string> = {
  admin: 'Administrador',
  organizer: 'Organizador',
  attendee: 'Asistente',
}

const ROLE_DOT: Record<UserRole, string> = {
  admin: 'bg-violet-500',
  organizer: 'bg-indigo-500',
  attendee: 'bg-slate-400',
}

interface RoleSelectProps {
  value: UserRole
  disabled: boolean
  onChange: (next: UserRole) => void
}

function RoleSelect({ value, disabled, onChange }: RoleSelectProps) {
  return (
    <div className="relative inline-block">
      <span
        aria-hidden
        className={`pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 h-2 w-2 rounded-full ${ROLE_DOT[value]}`}
      />
      <select
        value={value}
        disabled={disabled}
        onChange={(e) => onChange(e.target.value as UserRole)}
        className="appearance-none rounded-md border border-slate-300 bg-white pl-7 pr-9 py-1.5 text-sm font-medium text-slate-800 shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 hover:border-slate-400 disabled:bg-slate-50 disabled:text-slate-500 disabled:cursor-not-allowed transition-colors"
      >
        {ROLES.map((r) => (
          <option key={r} value={r}>{ROLE_LABEL[r]}</option>
        ))}
      </select>
      <svg
        aria-hidden
        viewBox="0 0 20 20"
        fill="currentColor"
        className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400"
      >
        <path
          fillRule="evenodd"
          d="M5.23 7.21a.75.75 0 011.06.02L10 11.06l3.71-3.83a.75.75 0 111.08 1.04l-4.25 4.39a.75.75 0 01-1.08 0L5.21 8.27a.75.75 0 01.02-1.06z"
          clipRule="evenodd"
        />
      </svg>
    </div>
  )
}

interface ActiveSwitchProps {
  checked: boolean
  disabled: boolean
  pending: boolean
  onChange: () => void
  label: string
}

function ActiveSwitch({ checked, disabled, pending, onChange, label }: ActiveSwitchProps) {
  return (
    <div className="flex items-center gap-2">
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        aria-label={label}
        disabled={disabled}
        onClick={onChange}
        className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed ${
          checked ? 'bg-emerald-500 hover:bg-emerald-600' : 'bg-slate-300 hover:bg-slate-400'
        }`}
      >
        <span
          aria-hidden
          className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition-transform ${
            checked ? 'translate-x-5' : 'translate-x-0.5'
          } ${pending ? 'animate-pulse' : ''}`}
        />
      </button>
      <span className={`text-xs font-medium ${checked ? 'text-emerald-700' : 'text-slate-500'}`}>
        {checked ? 'Activo' : 'Inactivo'}
      </span>
    </div>
  )
}

export function AdminUsersPage() {
  const { user } = useAuth()
  const toast = useToast()
  const [data, setData] = useState<Page<AdminUser> | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [pendingId, setPendingId] = useState<number | null>(null)
  const [page, setPage] = useState(1)

  const load = useCallback(() => {
    setLoading(true)
    adminApi
      .listUsers({ page, size: PAGE_SIZE })
      .then((res) => {
        setData(res)
        setError(null)
      })
      .catch((err) => setError(describeError(err, 'No pudimos cargar los usuarios.')))
      .finally(() => setLoading(false))
  }, [page])

  useEffect(() => {
    load()
  }, [load])

  const updateRow = (next: AdminUser) => {
    setData((cur) =>
      cur ? { ...cur, items: cur.items.map((u) => (u.id === next.id ? next : u)) } : cur,
    )
  }

  const onChangeRole = async (target: AdminUser, role: UserRole) => {
    if (role === target.role) return
    setPendingId(target.id)
    try {
      const updated = await adminApi.changeRole(target.id, role)
      updateRow(updated)
      toast.success(`${target.full_name} ahora es ${ROLE_LABEL[role].toLowerCase()}.`)
    } catch (err) {
      toast.error(describeError(err, 'No pudimos cambiar el rol.'))
    } finally {
      setPendingId(null)
    }
  }

  const onToggleActive = async (target: AdminUser) => {
    const next = !target.is_active
    setPendingId(target.id)
    try {
      const updated = await adminApi.setActive(target.id, next)
      updateRow(updated)
      toast.info(`${target.full_name} ${next ? 'reactivado' : 'desactivado'}.`)
    } catch (err) {
      toast.error(describeError(err, 'No pudimos cambiar el estado.'))
    } finally {
      setPendingId(null)
    }
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-slate-900">Usuarios</h1>
        <p className="text-sm text-slate-500">
          Solo los administradores pueden cambiar el rol o el estado de otros usuarios.
        </p>
      </div>

      {loading && <Spinner />}
      {error && <p className="text-sm text-red-600">{error}</p>}

      {!loading && !error && data && (
        <>
          {data.items.length === 0 ? (
            <p className="text-sm text-slate-500 py-12 text-center">No hay usuarios para mostrar.</p>
          ) : (
            <div className="overflow-x-auto bg-white border border-slate-200 rounded-lg shadow-sm">
              <table className="min-w-full text-sm">
                <thead className="bg-slate-50 text-slate-600 text-xs uppercase tracking-wide">
                  <tr>
                    <th className="text-left font-semibold px-4 py-3">Usuario</th>
                    <th className="text-left font-semibold px-4 py-3">Rol</th>
                    <th className="text-left font-semibold px-4 py-3">Estado</th>
                    <th className="text-left font-semibold px-4 py-3">Creado</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {data.items.map((u) => {
                    const isSelf = !!user && user.id === u.id
                    const pending = pendingId === u.id
                    const disabled = isSelf || pending
                    return (
                      <tr key={u.id} className={`${isSelf ? 'bg-slate-50' : 'hover:bg-slate-50'} transition-colors`}>
                        <td className="px-4 py-3 align-middle">
                          <div className="font-medium text-slate-900">
                            {u.full_name}
                            {isSelf && <span className="ml-2 text-xs font-normal text-slate-400">(tú)</span>}
                          </div>
                          <div className="text-xs text-slate-500">{u.email}</div>
                        </td>
                        <td className="px-4 py-3 align-middle">
                          <RoleSelect
                            value={u.role}
                            disabled={disabled}
                            onChange={(next) => onChangeRole(u, next)}
                          />
                        </td>
                        <td className="px-4 py-3 align-middle">
                          <ActiveSwitch
                            checked={u.is_active}
                            disabled={disabled}
                            pending={pending}
                            label={u.is_active ? `Desactivar ${u.full_name}` : `Reactivar ${u.full_name}`}
                            onChange={() => onToggleActive(u)}
                          />
                        </td>
                        <td className="px-4 py-3 align-middle text-slate-500 text-xs whitespace-nowrap">
                          {formatDateTime(u.created_at)}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
          <Pager page={data.page} size={data.size} total={data.total} onChange={setPage} />
        </>
      )}
    </div>
  )
}
