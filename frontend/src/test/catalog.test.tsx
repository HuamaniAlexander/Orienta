import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
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
function show(entry = '/') { render(<MemoryRouter initialEntries={[entry]}><CatalogPage /></MemoryRouter>) }
function response(items: Career[]) {
  return new Response(JSON.stringify({ items, total: items.length, pagina: 1, limite: 12, data_mode: 'demo' }))
}
const facets = { tipo: ['Universitaria'], modalidad: ['Presencial', 'Virtual'], ubicacion: ['Campus Lima Norte', 'Virtual'] }
function mockApi(items: Career[] = [career]) {
  const fetcher = vi.fn((url: string) => Promise.resolve(url.endsWith('/filtros')
    ? new Response(JSON.stringify(facets)) : response(items)))
  vi.stubGlobal('fetch', fetcher)
  return fetcher
}

describe('Catálogo HU01', () => {
  it('muestra tarjetas conectadas a la API y acceso a ficha', async () => {
    mockApi()
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
    mockApi([])
    show()
    expect(await screen.findByText('El catálogo aún está vacío')).toBeInTheDocument()
  })
  it('permite reintentar después de un error', async () => {
    let broken = true
    vi.stubGlobal('fetch', vi.fn((url: string) => {
      if (url.endsWith('/filtros')) return Promise.resolve(new Response(JSON.stringify(facets)))
      if (broken) { broken = false; return Promise.reject(new Error('offline')) }
      return Promise.resolve(response([career]))
    }))
    show()
    expect(await screen.findByRole('alert')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: /Reintentar/ }))
    expect(await screen.findByRole('heading', { name: career.name })).toBeInTheDocument()
  })
  it('combina búsqueda y filtros, conserva contexto en ficha y permite limpiar', async () => {
    const fetcher = mockApi()
    show()
    await screen.findByRole('heading', { name: career.name })
    const user = userEvent.setup()
    await user.type(screen.getByRole('searchbox'), 'software')
    await user.click(screen.getByRole('button', { name: 'Buscar' }))
    await user.selectOptions(screen.getByLabelText('Modalidad'), 'Virtual')
    await waitFor(() => expect(fetcher.mock.calls.some(([url]) =>
      url.includes('q=software') && url.includes('modalidad=Virtual'))).toBe(true))
    const link = await screen.findByRole('link', { name: /Ver ficha/ })
    expect(link.getAttribute('href')).toContain('q=software')
    expect(link.getAttribute('href')).toContain('modalidad=Virtual')
    await user.click(screen.getByRole('button', { name: /Limpiar filtros/ }))
    await waitFor(() => expect(screen.queryByLabelText('Filtros activos')).not.toBeInTheDocument())
    expect(screen.getByRole('searchbox')).toHaveValue('')
  })
  it('distingue sin coincidencias de catálogo vacío y restaura filtros desde URL', async () => {
    mockApi([])
    show('/?q=medicina&modalidad=Virtual')
    expect(await screen.findByText('No encontramos coincidencias')).toBeInTheDocument()
    expect(screen.getByRole('searchbox')).toHaveValue('medicina')
    expect(screen.getByLabelText('Modalidad')).toHaveValue('Virtual')
  })
  it('descarta una respuesta obsoleta al cambiar la búsqueda', async () => {
    let resolveOld: (r: Response) => void = () => {}
    vi.stubGlobal('fetch', vi.fn((url: string) => {
      if (url.endsWith('/filtros')) return Promise.resolve(new Response(JSON.stringify(facets)))
      if (url.includes('q=nueva')) return Promise.resolve(response([{ ...career, name: 'Nueva carrera' }]))
      return new Promise<Response>(resolve => { resolveOld = resolve })
    }))
    show()
    await userEvent.type(screen.getByRole('searchbox'), 'nueva')
    await userEvent.click(screen.getByRole('button', { name: 'Buscar' }))
    expect(await screen.findByRole('heading', { name: 'Nueva carrera' })).toBeInTheDocument()
    resolveOld(response([career]))
    await waitFor(() => expect(screen.queryByRole('heading', { name: career.name })).not.toBeInTheDocument())
  })
})
