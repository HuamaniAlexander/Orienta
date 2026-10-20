import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { ComparisonProvider } from '../application/ComparisonContext'
import { ComparePage } from '../pages/ComparePage'
import { career } from './fixtures'

afterEach(() => { cleanup(); vi.unstubAllGlobals(); sessionStorage.clear() })
const analysis = { prediction: 'Misma área', catalog_contrast: 'Áreas distintas', areas: ['Ingeniería', 'Negocios'],
  explanation_kind: 'structured', quality_target: .90, quality_approved: false,
  criteria_analysis: ['duration', 'modality', 'location', 'cost', 'requirements', 'employment'].map((key, index) => ({
    key, label: ['Duración', 'Modalidad', 'Ubicación', 'Costo', 'Requisitos', 'Campo laboral'][index],
    left_value: 'Dato A', right_value: 'Dato B', relationship: 'different',
    explanation: `Diferencia documentada ${key}`, recommendation: `Revisa ${key}`, caveats: ['Dato estimado'],
  })),
  model_evaluations: [{ name: 'Árbol de decisión', accuracy: .49, precision_macro: .42,
    recall_macro: .48, f1_macro: .36, validation_distance_to_ideal: .4 }],
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
  it('explica seis criterios y separa la evaluación del modelo no habilitado', async () => {
    show()
    await userEvent.click(await screen.findByRole('button', { name: /Analizar con IA/ }))
    expect(await screen.findByRole('heading', { name: 'Seis criterios para tomar una decisión informada' })).toBeInTheDocument()
    expect(screen.getAllByText('Para decidir')).toHaveLength(6)
    expect(screen.getByText('Diferencia documentada employment')).toBeInTheDocument()
    await userEvent.click(screen.getByText('Evaluación de los modelos de contraste de áreas'))
    expect(screen.getByText('No habilitado para orientar decisiones')).toBeVisible()
    expect(screen.queryByText('Misma área')).not.toBeInTheDocument()
    expect(screen.getByText(/no superó una referencia básica/)).toBeInTheDocument()
    await userEvent.click(screen.getByText('Ver evaluación y limitaciones del modelo'))
    expect(screen.getAllByText('49.0%')).toHaveLength(2)
    screen.getAllByText('49.0%').forEach(value => expect(value).toBeVisible())
  })
  it('conserva la comparación cuando falla IA y permite reintentar', async () => {
    show(true)
    await userEvent.click(await screen.findByRole('button', { name: /Analizar con IA/ }))
    expect(await screen.findByText('El análisis IA no está disponible')).toBeInTheDocument()
    expect(screen.getByRole('region', { name: /seis criterios/ })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Reintentar análisis/ })).toBeInTheDocument()
  })
})
