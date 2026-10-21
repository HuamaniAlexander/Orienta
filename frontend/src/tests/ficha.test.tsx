import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { PaginaCarrera } from '../pages/PaginaCarrera'
import { PaginaExplorar } from '../pages/PaginaExplorar'
import { etiquetaCosto, urlFuenteSegura } from '../domain/presentacion'
import { carrera } from './datosPrueba'

afterEach(() => { cleanup(); vi.unstubAllGlobals() })
function mostrar() {
  render(<MemoryRouter initialEntries={['/carreras/C01?q=software']}><Routes>
    <Route path="/carreras/:id" element={<PaginaCarrera />} /><Route path="/" element={<PaginaExplorar />} />
  </Routes></MemoryRouter>)
}
describe('Ficha HU03', () => {
  it('muestra seis criterios, fuente estimada y retorno a filtros', async () => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation(() => Promise.resolve(new Response(JSON.stringify(carrera)))))
    mostrar()
    expect(await screen.findByRole('heading', { name: carrera.nombre })).toBeInTheDocument()
    expect(screen.getByText('60 meses')).toBeInTheDocument()
    expect(screen.getByText('Secundaria completa')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Campo laboral' })).toBeInTheDocument()
    expect(screen.getAllByText('Estimado').length).toBeGreaterThan(0)
    expect(screen.getByRole('link', { name: /Volver a resultados/ })).toHaveAttribute('href', '/?q=software')
  })
  it('muestra faltantes sin convertirlos en cero y rechaza enlaces inseguros', async () => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation(() => Promise.resolve(new Response(JSON.stringify({
      ...carrera, costoMensualSoles: null, duracionMeses: null, requisitos: null,
      fuentes: [{ campo: 'Costo', estado: 'Sin verificar', referencia: 'javascript:alert(1)' }],
    })))))
    mostrar()
    await screen.findByRole('heading', { name: carrera.nombre })
    expect(screen.getAllByText('Dato no disponible').length).toBe(3)
    expect(screen.queryByRole('link', { name: /Ver fuente/ })).not.toBeInTheDocument()
    expect(etiquetaCosto('0')).toContain('0')
    expect(etiquetaCosto(null)).toBe('Dato no disponible')
    expect(urlFuenteSegura('https://utp.edu.pe/carrera')).toBe('https://utp.edu.pe/carrera')
    expect(urlFuenteSegura('data:text/html,test')).toBeNull()
  })
  it('muestra 404 sin inventar una ficha', async () => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation(() => Promise.resolve(new Response('{}', { status: 404 }))))
    mostrar()
    expect(await screen.findByRole('heading', { name: 'Oferta no disponible' })).toBeInTheDocument()
  })
  it('recorre catálogo a ficha y vuelve conservando búsqueda', async () => {
    vi.stubGlobal('fetch', vi.fn((direccion: string) => Promise.resolve(new Response(JSON.stringify(
      direccion.includes('/carreras/C01') ? carrera : direccion.endsWith('/filtros')
        ? { tipo: ['Universitaria'], modalidad: ['Presencial'], ubicacion: ['Campus Lima Norte'] }
        : { elementos: [carrera], total: 1, pagina: 1, limite: 12, modoDatos: 'demo' }
    )))))
    render(<MemoryRouter initialEntries={['/?q=software']}><Routes>
      <Route path="/" element={<PaginaExplorar />} /><Route path="/carreras/:id" element={<PaginaCarrera />} />
    </Routes></MemoryRouter>)
    await userEvent.click(await screen.findByRole('link', { name: /Ver ficha académica/ }))
    expect(await screen.findByRole('heading', { name: 'Información académica' })).toBeInTheDocument()
    await userEvent.click(screen.getByRole('link', { name: /Volver a resultados/ }))
    expect(await screen.findByRole('searchbox')).toHaveValue('software')
    expect(await screen.findByRole('heading', { name: carrera.nombre })).toBeInTheDocument()
  })
})
