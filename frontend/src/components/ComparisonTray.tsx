import { InstitutionLogo } from './InstitutionLogo'
import { institutionName, careerLabel } from '../domain/institutions'
import { Link } from 'react-router-dom'
import { useComparison } from '../application/selection'
import { useResource } from '../application/useResource'
import type { Career } from '../domain/career'
import { Icon } from './Icon'

function Selected({ id }: { id: string }) {
  const { toggle } = useComparison()
  const { result } = useResource<Career>(`/carreras/${encodeURIComponent(id)}`)
  return <div className="tray-item">{result.status === 'success' && <InstitutionLogo code={result.data.institution} />}<div>
    <strong>{result.status === 'success' ? result.data.name : `Alternativa ${id}`}</strong>
    <small>{result.status === 'success' ? institutionName(result.data.institution) : result.status === 'error' ? 'Revisa la disponibilidad' : 'Cargando…'}</small>
  </div><button onClick={() => toggle(id)} aria-label={`Quitar ${result.status === 'success' ? careerLabel(result.data) : id}`}>×</button></div>
}
export function ComparisonTray() {
  const { ids, message } = useComparison()
  return <>{message && <p className="selection-message" role="alert">{message}</p>}
    {ids.length > 0 && <section className="comparison-tray" aria-label="Tu comparación">
      <div className="tray-title"><Icon name="compass" /><div><strong>Tu comparación</strong><small>{ids.length} de 2 seleccionadas</small></div></div>
      <div className="tray-items">{ids.map(id => <Selected key={id} id={id} />)}</div>
      <Link className="button primary" to="/comparar" aria-label={ids.length === 2 ? 'Comparar alternativas' : 'Ver selección'}>
        <span className="tray-action-long">{ids.length === 2 ? 'Comparar alternativas' : 'Ver selección'}</span>
        <span className="tray-action-short" aria-hidden="true">{ids.length === 2 ? 'Comparar' : 'Selección'}</span><Icon name="arrow" /></Link>
    </section>}</>
}
