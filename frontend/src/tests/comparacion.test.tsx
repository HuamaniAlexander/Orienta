import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { ProveedorComparacion } from '../application/ProveedorComparacion'
import { BandejaComparacion } from '../components/BandejaComparacion'
import { SeleccionarCarrera } from '../components/SeleccionarCarrera'
import { PaginaComparar } from '../pages/PaginaComparar'
import { carrera } from './datosPrueba'

afterEach(() => { cleanup(); vi.unstubAllGlobals(); sessionStorage.clear() })
function mostrar(entrada = '/') {
  vi.stubGlobal('fetch', vi.fn((direccion: string) => Promise.resolve(new Response(JSON.stringify(
    direccion.endsWith('/comparaciones') ? { izquierda: carrera, derecha: { ...carrera, id: 'C02', nombre: 'Administración' },
      diferenciaDuracionMeses: 0, diferenciaCostoMensualSoles: '0' } : carrera)))))
  render(<MemoryRouter initialEntries={[entrada]}><ProveedorComparacion><Routes>
    <Route path="/" element={<><SeleccionarCarrera id="C01" /><SeleccionarCarrera id="C02" /><SeleccionarCarrera id="C03" /></>} />
    <Route path="/comparar" element={<PaginaComparar />} />
  </Routes><BandejaComparacion /></ProveedorComparacion></MemoryRouter>)
}
describe('Comparación HU04', () => {
  it('selecciona dos, impide una tercera y conserva la selección en sesión', async () => {
    mostrar()
    const usuario = userEvent.setup()
    await usuario.click(screen.getAllByRole('button', { name: 'Comparar' })[0])
    await usuario.click(screen.getAllByRole('button', { name: 'Comparar' })[0])
    await usuario.click(screen.getByRole('button', { name: 'Comparar' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Ya elegiste dos')
    expect(JSON.parse(sessionStorage.getItem('orienta-comparison')!)).toEqual(['C01', 'C02'])
    await usuario.click(screen.getByRole('link', { name: /Comparar alternativas/ }))
    expect(await screen.findByRole('region', { name: /seis criterios/ })).toBeInTheDocument()
    expect(screen.getByText('Los importes mensuales informados son iguales.')).toBeInTheDocument()
  })
  it('muestra selección incompleta y permite quitar opciones', async () => {
    sessionStorage.setItem('orienta-comparison', '["C01"]')
    mostrar('/comparar')
    expect(screen.getByRole('heading', { name: 'Falta una alternativa' })).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: /^Quitar / }))
    expect(screen.getByRole('heading', { name: 'Elige dos alternativas para empezar' })).toBeInTheDocument()
  })
  it('sustituye una alternativa conservando la otra', async () => {
    sessionStorage.setItem('orienta-comparison', '["C01","C02"]')
    mostrar('/?sustituir=0')
    const botones = screen.getAllByRole('button', { name: 'Elegir alternativa' })
    expect(botones[1]).toBeDisabled()
    await userEvent.click(botones[2])
    await waitFor(() => expect(JSON.parse(sessionStorage.getItem('orienta-comparison')!)).toEqual(['C03', 'C02']))
    expect(await screen.findByRole('region', { name: /seis criterios/ })).toBeInTheDocument()
  })
})
