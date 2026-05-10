import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { speakersApi } from '../api/speakers'
import { useAuth } from '../auth/AuthContext'
import { Button } from '../components/Button'
import { Input } from '../components/Input'
import { Pager } from '../components/Pager'
import { Spinner } from '../components/Spinner'
import { useToast } from '../components/Toast'
import { describeError } from '../lib/errors'
import type { Page, Speaker } from '../types'

const PAGE_SIZE = 12

export function SpeakersPage() {
  const { user } = useAuth()
  const toast = useToast()
  const canManage = !!user && (user.role === 'organizer' || user.role === 'admin')
  const [data, setData] = useState<Page<Speaker> | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [q, setQ] = useState('')
  const [activeQ, setActiveQ] = useState('')
  const [page, setPage] = useState(1)

  const load = useCallback(() => {
    setLoading(true)
    speakersApi
      .list({ q: activeQ || undefined, page, size: PAGE_SIZE })
      .then((res) => {
        setData(res)
        setError(null)
      })
      .catch((err) => setError(describeError(err, 'No pudimos cargar los ponentes.')))
      .finally(() => setLoading(false))
  }, [activeQ, page])

  useEffect(() => {
    load()
  }, [load])

  const onSearch = (e: FormEvent) => {
    e.preventDefault()
    setPage(1)
    setActiveQ(q.trim())
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      <div className="flex items-center justify-between gap-3 flex-wrap mb-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Ponentes</h1>
          <p className="text-sm text-slate-500">Personas que pueden estar asignadas a las sesiones.</p>
        </div>
        {canManage && (
          <Link to="/speakers/new">
            <Button>Nuevo ponente</Button>
          </Link>
        )}
      </div>

      <form onSubmit={onSearch} className="flex items-end gap-2 mb-6">
        <div className="flex-1">
          <Input
            label="Buscar"
            placeholder="Nombre del ponente…"
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
      {error && <p className="text-sm text-red-600">{error}</p>}

      {!loading && !error && data && (
        <>
          {data.items.length === 0 ? (
            <p className="text-sm text-slate-500 py-12 text-center">No hay ponentes para mostrar.</p>
          ) : (
            <ul className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {data.items.map((sp) => (
                <li key={sp.id} className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm flex gap-3">
                  {sp.photo_url ? (
                    <img
                      src={sp.photo_url}
                      alt=""
                      className="h-14 w-14 rounded-full object-cover bg-slate-100"
                      onError={(e) => {
                        e.currentTarget.style.display = 'none'
                      }}
                    />
                  ) : (
                    <div className="h-14 w-14 rounded-full bg-slate-200 flex items-center justify-center text-slate-500 font-bold">
                      {sp.name.charAt(0).toUpperCase()}
                    </div>
                  )}
                  <div className="min-w-0 flex-1">
                    <h3 className="font-medium text-slate-900 truncate">{sp.name}</h3>
                    {sp.bio && <p className="text-sm text-slate-600 mt-1 line-clamp-3">{sp.bio}</p>}
                    {canManage && (
                      <div className="mt-2 flex gap-2">
                        <Link to={`/speakers/${sp.id}/edit`} className="text-xs text-indigo-600 hover:underline">
                          Editar
                        </Link>
                        <button
                          type="button"
                          className="text-xs text-red-600 hover:underline"
                          onClick={async () => {
                            if (!confirm(`¿Eliminar al ponente "${sp.name}"?`)) return
                            try {
                              await speakersApi.remove(sp.id)
                              toast.info(`Ponente "${sp.name}" eliminado.`)
                              load()
                            } catch (err) {
                              toast.error(describeError(err, 'No pudimos eliminar el ponente.'))
                            }
                          }}
                        >
                          Eliminar
                        </button>
                      </div>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
          <Pager page={data.page} size={data.size} total={data.total} onChange={setPage} />
        </>
      )}
    </div>
  )
}
