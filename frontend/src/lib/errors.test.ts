import { describe, expect, it } from 'vitest'
import type { AxiosError } from 'axios'
import { ERROR_MESSAGES, describeError } from './errors'

interface ErrorPayload {
  code?: string
  detail?: string | unknown[]
}

function makeAxiosError(payload: ErrorPayload): AxiosError {
  return {
    isAxiosError: true,
    response: { data: payload },
  } as unknown as AxiosError
}

describe('describeError', () => {
  it('maps a known backend code to its Spanish message', () => {
    const err = makeAxiosError({ code: 'EVENT_FULL', detail: 'event is full' })
    expect(describeError(err)).toBe(ERROR_MESSAGES.EVENT_FULL)
  })

  it('falls back to detail if the code is unknown', () => {
    const err = makeAxiosError({ code: 'SOMETHING_ELSE', detail: 'something happened' })
    expect(describeError(err)).toBe('something happened')
  })

  it('falls back to provided default if no info', () => {
    const err = makeAxiosError({})
    expect(describeError(err, 'oops')).toBe('oops')
  })

  it('returns the default for non-Axios errors', () => {
    expect(describeError(new Error('boom'), 'fallback')).toBe('fallback')
  })

  it('formats FastAPI 422 validation errors (detail is an array)', () => {
    const err = makeAxiosError({
      detail: [
        {
          type: 'value_error',
          loc: ['body', 'email'],
          msg: 'value is not a valid email address: reserved tld',
        },
      ],
    })
    expect(describeError(err)).toBe(
      'email: value is not a valid email address: reserved tld',
    )
  })

  it('covers every known backend code', () => {
    const codes = [
      'EMAIL_ALREADY_EXISTS', 'INVALID_CREDENTIALS', 'USER_NOT_FOUND',
      'EVENT_NOT_FOUND', 'EVENT_NOT_OWNED', 'EVENT_NOT_MODIFIABLE',
      'INVALID_STATUS_TRANSITION', 'CAPACITY_BELOW_REGISTERED',
      'SPEAKER_NOT_FOUND', 'SESSION_NOT_FOUND', 'SESSION_OUT_OF_EVENT_RANGE',
      'SESSION_SCHEDULE_CONFLICT', 'SPEAKER_ALREADY_LINKED', 'SPEAKER_NOT_LINKED',
      'REGISTRATION_NOT_FOUND', 'ALREADY_REGISTERED', 'EVENT_FULL', 'NOT_PUBLISHED',
    ]
    for (const c of codes) expect(ERROR_MESSAGES[c]).toBeTruthy()
  })
})
