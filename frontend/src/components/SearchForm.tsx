import { useState } from 'react'
import { Icon } from './Icon'

export function SearchForm({ initial, onSearch }: { initial: string; onSearch: (q: string) => void }) {
  const [draft, setDraft] = useState(initial)
  return <form className="search-form" role="search" onSubmit={event => {
    event.preventDefault(); onSearch(draft.trim())
  }}><div className="search-input"><Icon name="search" />
    <label className="sr-only" htmlFor="career-search">Buscar carrera por nombre</label>
    <input id="career-search" type="search" value={draft} maxLength={150}
      onChange={event => setDraft(event.target.value)} placeholder="¿Qué carrera te gustaría estudiar?" />
  </div><button className="button primary" type="submit">Buscar <Icon name="arrow" /></button></form>
}
