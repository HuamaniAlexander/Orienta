import { useState } from 'react'
import type { Facetas } from '../domain/carrera'
import { Icono } from './Icono'

import { nombresFiltros } from '../domain/filtros'

export function Filtros({ valores, facetas, alCambiar, limpiar, consultaFallida, reintentar }: {
  valores: URLSearchParams; facetas?: Facetas; alCambiar: (clave: string, valor: string) => void
  limpiar: () => void; consultaFallida: boolean; reintentar: () => void
}) {
  const [abierto, establecerAbierto] = useState(false)
  return <aside className={`filters ${abierto ? 'is-open' : ''}`} aria-label="Filtros de carreras">
    <button className="filter-toggle" onClick={() => establecerAbierto(!abierto)} aria-expanded={abierto}
      aria-controls="filter-fields"><Icono nombre="filter" /> Filtra tu búsqueda <span>{abierto ? '−' : '+'}</span></button>
    <div className="filter-desktop-title"><Icono nombre="filter" /><h2>Filtra tu búsqueda</h2></div>
    <div id="filter-fields" className="filter-fields">
      {Object.entries(nombresFiltros).map(([clave, etiqueta]) => {
        const seleccionado = valores.get(clave) || ''
        const opciones = facetas?.[clave as keyof Facetas] || []
        return <div className="filter-field" key={clave}><label htmlFor={`filter-${clave}`}>{etiqueta}</label>
          <select id={`filter-${clave}`} value={seleccionado} disabled={!facetas} onChange={evento => alCambiar(clave, evento.target.value)}>
            <option value="">{clave === 'tipo' ? 'Todos los tipos' : clave === 'modalidad' ? 'Todas las modalidades' : 'Todas las opciones'}</option>
            {seleccionado && !opciones.includes(seleccionado) && <option value={seleccionado}>{seleccionado}</option>}
            {opciones.map(valor => <option key={valor} value={valor}>{clave === "gestion" ? valor === "publica" ? "Pública" : "Privada" : valor}</option>)}
          </select></div>
      })}
      <div className="filter-field"><label htmlFor="costo-maximo">Pensión máxima mensual (S/)</label><input id="costo-maximo" type="number" min="0" step="50" placeholder="Sin límite" value={valores.get("costo_maximo") || ""} onChange={evento => alCambiar("costo_maximo", evento.target.value)} /><small>Importes estimados del catálogo</small></div>
      {consultaFallida && <p className="filter-error" role="alert">No se cargaron los filtros. <button onClick={reintentar}>Reintentar</button></p>}
      <button className="clear-filters" onClick={limpiar}><Icono nombre="reset" /> Limpiar filtros</button>
      <div className="filter-tip"><Icono nombre="info" /><p><strong>Información para decidir</strong><span>Revisa las fuentes y las condiciones del dato en cada ficha.</span></p></div>
    </div>
  </aside>
}
