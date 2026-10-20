import { PerfilAcademico } from '../components/PerfilAcademico'
import { LogoInstitucion } from '../components/LogoInstitucion'
import { nombreInstitucion } from '../domain/instituciones'
import { Link, useLocation, useParams } from 'react-router-dom'
import { useRecurso } from '../hooks/useRecurso'
import { ErrorApi } from '../adapters/api'
import { EstadoError, Cargando } from '../components/EstadosConsulta'
import { Icono } from '../components/Icono'
import type { NombreIcono } from '../components/Icono'
import type { Carrera, Fuente } from '../domain/carrera'
import { etiquetaCosto, etiquetaRevision, urlFuenteSegura } from '../domain/presentacion'
import { SeleccionarCarrera } from '../components/SeleccionarCarrera'

function EstadoFuente({ fuente }: { fuente?: Fuente }) {
  const estado = fuente?.estado || 'Sin estado registrado'
  const verificado = /^verificado/i.test(estado)
  const estimado = /^estima/i.test(estado)
  return <span className={`data-status ${verificado ? 'verified' : estimado ? 'estimated' : ''}`}>
    <Icono nombre={verificado ? 'check' : 'info'} />{verificado ? 'Verificado según registro' : estimado ? 'Estimado' : 'Sin verificación registrada'}
  </span>
}

function DatoAcademico({ icono, titulo, valor, nota, fuente }: {
  icono: NombreIcono; titulo: string; valor: string; nota?: string; fuente?: Fuente
}) {
  return <div className="detail-fact"><span className="fact-icon"><Icono nombre={icono} /></span>
    <div><dt>{titulo}</dt><dd>{valor}</dd>{nota && <p>{nota}</p>}
      <EstadoFuente fuente={fuente} /></div></div>
}

export function PaginaCarrera() {
  const { id = '' } = useParams()
  const { search: busqueda } = useLocation()
  const { resultado, reintentar } = useRecurso<Carrera>(`/carreras/${encodeURIComponent(id)}`)
  const regreso = `/${busqueda}`
  if (resultado.estado === 'loading') return <><Link to={regreso} className="back-link">← Volver a resultados</Link><Cargando detalle /></>
  if (resultado.estado === 'error') return <><Link to={regreso} className="back-link">← Volver a resultados</Link>
    {resultado.error instanceof ErrorApi && resultado.error.estado === 404
      ? <section className="empty-state"><span className="state-icon"><Icono nombre="book" /></span>
        <h1>Oferta no disponible</h1><p>La alternativa ya no está publicada o el enlace es incorrecto.</p>
        <Link className="button primary" to={regreso}>Explorar alternativas</Link></section>
      : <EstadoError reintentar={reintentar} />}</>
  const c = resultado.datos
  const fuente = (campo: string) => c.fuentes.find(s => s.campo === campo)
  return <>
    <div className="breadcrumb"><Link to={regreso}>Explorar</Link><span>/</span><span>{c.nombre}</span></div>
    <Link to={regreso} className="back-link"><span aria-hidden="true">←</span> Volver a resultados</Link>
    <section className="detail-heading"><SeleccionarCarrera id={c.id} /><p className="eyebrow">CONOCE TU ALTERNATIVA</p>
      <h1>{c.nombre}</h1><div className="detail-subtitle"><LogoInstitucion codigo={c.institucion} /><span>{nombreInstitucion(c.institucion)}</span>
        <span className="tag">{c.tipoFormacion || 'Tipo no disponible'}</span></div></section>
    <div className="detail-layout"><div className="detail-main">
      {c.detalles && <PerfilAcademico detalles={c.detalles} />}
      <section className="panel" aria-labelledby="academic-title"><h2 id="academic-title">Información académica</h2>
        <dl className="detail-facts">
          <DatoAcademico titulo="Duración" icono="clock" valor={c.duracionMeses === null ? 'Dato no disponible' : `${c.duracionMeses} meses`}
            nota={c.duracionMeses === null ? 'Pendiente de registrar.' : 'Duración informada por la fuente registrada.'} fuente={fuente('Duración')} />
          <DatoAcademico titulo="Modalidad" icono="screen" valor={c.modalidad || 'Dato no disponible'} fuente={fuente('Modalidad')} />
          <DatoAcademico titulo="Ubicación / sede" icono="pin" valor={c.ubicacion || 'Dato no disponible'}
            nota="Confirma la sede y disponibilidad con la institución." />
          <DatoAcademico titulo="Costo mensual de enseñanza" icono="coins" valor={etiquetaCosto(c.costoMensualSoles)}
            nota={fuente('Costo')?.estado || 'Consulta moneda, periodo y condiciones antes de decidir.'} fuente={fuente('Costo')} />
        </dl></section>
      <section className="panel text-panel"><span className="fact-icon"><Icono nombre="book" /></span>
        <div><h2>Requisitos de ingreso</h2><p>{c.requisitos || 'Dato no disponible'}</p>
          <p className="secondary-note">Confirma el proceso vigente con la institución.</p></div></section>
      <section className="panel text-panel"><span className="fact-icon"><Icono nombre="briefcase" /></span>
        <div><h2>Campo laboral</h2><p>{c.campoLaboral || 'Dato no disponible'}</p>
          <p className="secondary-note">Consulta los ámbitos de trabajo y la información vigente con la institución.</p></div></section>
      <div className="detail-disclaimer"><Icono nombre="info" /><p>Una ficha es un punto de partida.
        Revisa las fuentes y consulta la información vigente antes de tomar una decisión.</p></div>
    </div><aside className="detail-sidebar" aria-label="Fuentes y revisión">
      <section className="panel sources-panel"><div className="panel-title"><span className="fact-icon"><Icono nombre="book" /></span><h2>Fuentes y revisión</h2></div>
        <div className="review-date"><small>Última revisión registrada</small><strong>{etiquetaRevision(c.fechaRevision)}</strong></div>
        <p className="source-intro">Consulta la procedencia y la condición de cada dato antes de decidir.</p>
        <ul className="source-list">{c.fuentes.map(s => {
          const direccion = urlFuenteSegura(s.referencia)
          return <li key={s.campo}><strong>{s.campo}</strong><EstadoFuente fuente={s} />
            {direccion ? <a href={direccion} target="_blank" rel="noopener noreferrer">Ver fuente <span className="sr-only">de {s.campo} (abre en otra pestaña)</span><Icono nombre="external" /></a>
              : <p>{s.referencia || 'Fuente no registrada'}</p>}
            <p className="source-condition">{s.estado}</p></li>
        })}</ul>
      </section>
      <section className="next-step"><Icono nombre="compass" /><h2>Sigue explorando</h2><p>Conoce otras alternativas y amplía tus posibilidades.</p>
        <Link to={regreso}>Volver al catálogo <Icono nombre="arrow" /></Link></section>
    </aside></div>
  </>
}
