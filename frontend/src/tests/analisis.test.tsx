import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { ProveedorComparacion } from '../application/ProveedorComparacion'
import { PaginaComparar } from '../pages/PaginaComparar'
import { carrera } from './datosPrueba'

afterEach(() => { cleanup(); vi.unstubAllGlobals(); sessionStorage.clear() })
const analisis = { prediccion: 'Misma área', contrasteCatalogo: 'Áreas distintas', areas: ['Ingeniería', 'Negocios'],
  tipoExplicacion: 'structured', umbralCalidad: .90, calidadAprobada: false,
  analisisCriterios: ['duration', 'modality', 'location', 'cost', 'requirements', 'employment'].map((clave, indice) => ({
    clave, etiqueta: ['Duración', 'Modalidad', 'Ubicación', 'Costo', 'Requisitos', 'Campo laboral'][indice],
    valorIzquierda: 'Dato A', valorDerecha: 'Dato B', relacion: 'different',
    explicacion: `Diferencia documentada ${clave}`, recomendacion: `Revisa ${clave}`, advertencias: ['Dato estimado'],
  })),
  evaluacionesModelos: [{ nombre: 'Árbol de decisión', accuracy: .49, precision_macro: .42,
    recall_macro: .48, f1_macro: .36, validation_distance_to_ideal: .4 }],
  fuentesAreas: ['https://www.utp.edu.pe', null], coincideCatalogo: false,
  nombreModelo: 'Árbol de decisión', versionModelo: '1.0.0', metricas: { accuracy: .49, precision_macro: .42, recall_macro: .48, f1_macro: .36 },
  exactitudReferencia: .51, paresEntrenamiento: 28, paresPrueba: 55, limitaciones: ['Muestra pequeña'],
  siguientesPasos: ['Verifica las fuentes.'], recomendaciones: [] }
function mostrar(fallar = false) {
  sessionStorage.setItem('orienta-comparison', '["C01","C02"]')
  vi.stubGlobal('fetch', vi.fn((direccion: string) => Promise.resolve(new Response(JSON.stringify(
    direccion.endsWith('/analisis') ? analisis : { izquierda: carrera, derecha: { ...carrera, id: 'C02', nombre: 'Administración' },
      diferenciaDuracionMeses: 0, diferenciaCostoMensualSoles: '0' }
  ), { status: fallar && direccion.endsWith('/analisis') ? 503 : 200 }))))
  render(<MemoryRouter><ProveedorComparacion><PaginaComparar /></ProveedorComparacion></MemoryRouter>)
}
describe('Análisis HU-IA01', () => {
  it('envía las preferencias declaradas sin inventar las restantes', async () => {
    mostrar()
    const presupuesto = await screen.findByLabelText('Presupuesto mensual (S/)')
    await userEvent.type(presupuesto, '950')
    await userEvent.selectOptions(screen.getByLabelText('Modalidad preferida'), 'Virtual')
    await userEvent.click(screen.getByRole('button', { name: /Contrastar los seis criterios/ }))
    await screen.findByRole('heading', { name: 'Seis criterios para tomar una decisión informada' })
    const llamada = vi.mocked(fetch).mock.calls.find(([direccion]) => String(direccion).endsWith('/analisis'))
    expect(JSON.parse(String(llamada?.[1]?.body))).toEqual({ career_ids: ['C01', 'C02'],
      preferences: { budget_pen: 950, modality: 'Virtual' } })
    expect(screen.queryByText('Alternativa A')).not.toBeInTheDocument()
  })
  it('explica seis criterios y separa la evaluación del modelo no habilitado', async () => {
    mostrar()
    await userEvent.click(await screen.findByRole('button', { name: /Contrastar los seis criterios/ }))
    expect(await screen.findByRole('heading', { name: 'Seis criterios para tomar una decisión informada' })).toBeInTheDocument()
    expect(screen.getAllByText('Para decidir')).toHaveLength(6)
    expect(screen.getByText('Diferencia documentada employment')).toBeInTheDocument()
    await userEvent.click(screen.getByText('Evaluación de los modelos de contraste de áreas'))
    expect(screen.getByText('No habilitado para orientar decisiones')).toBeVisible()
    expect(screen.queryByText('Misma área')).not.toBeInTheDocument()
    expect(screen.getByText(/no superó una referencia básica/)).toBeInTheDocument()
    await userEvent.click(screen.getByText('Ver evaluación y limitaciones del modelo'))
    expect(screen.getAllByText('49.0%')).toHaveLength(2)
    screen.getAllByText('49.0%').forEach(valor => expect(valor).toBeVisible())
  })
  it('conserva la comparación cuando falla IA y permite reintentar', async () => {
    mostrar(true)
    await userEvent.click(await screen.findByRole('button', { name: /Contrastar los seis criterios/ }))
    expect(await screen.findByText('El análisis IA no está disponible')).toBeInTheDocument()
    expect(screen.getByRole('region', { name: /seis criterios/ })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Reintentar análisis/ })).toBeInTheDocument()
  })
})
