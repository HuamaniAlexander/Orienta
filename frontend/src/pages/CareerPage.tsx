import { InstitutionLogo } from '../components/InstitutionLogo'
import { institutionName } from '../domain/institutions'
import { Link, useLocation, useParams } from 'react-router-dom'
import { useResource } from '../application/useResource'
import { ApiError } from '../adapters/api'
import { ErrorState, Loading } from '../components/Feedback'
import { Icon } from '../components/Icon'
import type { IconName } from '../components/Icon'
import type { Career, Source } from '../domain/career'
import { costLabel, reviewLabel, safeSourceUrl } from '../domain/presentation'
import { SelectCareer } from '../components/SelectCareer'

function Status({ source }: { source?: Source }) {
  const status = source?.status || 'Sin estado registrado'
  const verified = /^verificado/i.test(status)
  const estimated = /^estimado/i.test(status)
  return <span className={`data-status ${verified ? 'verified' : estimated ? 'estimated' : ''}`}>
    <Icon name={verified ? 'check' : 'info'} />{verified ? 'Verificado según registro' : estimated ? 'Estimado' : 'Sin verificación registrada'}
  </span>
}

function Fact({ icon, title, value, note, source }: {
  icon: IconName; title: string; value: string; note?: string; source?: Source
}) {
  return <div className="detail-fact"><span className="fact-icon"><Icon name={icon} /></span>
    <div><dt>{title}</dt><dd>{value}</dd>{note && <p>{note}</p>}
      <Status source={source} /></div></div>
}

export function CareerPage() {
  const { id = '' } = useParams()
  const { search } = useLocation()
  const { result, retry } = useResource<Career>(`/carreras/${encodeURIComponent(id)}`)
  const back = `/${search}`
  if (result.status === 'loading') return <><Link to={back} className="back-link">← Volver a resultados</Link><Loading detail /></>
  if (result.status === 'error') return <><Link to={back} className="back-link">← Volver a resultados</Link>
    {result.error instanceof ApiError && result.error.status === 404
      ? <section className="empty-state"><span className="state-icon"><Icon name="book" /></span>
        <h1>Oferta no disponible</h1><p>La alternativa ya no está publicada o el enlace es incorrecto.</p>
        <Link className="button primary" to={back}>Explorar alternativas</Link></section>
      : <ErrorState retry={retry} />}</>
  const c = result.data
  const source = (field: string) => c.sources.find(s => s.field === field)
  return <>
    <div className="breadcrumb"><Link to={back}>Explorar</Link><span>/</span><span>{c.name}</span></div>
    <Link to={back} className="back-link"><span aria-hidden="true">←</span> Volver a resultados</Link>
    <section className="detail-heading"><SelectCareer id={c.id} /><p className="eyebrow">CONOCE TU ALTERNATIVA</p>
      <h1>{c.name}</h1><div className="detail-subtitle"><InstitutionLogo code={c.institution} /><span>{institutionName(c.institution)}</span>
        <span className="tag">{c.training_type || 'Tipo no disponible'}</span></div></section>
    <div className="detail-layout"><div className="detail-main">
      <section className="panel" aria-labelledby="academic-title"><h2 id="academic-title">Información académica</h2>
        <dl className="detail-facts">
          <Fact title="Duración" icon="clock" value={c.duration_months === null ? 'Dato no disponible' : `${c.duration_months} meses`}
            note={c.duration_months === null ? 'Pendiente de registrar.' : 'Duración informada por la fuente registrada.'} source={source('Duración')} />
          <Fact title="Modalidad" icon="screen" value={c.modality || 'Dato no disponible'} source={source('Modalidad')} />
          <Fact title="Ubicación / sede" icon="pin" value={c.location || 'Dato no disponible'}
            note="Confirma la sede y disponibilidad con la institución." />
          <Fact title="Costo mensual de enseñanza" icon="coins" value={costLabel(c.monthly_cost_pen)}
            note={source('Costo')?.status || 'Consulta moneda, periodo y condiciones antes de decidir.'} source={source('Costo')} />
        </dl></section>
      <section className="panel text-panel"><span className="fact-icon"><Icon name="book" /></span>
        <div><h2>Requisitos de ingreso</h2><p>{c.requirements || 'Dato no disponible'}</p>
          <p className="secondary-note">Confirma el proceso vigente con la institución.</p></div></section>
      <section className="panel text-panel"><span className="fact-icon"><Icon name="briefcase" /></span>
        <div><h2>Campo laboral</h2><p>{c.employment || 'Dato no disponible'}</p>
          <p className="secondary-note">Consulta los ámbitos de trabajo y la información vigente con la institución.</p></div></section>
      <div className="detail-disclaimer"><Icon name="info" /><p>Una ficha es un punto de partida.
        Revisa las fuentes y consulta la información vigente antes de tomar una decisión.</p></div>
    </div><aside className="detail-sidebar" aria-label="Fuentes y revisión">
      <section className="panel sources-panel"><div className="panel-title"><span className="fact-icon"><Icon name="book" /></span><h2>Fuentes y revisión</h2></div>
        <div className="review-date"><small>Última revisión registrada</small><strong>{reviewLabel(c.reviewed_on)}</strong></div>
        <p className="source-intro">Consulta la procedencia y la condición de cada dato antes de decidir.</p>
        <ul className="source-list">{c.sources.map(s => {
          const url = safeSourceUrl(s.reference)
          return <li key={s.field}><strong>{s.field}</strong><Status source={s} />
            {url ? <a href={url} target="_blank" rel="noopener noreferrer">Ver fuente <span className="sr-only">de {s.field} (abre en otra pestaña)</span><Icon name="external" /></a>
              : <p>{s.reference || 'Fuente no registrada'}</p>}
            <p className="source-condition">{s.status}</p></li>
        })}</ul>
      </section>
      <section className="next-step"><Icon name="compass" /><h2>Sigue explorando</h2><p>Conoce otras alternativas y amplía tus posibilidades.</p>
        <Link to={back}>Volver al catálogo <Icon name="arrow" /></Link></section>
    </aside></div>
  </>
}
