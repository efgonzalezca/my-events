/** Convert a value from <input type="datetime-local"> to an ISO UTC string. */
export function fromLocalInput(local: string): string {
  if (!local) return ''
  return new Date(local).toISOString()
}

/** Convert an ISO datetime string to the format expected by <input type="datetime-local">. */
export function toLocalInput(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

const DATE_FMT = new Intl.DateTimeFormat('es-CO', {
  day: 'numeric',
  month: 'short',
  year: 'numeric',
})
const TIME_FMT = new Intl.DateTimeFormat('es-CO', {
  hour: '2-digit',
  minute: '2-digit',
})

export function formatDateTime(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  return `${DATE_FMT.format(d)} · ${TIME_FMT.format(d)}`
}

export function formatDateRange(startIso: string, endIso: string): string {
  if (!startIso || !endIso) return ''
  const a = new Date(startIso)
  const b = new Date(endIso)
  const sameDay = a.toDateString() === b.toDateString()
  if (sameDay) {
    return `${DATE_FMT.format(a)} · ${TIME_FMT.format(a)} – ${TIME_FMT.format(b)}`
  }
  return `${formatDateTime(startIso)} → ${formatDateTime(endIso)}`
}
