import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { ComparisonProvider } from '../application/ComparisonContext'
import { ComparePage } from '../pages/ComparePage'
import { career } from './fixtures'

afterEach(() => { cleanup(); vi.unstubAllGlobals(); sessionStorage.clear() })
const analysis = { prediction: 'Misma área', catalog_contrast: 'Áreas distintas', areas: ['Ingeniería', 'Negocios'],
  area_sources: ['https://www.utp.edu.pe', null], agrees_with_catalog: false,
  model_name: 'Árbol de decisión', model_version: '1.0.0', metrics: { accuracy: .49, precision_macro: .42, recall_macro: .48, f1_macro: .36 },
  baseline_accuracy: .51, training_pairs: 28, test_pairs: 55, limitations: ['Muestra pequeña'],
  next_steps: ['Verifica las fuentes.'], recommendations: [] }
function show(fail = false) {
  sessionStorage.setItem('orienta-comparison', '["C01","C02"]')
  vi.stubGlobal('fetch', vi.fn((url: string) => Promise.resolve(new Response(JSON.stringify(
    url.endsWith('/analisis') ? analysis : { left: career, right: { ...career, id: 'C02', name: 'Administración' },
      duration_difference_months: 0, monthly_cost_difference_pen: '0' }
  ), { status: fail && url.endsWith('/analisis') ? 503 : 200 }))))
  render(<MemoryRouter><ComparisonProvider><ComparePage /></ComparisonProvider></MemoryRouter>)
}
describe('Análisis HU-IA01', () => {
  it('muestra predicción separada del catálogo, discrepancia y métricas', async () => {
    show()
    await userEvent.click(await screen.findByRole('button', { name: /Analizar con IA/ }))
    expect(await screen.findByText(/El modelo discrepa del catálogo/)).toBeInTheDocument()
    expect(screen.getByText('Áreas distintas')).toBeInTheDocument()
    expect(screen.getByText('Misma área')).toBeInTheDocument()
    expect(screen.getByText(/no superó una referencia básica/)).toBeInTheDocument()
    await userEvent.click(screen.getByText('Ver evaluación y limitaciones del modelo'))
    expect(screen.getByText('49.0%')).toBeVisible()
  })
  it('conserva la comparación cuando falla IA y permite reintentar', async () => {
    show(true)
    await userEvent.click(await screen.findByRole('button', { name: /Analizar con IA/ }))
    expect(await screen.findByText('El análisis IA no está disponible')).toBeInTheDocument()
    expect(screen.getByRole('region', { name: /seis criterios/ })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Reintentar análisis/ })).toBeInTheDocument()
  })
})
