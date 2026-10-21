import { afterEach, expect, it, vi } from 'vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { CuestionarioVocacional } from '../components/CuestionarioVocacional'

const programas = [{ id: 'prg-sistemas', nombre: 'Sistemas', institucion: 'Institución uno' },
  { id: 'prg-contabilidad', nombre: 'Contabilidad', institucion: 'Institución dos' }]
const preguntas = Array.from({ length: 10 }, (_, indice) => ({ id: `p${indice + 1}`,
  texto: `Pregunta orientativa ${indice + 1}`, contexto: '', seccion: 'Tus preferencias',
  opciones: [{ id: indice < 6 ? '1' : indice < 9 ? programas[0].id : 'interes', texto: `Elección ${indice + 1}` }, { id: 'incierto', texto: 'No estoy seguro' }] }))
const cuestionario = { version: 'vocacional-1.0', programas, preguntas, aviso: 'Orientación, no prueba psicológica.' }
afterEach(() => { cleanup(); vi.unstubAllGlobals(); sessionStorage.clear() })

function mostrar(fallo = false) {
  const consultar = vi.fn<(url: string, opciones?: RequestInit) => Promise<Response>>((url: string) => Promise.resolve(new Response(JSON.stringify(url.includes('cuestionario/comparativo')
    ? cuestionario : { estado: 'sin_modelo', explicacion: 'Faltan elecciones reales para entrenar.', recomendada: null,
      factores: [], factoresContrarios: [], incertidumbres: [], modelo: null, idRegistro: null }), { status: fallo && url.endsWith('/recomendaciones') ? 503 : 200 })))
  vi.stubGlobal('fetch', consultar)
  render(<CuestionarioVocacional identificadores={programas.map(p => p.id)} />)
  return consultar
}

async function completar() {
  await userEvent.click(screen.getByRole('button', { name: 'Analizar con IA' }))
  for (let i = 1; i <= 10; i++) {
    await userEvent.click(await screen.findByRole('radio', { name: `Elección ${i}` }))
    if (i < 10) await userEvent.click(screen.getByRole('button', { name: 'Siguiente' }))
  }
}

it('bloquea avanzar sin respuesta, conserva respuestas al retroceder y al cerrar', async () => {
  mostrar()
  await userEvent.click(screen.getByRole('button', { name: 'Analizar con IA' }))
  expect(await screen.findByRole('button', { name: 'Siguiente' })).toBeDisabled()
  await userEvent.click(screen.getByRole('radio', { name: 'Elección 1' }))
  await userEvent.click(screen.getByRole('button', { name: 'Siguiente' }))
  await userEvent.click(screen.getByRole('button', { name: 'Anterior' }))
  expect(screen.getByRole('radio', { name: 'Elección 1' })).toBeChecked()
  await userEvent.click(screen.getByRole('button', { name: 'Cerrar cuestionario' }))
  await userEvent.click(screen.getByRole('button', { name: 'Analizar con IA' }))
  expect(screen.getByRole('radio', { name: 'Elección 1' })).toBeChecked()
})

it('envía diez respuestas y condiciones sin guardar datos de un visitante sin consentimiento', async () => {
  const consultar = mostrar()
  await completar()
  await userEvent.type(screen.getByLabelText('Presupuesto máximo mensual (S/)'), '800')
  await userEvent.click(screen.getByRole('button', { name: 'Analizar mis respuestas' }))
  expect(await screen.findByText('Faltan elecciones reales para entrenar.')).toBeInTheDocument()
  const cuerpo = JSON.parse(String(consultar.mock.calls.find(([url]) => url.endsWith('/recomendaciones'))?.[1]?.body))
  expect(Object.keys(cuerpo.respuestas)).toHaveLength(10)
  expect(cuerpo.idsProgramas).toEqual(programas.map(p => p.id))
  expect(cuerpo.preferencias).toEqual({ presupuestoMaximo: 800 })
  expect(cuerpo.captura).toBeUndefined()
  expect(sessionStorage.getItem('orienta-participante')).toBeNull()
  await userEvent.click(screen.getByRole('button', { name: 'Modificar respuestas' }))
  expect(screen.getByRole('radio', { name: 'Elección 1' })).toBeChecked()
})

it('requiere consentimiento, mayoría de edad y elección independiente para aportar datos', async () => {
  const consultar = mostrar()
  await completar()
  await userEvent.click(screen.getByText('Aportar voluntariamente al entrenamiento'))
  await userEvent.click(screen.getByLabelText(/Autorizo usar/))
  await userEvent.click(screen.getByRole('button', { name: 'Analizar mis respuestas' }))
  expect(await screen.findByRole('alert')).toHaveTextContent('confirma que eres mayor de edad')
  expect(consultar.mock.calls.filter(([url]) => url.endsWith('/recomendaciones'))).toHaveLength(0)
  await userEvent.click(screen.getByLabelText('Confirmo que tengo 18 años o más.'))
  await userEvent.selectOptions(screen.getByLabelText('Antes de ver un resultado, ¿qué opción elegirías?'), programas[1].id)
  await userEvent.click(screen.getByRole('button', { name: 'Analizar mis respuestas' }))
  await screen.findByText('Faltan elecciones reales para entrenar.')
  const llamada = consultar.mock.calls.find(([url]) => url.endsWith('/recomendaciones'))
  expect(JSON.parse(String(llamada?.[1]?.body)).captura).toMatchObject({ consentimiento: true, mayorEdad: true, eleccion: programas[1].id })
})

it('conserva las respuestas tras un error y permite reintentar', async () => {
  const consultar = mostrar(true)
  await completar()
  await userEvent.click(screen.getByRole('button', { name: 'Analizar mis respuestas' }))
  expect(await screen.findByRole('alert')).toHaveTextContent('Tus respuestas se conservan')
  expect(screen.getByRole('radio', { name: 'Elección 10' })).toBeChecked()
  await userEvent.click(screen.getByRole('button', { name: 'Analizar mis respuestas' }))
  await waitFor(() => expect(consultar.mock.calls.filter(([url]) => url.endsWith('/recomendaciones'))).toHaveLength(2))
})
