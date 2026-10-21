import { useState } from 'react'
import { Icono } from './Icono'

export function FormularioBusqueda({ valorInicial, alBuscar }: { valorInicial: string; alBuscar: (q: string) => void }) {
  const [borrador, establecerBorrador] = useState(valorInicial)
  return <form className="search-form" role="search" onSubmit={evento => {
    evento.preventDefault(); alBuscar(borrador.trim())
  }}><div className="search-input"><Icono nombre="busqueda" />
    <label className="sr-only" htmlFor="career-search">Buscar carrera, institución o área</label>
    <input id="career-search" type="search" value={borrador} maxLength={150}
      onChange={evento => establecerBorrador(evento.target.value)} placeholder="Buscar por carrera, institución o área" />
  </div><button className="button primary" type="submit">Buscar <Icono nombre="arrow" /></button></form>
}
