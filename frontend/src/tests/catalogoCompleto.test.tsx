import { afterEach, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { internalizarRespuesta } from '../adapters/contratosApi'
import { PaginaInstituciones } from '../pages/PaginaInstituciones'
import { ProveedorComparacion } from '../application/ProveedorComparacion'
import { PaginaComparar } from '../pages/PaginaComparar'
import { carrera } from './datosPrueba'

afterEach(() => { cleanup(); vi.unstubAllGlobals(); sessionStorage.clear() })

it('conserva las claves originales y la procedencia del programa dentro de detalles', () => {
  const detalles = { modalidad: 'presencial', fuentes: ['https://www.upn.edu.pe'],
    carrera_id: 'administracion', procedencia_comparacion: { modalidad: 'estimacion' } }
  const respuesta = internalizarRespuesta<{ nombre: string; detalles: typeof detalles }>({ name: 'Administración', detalles })
  expect(respuesta.nombre).toBe('Administración')
  expect(respuesta.detalles).toEqual(detalles)
})

it('muestra todas las instituciones recibidas y enlaza sus ofertas filtradas', async () => {
  const instituciones = Array.from({ length: 25 }, (_, indice) => ({ nombre: `Institución ${indice + 1}`,
    ofertas: indice === 0 ? 381 : 1, gestion: 'publica', tipo: 'instituto', distritos: ['Comas'] }))
  vi.stubGlobal('fetch', vi.fn(() => Promise.resolve(new Response(JSON.stringify(instituciones)))))
  render(<MemoryRouter><PaginaInstituciones /></MemoryRouter>)
  expect(await screen.findByText('25 instituciones · 405 ofertas académicas')).toBeInTheDocument()
  expect(screen.getAllByRole('article')).toHaveLength(25)
  expect(screen.getAllByRole('link', { name: /Explorar carreras/ })[24]).toHaveAttribute('href', '/?institucion=Instituci%C3%B3n%2025')
})

it('restaura identificadores largos y cambia los criterios visibles mediante pestañas', async () => {
  const identificadores = ['prg-upn-los-olivos-ingenieria-de-sistemas-computacionales', 'prg-uni-rimac-ingenieria-de-sistemas']
  sessionStorage.setItem('orienta-comparison', JSON.stringify(identificadores))
  vi.stubGlobal('fetch', vi.fn(() => Promise.resolve(new Response(JSON.stringify({
    izquierda: { ...carrera, id: identificadores[0] }, derecha: { ...carrera, id: identificadores[1], nombre: 'Administración' },
    diferenciaDuracionMeses: 0, diferenciaCostoMensualSoles: '0',
  })))))
  render(<MemoryRouter><ProveedorComparacion><PaginaComparar /></ProveedorComparacion></MemoryRouter>)
  expect(await screen.findByRole('table')).toBeInTheDocument()
  await userEvent.click(screen.getByRole('tab', { name: 'Malla curricular' }))
  expect(screen.getByRole('tab', { name: 'Malla curricular' })).toHaveAttribute('aria-selected', 'true')
  expect(screen.getByRole('rowheader', { name: 'Cursos principales' })).toBeInTheDocument()
  expect(JSON.parse(String(vi.mocked(fetch).mock.calls[0][1]?.body))).toEqual({ career_ids: identificadores })
})
