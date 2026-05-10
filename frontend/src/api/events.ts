import { api } from './client'
import type { Event, Page } from '../types'

export interface EventCreatePayload {
  name: string
  description: string
  location: string
  starts_at: string
  ends_at: string
  capacity: number
}

export type EventUpdatePayload = Partial<EventCreatePayload>

export const eventsApi = {
  list: (params: { q?: string; page?: number; size?: number } = {}) =>
    api.get<Page<Event>>('/events', { params }).then((r) => r.data),

  get: (id: number) => api.get<Event>(`/events/${id}`).then((r) => r.data),

  create: (payload: EventCreatePayload) =>
    api.post<Event>('/events', payload).then((r) => r.data),

  update: (id: number, payload: EventUpdatePayload) =>
    api.patch<Event>(`/events/${id}`, payload).then((r) => r.data),

  publish: (id: number) =>
    api.post<Event>(`/events/${id}/publish`).then((r) => r.data),

  cancel: (id: number) =>
    api.post<Event>(`/events/${id}/cancel`).then((r) => r.data),

  remove: (id: number) => api.delete(`/events/${id}`).then(() => undefined),
}
