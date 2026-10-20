import { useState } from 'react'
import type { Facets } from '../domain/career'
import { Icon } from './Icon'

import { filterNames } from '../domain/filters'

export function Filters({ values, facets, onChange, clear, failed, retry }: {
  values: URLSearchParams; facets?: Facets; onChange: (key: string, value: string) => void
  clear: () => void; failed: boolean; retry: () => void
}) {
  const [open, setOpen] = useState(false)
  return <aside className={`filters ${open ? 'is-open' : ''}`} aria-label="Filtros de carreras">
    <button className="filter-toggle" onClick={() => setOpen(!open)} aria-expanded={open}
      aria-controls="filter-fields"><Icon name="filter" /> Filtra tu búsqueda <span>{open ? '−' : '+'}</span></button>
    <div className="filter-desktop-title"><Icon name="filter" /><h2>Filtra tu búsqueda</h2></div>
    <div id="filter-fields" className="filter-fields">
      {Object.entries(filterNames).map(([key, label]) => {
        const selected = values.get(key) || ''
        const options = facets?.[key as keyof Facets] || []
        return <div className="filter-field" key={key}><label htmlFor={`filter-${key}`}>{label}</label>
          <select id={`filter-${key}`} value={selected} disabled={!facets} onChange={event => onChange(key, event.target.value)}>
            <option value="">{key === 'tipo' ? 'Todos los tipos' : key === 'modalidad' ? 'Todas las modalidades' : 'Todas las ubicaciones'}</option>
            {selected && !options.includes(selected) && <option value={selected}>{selected}</option>}
            {options.map(value => <option key={value} value={value}>{value}</option>)}
          </select></div>
      })}
      {failed && <p className="filter-error" role="alert">No se cargaron los filtros. <button onClick={retry}>Reintentar</button></p>}
      <button className="clear-filters" onClick={clear}><Icon name="reset" /> Limpiar filtros</button>
      <div className="filter-tip"><Icon name="info" /><p><strong>Información para decidir</strong><span>Revisa las fuentes y las condiciones del dato en cada ficha.</span></p></div>
    </div>
  </aside>
}
