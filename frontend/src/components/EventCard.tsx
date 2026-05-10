import { Link } from 'react-router-dom'
import type { Event, EventStatus } from '../types'
import { formatDateRange } from '../lib/datetime'

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

export function EventCard({ event }: { event: Event }) {
  const full = event.registered_count >= event.capacity
  return (
    <Link
      to={`/events/${event.id}`}
      className="block rounded-lg border border-slate-200 bg-white p-5 shadow-sm hover:shadow-md hover:border-indigo-300 transition"
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-semibold text-slate-900 text-lg leading-tight">{event.name}</h3>
        <span className={`text-xs font-medium px-2 py-1 rounded ${STATUS_STYLE[event.status]}`}>
          {STATUS_LABEL[event.status]}
        </span>
      </div>
      <p className="text-sm text-slate-500 mt-1">{event.location || 'Sin ubicación'}</p>
      <p className="text-sm text-slate-700 mt-2">{formatDateRange(event.starts_at, event.ends_at)}</p>
      <div className="mt-3 flex items-center justify-between text-sm">
        <span className={full ? 'text-red-600 font-medium' : 'text-slate-600'}>
          {event.registered_count} / {event.capacity} inscritos
        </span>
        {full && <span className="text-xs uppercase font-bold text-red-600">Lleno</span>}
      </div>
    </Link>
  )
}
