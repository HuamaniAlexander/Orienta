import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { CareerPage } from '../pages/CareerPage'
import { CatalogPage } from '../pages/CatalogPage'
import { costLabel, safeSourceUrl } from '../domain/presentation'
import { career } from './fixtures'

afterEach(() => { cleanup(); vi.unstubAllGlobals() })
function show() {
  render(<MemoryRouter initialEntries={['/carreras/C01?q=software']}><Routes>
    <Route path="/carreras/:id" element={<CareerPage />} /><Route path="/" element={<CatalogPage />} />
  </Routes></MemoryRouter>)
}
describe('Ficha HU03', () => {
  it('muestra seis criterios, fuente estimada y retorno a filtros', async () => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation(() => Promise.resolve(new Response(JSON.stringify(career)))))
    show()
    expect(await screen.findByRole('heading', { name: career.name })).toBeInTheDocument()
    expect(screen.getByText('60 meses')).toBeInTheDocument()
    expect(screen.getByText('Secundaria completa')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Campo laboral' })).toBeInTheDocument()
    expect(screen.getAllByText('Estimado').length).toBeGreaterThan(0)
    expect(screen.getByRole('link', { name: /Volver a resultados/ })).toHaveAttribute('href', '/?q=software')
  })
  it('muestra faltantes sin convertirlos en cero y rechaza enlaces inseguros', async () => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation(() => Promise.resolve(new Response(JSON.stringify({
      ...career, monthly_cost_pen: null, duration_months: null, requirements: null,
      sources: [{ field: 'Costo', status: 'Sin verificar', reference: 'javascript:alert(1)' }],
    })))))
    show()
    await screen.findByRole('heading', { name: career.name })
    expect(screen.getAllByText('Dato no disponible').length).toBe(3)
    expect(screen.queryByRole('link', { name: /Ver fuente/ })).not.toBeInTheDocument()
    expect(costLabel('0')).toContain('0')
    expect(costLabel(null)).toBe('Dato no disponible')
    expect(safeSourceUrl('https://utp.edu.pe/carrera')).toBe('https://utp.edu.pe/carrera')
    expect(safeSourceUrl('data:text/html,test')).toBeNull()
  })
  it('muestra 404 sin inventar una ficha', async () => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation(() => Promise.resolve(new Response('{}', { status: 404 }))))
    show()
    expect(await screen.findByRole('heading', { name: 'Oferta no disponible' })).toBeInTheDocument()
  })
  it('recorre catálogo a ficha y vuelve conservando búsqueda', async () => {
    vi.stubGlobal('fetch', vi.fn((url: string) => Promise.resolve(new Response(JSON.stringify(
      url.includes('/carreras/C01') ? career : url.endsWith('/filtros')
        ? { tipo: ['Universitaria'], modalidad: ['Presencial'], ubicacion: ['Campus Lima Norte'] }
        : { items: [career], total: 1, pagina: 1, limite: 12, data_mode: 'demo' }
    )))))
    render(<MemoryRouter initialEntries={['/?q=software']}><Routes>
      <Route path="/" element={<CatalogPage />} /><Route path="/carreras/:id" element={<CareerPage />} />
    </Routes></MemoryRouter>)
    await userEvent.click(await screen.findByRole('link', { name: /Ver ficha académica/ }))
    expect(await screen.findByRole('heading', { name: 'Información académica' })).toBeInTheDocument()
    await userEvent.click(screen.getByRole('link', { name: /Volver a resultados/ }))
    expect(await screen.findByRole('searchbox')).toHaveValue('software')
    expect(await screen.findByRole('heading', { name: career.name })).toBeInTheDocument()
  })
})
