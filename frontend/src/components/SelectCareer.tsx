import { useNavigate, useSearchParams } from 'react-router-dom'
import { useComparison } from '../application/selection'
import { Icon } from './Icon'

export function SelectCareer({ id }: { id: string }) {
  const { ids, toggle } = useComparison()
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const raw = params.get('sustituir')
  const index = raw === '0' || raw === '1' ? Number(raw) : undefined
  const selected = ids.includes(id)
  const blocked = index !== undefined && selected && ids[index] !== id
  return <button className={`select-career ${selected ? 'selected' : ''}`} aria-pressed={selected}
    disabled={blocked} onClick={() => {
      toggle(id, index)
      if (index !== undefined && !blocked) navigate('/comparar')
    }}><span className="selection-box">{selected && <Icon name="check" />}</span>
      {index !== undefined ? 'Elegir alternativa' : selected ? 'Seleccionada' : 'Comparar'}</button>
}
