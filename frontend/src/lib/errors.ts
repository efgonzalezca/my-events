import type { AxiosError } from 'axios'
import type { ApiError } from '../types'

export const ERROR_MESSAGES: Record<string, string> = {
  EMAIL_ALREADY_EXISTS: 'Ya existe una cuenta con ese correo.',
  INVALID_CREDENTIALS: 'Correo o contraseña incorrectos.',
  USER_NOT_FOUND: 'Usuario no encontrado.',
  EVENT_NOT_FOUND: 'El evento no existe.',
  EVENT_NOT_OWNED: 'No puedes modificar un evento que no es tuyo.',
  EVENT_NOT_MODIFIABLE: 'Este evento no se puede modificar en su estado actual.',
  INVALID_STATUS_TRANSITION: 'Esa transición de estado no está permitida.',
  CAPACITY_BELOW_REGISTERED: 'No puedes bajar la capacidad por debajo de los ya inscritos.',
  SPEAKER_NOT_FOUND: 'El ponente no existe.',
  SESSION_NOT_FOUND: 'La sesión no existe.',
  SESSION_OUT_OF_EVENT_RANGE: 'La sesión está fuera del rango del evento.',
  SESSION_SCHEDULE_CONFLICT: 'Hay otra sesión que se solapa con esta.',
  SPEAKER_ALREADY_LINKED: 'Ese ponente ya está en la sesión.',
  SPEAKER_NOT_LINKED: 'Ese ponente no está en la sesión.',
  REGISTRATION_NOT_FOUND: 'No estabas inscrito a este evento.',
  ALREADY_REGISTERED: 'Ya estás inscrito a este evento.',
  EVENT_FULL: 'Lo siento, el evento se llenó.',
  NOT_PUBLISHED: 'Este evento no está abierto a inscripciones.',
}

interface ValidationItem {
  loc?: (string | number)[]
  msg?: string
}

export function describeError(err: unknown, fallback = 'Algo salió mal'): string {
  const ax = err as AxiosError<ApiError | { detail: ValidationItem[] }>
  const data = ax?.response?.data as ApiError | { detail: ValidationItem[] } | undefined
  const code = (data as ApiError | undefined)?.code
  if (code && ERROR_MESSAGES[code]) return ERROR_MESSAGES[code]
  const detail = data?.detail
  if (typeof detail === 'string' && detail.length > 0) return detail
  if (Array.isArray(detail) && detail.length > 0) {
    return detail
      .map((item) => {
        const field = item.loc?.filter((p) => p !== 'body').join('.') ?? ''
        return field ? `${field}: ${item.msg ?? ''}` : item.msg ?? ''
      })
      .filter(Boolean)
      .join(' · ')
  }
  return fallback
}
