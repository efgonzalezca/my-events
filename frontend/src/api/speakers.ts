import { api } from './client'
import type { Page, Speaker } from '../types'

export interface SpeakerPayload {
  name: string
  bio: string
  photo_url: string
}

export const speakersApi = {
  list: (params: { q?: string; page?: number; size?: number } = {}) =>
    api.get<Page<Speaker>>('/speakers', { params }).then((r) => r.data),

  get: (id: number) => api.get<Speaker>(`/speakers/${id}`).then((r) => r.data),

  create: (payload: SpeakerPayload) =>
    api.post<Speaker>('/speakers', payload).then((r) => r.data),

  update: (id: number, payload: Partial<SpeakerPayload>) =>
    api.patch<Speaker>(`/speakers/${id}`, payload).then((r) => r.data),

  remove: (id: number) => api.delete(`/speakers/${id}`).then(() => undefined),
}
