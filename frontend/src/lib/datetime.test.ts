import { describe, expect, it } from 'vitest'
import { fromLocalInput, toLocalInput, formatDateRange } from './datetime'

describe('datetime helpers', () => {
  it('toLocalInput returns the value <input type="datetime-local"> expects', () => {
    const iso = '2026-05-09T15:30:00.000Z'
    const local = toLocalInput(iso)
    expect(local).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/)
  })

  it('fromLocalInput converts a datetime-local string to ISO UTC', () => {
    const local = '2026-05-09T10:00'
    const iso = fromLocalInput(local)
    expect(iso).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/)
  })

  it('toLocalInput followed by fromLocalInput preserves the moment', () => {
    const iso = '2026-05-09T15:30:00.000Z'
    const roundtripped = fromLocalInput(toLocalInput(iso))
    expect(new Date(roundtripped).getTime()).toBe(new Date(iso).getTime())
  })

  it('toLocalInput returns empty string for empty input', () => {
    expect(toLocalInput('')).toBe('')
  })

  it('fromLocalInput returns empty string for empty input', () => {
    expect(fromLocalInput('')).toBe('')
  })

  it('treats backend naive timestamps as UTC (no 5h drift)', () => {
    const naive = '2026-05-09T15:30:00'
    const withZ = '2026-05-09T15:30:00Z'
    expect(toLocalInput(naive)).toBe(toLocalInput(withZ))
  })

  it('formatDateRange formats same-day events compactly', () => {
    const start = new Date('2026-05-09T10:00:00').toISOString()
    const end = new Date('2026-05-09T13:00:00').toISOString()
    const text = formatDateRange(start, end)
    expect(text).toContain('–')
  })

  it('formatDateRange handles cross-day ranges', () => {
    const start = new Date('2026-05-09T10:00:00').toISOString()
    const end = new Date('2026-05-10T13:00:00').toISOString()
    const text = formatDateRange(start, end)
    expect(text).toContain('→')
  })
})
