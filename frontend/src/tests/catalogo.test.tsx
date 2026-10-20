import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { PaginaExplorar } from '../pages/PaginaExplorar'
import type { Carrera } from '../domain/carrera'

import { carrera } from './datosPrueba'

afterEach(() => { cleanup(); vi.unstubAllGlobals() })
function mostrar(entrada = '/') { render(<MemoryRouter initialEntries={[entrada]}><PaginaExplorar /></MemoryRouter>) }
function respuesta(elementos: Carrera[]) {
  return new Response(JSON.stringify({ elementos, total: elementos.length, pagina: 1, limite: 12, modoDatos: 'demo' }))
}
const facetas = { tipo: ['Universitaria'], modalidad: ['Presencial', 'Virtual'], ubicacion: ['Campus Lima Norte', 'Virtual'] }
function simularApi(elementos: Carrera[] = [carrera]) {
  const consultor = vi.fn((direccion: string) => Promise.resolve(direccion.endsWith('/filtros')
    ? new Response(JSON.stringify(facetas)) : respuesta(elementos)))
  vi.stubGlobal('fetch', consultor)
  return consultor
}

describe('Catálogo HU01', () => {
  it('conserva el modo de sustitución al limpiar filtros', async () => {
    simularApi()
    mostrar('/?q=software&sustituir=0')
    await screen.findByRole('heading', { name: carrera.nombre })
    await userEvent.click(screen.getByRole('button', { name: /Limpiar filtros/ }))
    const enlace = await screen.findByRole('link', { name: /Ver ficha/ })
    expect(enlace.getAttribute('href')).toContain('sustituir=0')
    expect(screen.getByRole('searchbox')).toHaveValue('')
  })
  it('permite regresar desde una página fuera de rango', async () => {
    vi.stubGlobal('fetch', vi.fn((direccion: string) => Promise.resolve(direccion.endsWith('/filtros')
      ? new Response(JSON.stringify(facetas)) : new Response(JSON.stringify({
        elementos: [], total: 19, pagina: 999, limite: 12, modoDatos: 'postgres',
      })))))
    mostrar('/?pagina=999')
    expect(await screen.findByText('Esta página no tiene resultados')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Volver a la primera página' })).toBeInTheDocument()
  })
  it('muestra tarjetas conectadas a la API y acceso a ficha', async () => {
    simularApi()
    mostrar()
    expect(await screen.findByRole('heading', { name: carrera.nombre })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Ver ficha/ })).toHaveAttribute('href', '/carreras/C01')
    expect(screen.queryByText(/Demostración con datos/)).not.toBeInTheDocument()
  })
  it('muestra carga mientras espera', () => {
    vi.stubGlobal('fetch', vi.fn(() => new Promise(() => {})))
    mostrar()
    expect(screen.getByRole('status', { name: 'Cargando información' })).toBeInTheDocument()
  })
  it('distingue catálogo vacío', async () => {
    simularApi([])
    mostrar()
    expect(await screen.findByText('El catálogo aún está vacío')).toBeInTheDocument()
  })
  it('permite reintentar después de un error', async () => {
    let averiada = true
    vi.stubGlobal('fetch', vi.fn((direccion: string) => {
      if (direccion.endsWith('/filtros')) return Promise.resolve(new Response(JSON.stringify(facetas)))
      if (averiada) { averiada = false; return Promise.reject(new Error('offline')) }
      return Promise.resolve(respuesta([carrera]))
    }))
    mostrar()
    expect(await screen.findByRole('alert')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: /Reintentar/ }))
    expect(await screen.findByRole('heading', { name: carrera.nombre })).toBeInTheDocument()
  })
  it('combina búsqueda y filtros, conserva contexto en ficha y permite limpiar', async () => {
    const consultor = simularApi()
    mostrar()
    await screen.findByRole('heading', { name: carrera.nombre })
    const usuario = userEvent.setup()
    await usuario.type(screen.getByRole('searchbox'), 'software')
    await usuario.click(screen.getByRole('button', { name: 'Buscar' }))
    await usuario.selectOptions(screen.getByLabelText('Modalidad'), 'Virtual')
    await waitFor(() => expect(consultor.mock.calls.some(([direccion]) =>
      direccion.includes('q=software') && direccion.includes('modalidad=Virtual'))).toBe(true))
    const enlace = await screen.findByRole('link', { name: /Ver ficha/ })
    expect(enlace.getAttribute('href')).toContain('q=software')
    expect(enlace.getAttribute('href')).toContain('modalidad=Virtual')
    await usuario.click(screen.getByRole('button', { name: /Limpiar filtros/ }))
    await waitFor(() => expect(screen.queryByLabelText('Filtros activos')).not.toBeInTheDocument())
    expect(screen.getByRole('searchbox')).toHaveValue('')
  })
  it('distingue sin coincidencias de catálogo vacío y restaura filtros desde URL', async () => {
    simularApi([])
    mostrar('/?q=medicina&modalidad=Virtual')
    expect(await screen.findByText('No encontramos coincidencias')).toBeInTheDocument()
    expect(screen.getByRole('searchbox')).toHaveValue('medicina')
    expect(screen.getByLabelText('Modalidad')).toHaveValue('Virtual')
  })
  it('descarta una respuesta obsoleta al cambiar la búsqueda', async () => {
    let resolverAnterior: (r: Response) => void = () => {}
    vi.stubGlobal('fetch', vi.fn((direccion: string) => {
      if (direccion.endsWith('/filtros')) return Promise.resolve(new Response(JSON.stringify(facetas)))
      if (direccion.includes('q=nueva')) return Promise.resolve(respuesta([{ ...carrera, nombre: 'Nueva carrera' }]))
      return new Promise<Response>(resolver => { resolverAnterior = resolver })
    }))
    mostrar()
    await userEvent.type(screen.getByRole('searchbox'), 'nueva')
    await userEvent.click(screen.getByRole('button', { name: 'Buscar' }))
    expect(await screen.findByRole('heading', { name: 'Nueva carrera' })).toBeInTheDocument()
    resolverAnterior(respuesta([carrera]))
    await waitFor(() => expect(screen.queryByRole('heading', { name: carrera.nombre })).not.toBeInTheDocument())
  })
})
