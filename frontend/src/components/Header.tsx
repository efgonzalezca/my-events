import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { Button } from './Button'

const ROLE_LABEL: Record<string, string> = {
  admin: 'Admin',
  organizer: 'Organizador',
  attendee: 'Asistente',
}

const navItem = ({ isActive }: { isActive: boolean }) =>
  `px-3 py-2 rounded text-sm font-medium ${isActive ? 'bg-indigo-100 text-indigo-700' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'}`

export function Header() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <header className="sticky top-0 z-10 bg-white border-b border-slate-200">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between gap-3">
        <Link to="/events" className="text-lg font-bold text-indigo-700 whitespace-nowrap">
          My Events
        </Link>
        <nav className="hidden sm:flex items-center gap-1">
          <NavLink to="/events" className={navItem}>Eventos</NavLink>
          {user && <NavLink to="/profile" className={navItem}>Mi perfil</NavLink>}
        </nav>
        <div className="flex items-center gap-2">
          {user ? (
            <>
              <span className="hidden md:inline text-sm text-slate-600">
                {user.full_name} <span className="text-xs text-slate-400">({ROLE_LABEL[user.role] ?? user.role})</span>
              </span>
              <Button
                variant="ghost"
                onClick={() => {
                  logout()
                  navigate('/login')
                }}
              >
                Salir
              </Button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-sm font-medium text-slate-700 hover:text-slate-900">Entrar</Link>
              <Link to="/register">
                <Button variant="primary">Registrarme</Button>
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
