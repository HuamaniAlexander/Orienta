import { Link } from 'react-router-dom'
import { useComparison } from '../application/selection'
import { useResource } from '../application/useResource'
import type { Career } from '../domain/career'
import { Icon } from './Icon'

function Selected({ id, index }: { id: string; index: number }) {
  const { toggle } = useComparison()
  const { result } = useResource<Career>(`/carreras/${encodeURIComponent(id)}`)
  return <div className="tray-item"><span className="option-letter">{index ? 'B' : 'A'}</span><div>
    <strong>{result.status === 'success' ? result.data.name : `Alternativa ${id}`}</strong>
    <small>{result.status === 'success' ? result.data.institution : result.status === 'error' ? 'Revisa la disponibilidad' : 'Cargando…'}</small>
  </div><button onClick={() => toggle(id)} aria-label={`Quitar alternativa ${index ? 'B' : 'A'}`}>×</button></div>
}
export function ComparisonTray() {
  const { ids, message } = useComparison()
  return <>{message && <p className="selection-message" role="alert">{message}</p>}
    {ids.length > 0 && <section className="comparison-tray" aria-label="Tu comparación">
      <div className="tray-title"><Icon name="compass" /><div><strong>Tu comparación</strong><small>{ids.length} de 2 seleccionadas</small></div></div>
      <div className="tray-items">{ids.map((id, index) => <Selected key={id} id={id} index={index} />)}</div>
      <Link className="button primary" to="/comparar">{ids.length === 2 ? 'Comparar alternativas' : 'Ver selección'} <Icon name="arrow" /></Link>
    </section>}</>
}
