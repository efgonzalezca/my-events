const KEY = 'mevt_my_event_ids'

export function getMyEventIds(): number[] {
  const raw = localStorage.getItem(KEY)
  if (!raw) return []
  try {
    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) return []
    return parsed.filter((n) => Number.isFinite(n))
  } catch {
    return []
  }
}

function save(ids: number[]) {
  localStorage.setItem(KEY, JSON.stringify(ids))
}

export function trackMyEvent(id: number) {
  const ids = getMyEventIds()
  if (!ids.includes(id)) save([id, ...ids])
}

export function untrackMyEvent(id: number) {
  save(getMyEventIds().filter((x) => x !== id))
}
