import { api } from './client'
import type { Session } from '../types'

export interface SessionCreatePayload {
  title: string
  description: string
  starts_at: string
  ends_at: string
}

export type SessionUpdatePayload = Partial<SessionCreatePayload>

export const sessionsApi = {
  listOfEvent: (eventId: number) =>
    api.get<Session[]>(`/events/${eventId}/sessions`).then((r) => r.data),

  get: (id: number) => api.get<Session>(`/sessions/${id}`).then((r) => r.data),

  create: (eventId: number, payload: SessionCreatePayload) =>
    api.post<Session>(`/events/${eventId}/sessions`, payload).then((r) => r.data),

  update: (id: number, payload: SessionUpdatePayload) =>
    api.patch<Session>(`/sessions/${id}`, payload).then((r) => r.data),

  remove: (id: number) => api.delete(`/sessions/${id}`).then(() => undefined),

  linkSpeaker: (sessionId: number, speakerId: number) =>
    api
      .post<Session>(`/sessions/${sessionId}/speakers/${speakerId}`)
      .then((r) => r.data),

  unlinkSpeaker: (sessionId: number, speakerId: number) =>
    api
      .delete(`/sessions/${sessionId}/speakers/${speakerId}`)
      .then(() => undefined),
}
