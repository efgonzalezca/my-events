export type UserRole = 'admin' | 'organizer' | 'attendee'

export interface User {
  id: number
  email: string
  full_name: string
  role: UserRole
  is_active: boolean
}

export type EventStatus = 'draft' | 'published' | 'cancelled'

export interface Event {
  id: number
  name: string
  description: string
  location: string
  starts_at: string
  ends_at: string
  capacity: number
  registered_count: number
  status: EventStatus
  organizer_id: number
}

export interface Page<T> {
  items: T[]
  page: number
  size: number
  total: number
}

export interface Session {
  id: number
  event_id: number
  title: string
  description: string
  starts_at: string
  ends_at: string
  speaker_ids: number[]
}

export interface Speaker {
  id: number
  name: string
  bio: string
  photo_url: string
}

export interface Registration {
  id: number
  user_id: number
  event_id: number
  created_at: string
}

export interface MyRegistrationItem {
  registration_id: number
  registered_at: string
  event: {
    id: number
    name: string
    location: string
    starts_at: string
    ends_at: string
    capacity: number
    registered_count: number
    status: string
  }
}

export interface ApiError {
  detail: string
  code: string
}