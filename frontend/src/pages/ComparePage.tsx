import { InstitutionLogo } from '../components/InstitutionLogo'
import { institutionName, careerLabel } from '../domain/institutions'
import { Link } from 'react-router-dom'
import { useComparison } from '../application/selection'
import { useResource } from '../application/useResource'
import { ErrorState, Loading } from '../components/Feedback'
import { Icon } from '../components/Icon'
import type { Career } from '../domain/career'
import { costLabel } from '../domain/presentation'
import { AnalysisPanel } from '../components/AnalysisPanel'

export interface ComparisonResult {
  left: Career
  right: Career
  duration_difference_months: number | null
  monthly_cost_difference_pen: string | null
}

function ComparisonContent({ ids }: { ids: string[] }) {
  const { result, retry } = useResource<ComparisonResult>('/comparaciones', { career_ids: ids })
  if (result.status === 'loading') return <Loading detail />
  if (result.status === 'error') return <ErrorState retry={retry} />
  const { left, right, duration_difference_months: duration, monthly_cost_difference_pen: cost } = result.data
  const rows = [
    ['Duración', ...[left, right].map(c => c.duration_months === null ? 'Dato no disponible' : `${c.duration_months} meses`)],
    ['Modalidad', left.modality, right.modality], ['Ubicación / sede', left.location, right.location],
    ['Costo mensual de enseñanza', costLabel(left.monthly_cost_pen), costLabel(right.monthly_cost_pen)],
    ['Requisitos de ingreso', left.requirements, right.requirements], ['Campo laboral', left.employment, right.employment],
  ]
  return <>
    <div className="comparison-headings"><div className="criterion-spacer" />{[left, right].map((c, index) =>
      <article key={c.id} className="comparison-option"><InstitutionLogo code={c.institution} />
        <p>{institutionName(c.institution)} <span className="tag">{c.training_type || 'Sin tipo'}</span></p><h2>{c.name}</h2>
        <div><Link to={`/carreras/${c.id}`}>Ver ficha <Icon name="external" /></Link>
          <Link to={`/?sustituir=${index}`}>Sustituir</Link></div></article>)}</div>
    <section className="comparison-data" aria-label="Comparación de los seis criterios">{rows.map(([label, a, b]) =>
      <div className="comparison-row" key={label}><h3>{label}</h3><p><small>{careerLabel(left)}</small>{a || 'Dato no disponible'}</p>
        <p><small>{careerLabel(right)}</small>{b || 'Dato no disponible'}</p></div>)}</section>
    <div className="comparison-notes"><div><Icon name="clock" /><p><strong>Diferencia de duración</strong>
      {duration === null ? 'No disponible: falta información.' : duration === 0 ? 'Ambas alternativas tienen la misma duración informada.' : `${careerLabel(right)} tiene ${Math.abs(duration)} meses ${duration > 0 ? 'más' : 'menos'} que ${careerLabel(left)}.`}</p></div>
      <div><Icon name="coins" /><p><strong>Diferencia de importes mensuales</strong>
        {cost === null ? 'No disponible: falta información.' : Number(cost) === 0 ? 'Los importes mensuales informados son iguales.' : `${careerLabel(right)} tiene S/ ${Math.abs(Number(cost)).toLocaleString('es-PE')} ${Number(cost) > 0 ? 'más' : 'menos'} que ${careerLabel(left)} por mes.`}
      </p></div></div>
    <div className="cost-conditions"><Icon name="info" /><div><strong>Condiciones de los costos</strong>
      {[left, right].map(c => <p key={c.id}>{careerLabel(c)} · {c.sources.find(s => s.field === 'Costo')?.status || 'Condiciones pendientes de verificar'}</p>)}
      <p>Se contrastan importes de enseñanza en soles por mes. No representan el costo total de estudiar.</p></div></div>
    <AnalysisPanel ids={ids} names={[careerLabel(left), careerLabel(right)]} />
  </>
}

export function ComparePage() {
  const { ids, clear } = useComparison()
  return <><div className="breadcrumb"><Link to="/">Explorar</Link><span>/</span>Comparador</div>
    <section className="compare-hero"><div><p className="eyebrow">DOS OPCIONES, LOS MISMOS CRITERIOS</p>
      <h1>Compara tu próximo paso.</h1><p>Revisa las diferencias y consulta las fuentes de cada alternativa.</p></div>
      {ids.length > 0 && <button className="button" onClick={clear}>Limpiar selección</button>}</section>
    {ids.length !== 2 ? <section className="empty-state"><span className="state-icon"><Icon name="compass" /></span>
      <h2>{ids.length ? 'Falta una alternativa' : 'Elige dos alternativas para empezar'}</h2>
      <p>Selecciona exactamente dos opciones diferentes desde el catálogo o su ficha académica.</p>
      <Link className="button primary" to="/">Explorar carreras <Icon name="arrow" /></Link></section>
      : <ComparisonContent key={ids.join(':')} ids={ids} />}
  </>
}
