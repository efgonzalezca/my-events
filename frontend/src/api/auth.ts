import { api } from './client'
import type { User } from '../types'

export interface LoginResponse {
  access_token: string
  token_type: string
}

export const authApi = {
  register: (email: string, password: string, full_name: string) =>
    api.post<User>('/auth/register', { email, password, full_name }).then((r) => r.data),

  login: (email: string, password: string) =>
    api.post<LoginResponse>('/auth/login', { email, password }).then((r) => r.data),

  me: () => api.get<User>('/auth/me').then((r) => r.data),
}