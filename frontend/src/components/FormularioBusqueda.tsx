import { useState } from 'react'
import { Icono } from './Icono'

export function FormularioBusqueda({ valorInicial, alBuscar }: { valorInicial: string; alBuscar: (q: string) => void }) {
  const [draft, setDraft] = useState(valorInicial)
  return <form className="search-form" role="search" onSubmit={evento => {
    evento.preventDefault(); alBuscar(draft.trim())
  }}><div className="search-input"><Icono nombre="busqueda" />
    <label className="sr-only" htmlFor="career-search">Buscar carrera por nombre</label>
    <input id="career-search" type="search" value={draft} maxLength={150}
      onChange={evento => setDraft(evento.target.value)} placeholder="¿Qué carrera te gustaría estudiar?" />
  </div><button className="button primary" type="submit">Buscar <Icono nombre="arrow" /></button></form>
}
