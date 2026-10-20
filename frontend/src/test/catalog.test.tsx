import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { CatalogPage } from '../pages/CatalogPage'
import type { Career } from '../domain/career'

export const career: Career = {
  id: 'C01', name: 'Ingeniería de Software', institution: 'UTP', training_type: 'Universitaria',
  modality: 'Presencial', location: 'Campus Lima Norte', duration_months: 60,
  monthly_cost_pen: '775', requirements: 'Secundaria completa', employment: 'Software',
  reviewed_on: '2026-10-13', sources: [{ field: 'Costo', reference: 'Referencia del usuario', status: 'Estimado' }],
}

afterEach(() => { cleanup(); vi.unstubAllGlobals() })
function show() { render(<MemoryRouter><CatalogPage /></MemoryRouter>) }
function response(items: Career[]) {
  return new Response(JSON.stringify({ items, total: items.length, pagina: 1, limite: 12, data_mode: 'demo' }))
}

describe('Catálogo HU01', () => {
  it('muestra tarjetas conectadas a la API y acceso a ficha', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response([career])))
    show()
    expect(await screen.findByRole('heading', { name: career.name })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Ver ficha/ })).toHaveAttribute('href', '/carreras/C01')
    expect(screen.getByText(/Demostración con datos/)).toBeInTheDocument()
  })
  it('muestra carga mientras espera', () => {
    vi.stubGlobal('fetch', vi.fn(() => new Promise(() => {})))
    show()
    expect(screen.getByRole('status', { name: 'Cargando información' })).toBeInTheDocument()
  })
  it('distingue catálogo vacío', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response([])))
    show()
    expect(await screen.findByText('El catálogo aún está vacío')).toBeInTheDocument()
  })
  it('permite reintentar después de un error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValueOnce(new Error('offline'))
      .mockImplementation(() => Promise.resolve(response([career]))))
    show()
    expect(await screen.findByRole('alert')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: /Reintentar/ }))
    expect(await screen.findByRole('heading', { name: career.name })).toBeInTheDocument()
  })
})
