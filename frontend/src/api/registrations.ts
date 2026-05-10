import { api } from './client'
import type { MyRegistrationItem, Registration } from '../types'

export const registrationsApi = {
  register: (eventId: number) =>
    api.post<Registration>(`/events/${eventId}/register`).then((r) => r.data),

  cancel: (eventId: number) =>
    api.delete(`/events/${eventId}/register`).then(() => undefined),

  mine: () =>
    api.get<MyRegistrationItem[]>('/me/registrations').then((r) => r.data),
}
