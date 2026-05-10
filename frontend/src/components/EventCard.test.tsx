import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { EventCard } from './EventCard'
import type { Event } from '../types'

const sample: Event = {
  id: 1,
  name: 'React Conf Bogotá',
  description: '',
  location: 'Bogotá',
  starts_at: '2026-06-01T15:00:00.000Z',
  ends_at: '2026-06-01T18:00:00.000Z',
  capacity: 100,
  registered_count: 30,
  status: 'published',
  organizer_id: 1,
}

describe('EventCard', () => {
  it('renders event name, location, and counter', () => {
    render(
      <MemoryRouter>
        <EventCard event={sample} />
      </MemoryRouter>,
    )
    expect(screen.getByText('React Conf Bogotá')).toBeInTheDocument()
    expect(screen.getByText('Bogotá')).toBeInTheDocument()
    expect(screen.getByText('30 / 100 inscritos')).toBeInTheDocument()
    expect(screen.getByText('Publicado')).toBeInTheDocument()
  })

  it('shows the LLENO badge when capacity is reached', () => {
    render(
      <MemoryRouter>
        <EventCard event={{ ...sample, registered_count: 100 }} />
      </MemoryRouter>,
    )
    expect(screen.getByText(/Lleno/i)).toBeInTheDocument()
  })

  it('shows draft label for draft events', () => {
    render(
      <MemoryRouter>
        <EventCard event={{ ...sample, status: 'draft' }} />
      </MemoryRouter>,
    )
    expect(screen.getByText('Borrador')).toBeInTheDocument()
  })
})
