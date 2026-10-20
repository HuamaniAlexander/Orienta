import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { ComparisonProvider } from '../application/ComparisonContext'
import { ComparisonTray } from '../components/ComparisonTray'
import { SelectCareer } from '../components/SelectCareer'
import { ComparePage } from '../pages/ComparePage'
import { career } from './fixtures'

afterEach(() => { cleanup(); vi.unstubAllGlobals(); sessionStorage.clear() })
function show(entry = '/') {
  vi.stubGlobal('fetch', vi.fn((url: string) => Promise.resolve(new Response(JSON.stringify(
    url.endsWith('/comparaciones') ? { left: career, right: { ...career, id: 'C02', name: 'Administración' },
      duration_difference_months: 0, monthly_cost_difference_pen: '0' } : career)))))
  render(<MemoryRouter initialEntries={[entry]}><ComparisonProvider><Routes>
    <Route path="/" element={<><SelectCareer id="C01" /><SelectCareer id="C02" /><SelectCareer id="C03" /></>} />
    <Route path="/comparar" element={<ComparePage />} />
  </Routes><ComparisonTray /></ComparisonProvider></MemoryRouter>)
}
describe('Comparación HU04', () => {
  it('selecciona dos, impide una tercera y conserva la selección en sesión', async () => {
    show()
    const user = userEvent.setup()
    await user.click(screen.getAllByRole('button', { name: 'Comparar' })[0])
    await user.click(screen.getAllByRole('button', { name: 'Comparar' })[0])
    await user.click(screen.getByRole('button', { name: 'Comparar' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Ya elegiste dos')
    expect(JSON.parse(sessionStorage.getItem('orienta-comparison')!)).toEqual(['C01', 'C02'])
    await user.click(screen.getByRole('link', { name: /Comparar alternativas/ }))
    expect(await screen.findByRole('region', { name: /seis criterios/ })).toBeInTheDocument()
    expect(screen.getByText('Los importes mensuales informados son iguales.')).toBeInTheDocument()
  })
  it('muestra selección incompleta y permite quitar opciones', async () => {
    sessionStorage.setItem('orienta-comparison', '["C01"]')
    show('/comparar')
    expect(screen.getByRole('heading', { name: 'Falta una alternativa' })).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: /^Quitar / }))
    expect(screen.getByRole('heading', { name: 'Elige dos alternativas para empezar' })).toBeInTheDocument()
  })
  it('sustituye una alternativa conservando la otra', async () => {
    sessionStorage.setItem('orienta-comparison', '["C01","C02"]')
    show('/?sustituir=0')
    const buttons = screen.getAllByRole('button', { name: 'Elegir alternativa' })
    expect(buttons[1]).toBeDisabled()
    await userEvent.click(buttons[2])
    await waitFor(() => expect(JSON.parse(sessionStorage.getItem('orienta-comparison')!)).toEqual(['C03', 'C02']))
    expect(await screen.findByRole('region', { name: /seis criterios/ })).toBeInTheDocument()
  })
})
