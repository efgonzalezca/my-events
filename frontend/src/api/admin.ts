import { api } from './client'
import type { AdminUser, Page, UserRole } from '../types'

export const adminApi = {
  listUsers: (params: { page?: number; size?: number } = {}) =>
    api.get<Page<AdminUser>>('/admin/users', { params }).then((r) => r.data),

  getUser: (id: number) =>
    api.get<AdminUser>(`/admin/users/${id}`).then((r) => r.data),

  changeRole: (id: number, role: UserRole) =>
    api.patch<AdminUser>(`/admin/users/${id}/role`, { role }).then((r) => r.data),

  setActive: (id: number, is_active: boolean) =>
    api
      .patch<AdminUser>(`/admin/users/${id}/active`, { is_active })
      .then((r) => r.data),
}
