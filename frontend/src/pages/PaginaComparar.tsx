import { LogoInstitucion } from '../components/LogoInstitucion'
import { nombreInstitucion, etiquetaCarrera } from '../domain/instituciones'
import { Link } from 'react-router-dom'
import { useComparacionCarreras } from '../application/seleccion'
import { useRecurso } from '../hooks/useRecurso'
import { EstadoError, Cargando } from '../components/EstadosConsulta'
import { Icono } from '../components/Icono'
import type { Carrera } from '../domain/carrera'
import { etiquetaCosto } from '../domain/presentacion'
import { PanelRecomendacionIA } from '../components/PanelRecomendacionIA'

export interface ResultadoComparacion {
  izquierda: Carrera
  derecha: Carrera
  diferenciaDuracionMeses: number | null
  diferenciaCostoMensualSoles: string | null
}

function ContenidoComparacion({ identificadores }: { identificadores: string[] }) {
  const { resultado, reintentar } = useRecurso<ResultadoComparacion>('/comparaciones', { idsCarreras: identificadores })
  if (resultado.estado === 'loading') return <Cargando detalle />
  if (resultado.estado === 'error') return <EstadoError reintentar={reintentar} />
  const { izquierda, derecha, diferenciaDuracionMeses: duracion, diferenciaCostoMensualSoles: costo } = resultado.datos
  const filas = [
    ['Duración', ...[izquierda, derecha].map(c => c.duracionMeses === null ? 'Dato no disponible' : `${c.duracionMeses} meses`)],
    ['Modalidad', izquierda.modalidad, derecha.modalidad], ['Ubicación / sede', izquierda.ubicacion, derecha.ubicacion],
    ['Costo mensual de enseñanza', etiquetaCosto(izquierda.costoMensualSoles), etiquetaCosto(derecha.costoMensualSoles)],
    ['Requisitos de ingreso', izquierda.requisitos, derecha.requisitos], ['Campo laboral', izquierda.campoLaboral, derecha.campoLaboral],
  ]
  return <>
    <div className="comparison-headings"><div className="criterion-spacer" />{[izquierda, derecha].map((c, indice) =>
      <article key={c.id} className="comparison-option"><LogoInstitucion codigo={c.institucion} />
        <p>{nombreInstitucion(c.institucion)} <span className="tag">{c.tipoFormacion || 'Sin tipo'}</span></p><h2>{c.nombre}</h2>
        <div><Link to={`/carreras/${c.id}`}>Ver ficha <Icono nombre="external" /></Link>
          <Link to={`/?sustituir=${indice}`}>Sustituir</Link></div></article>)}</div>
    <section className="comparison-data" aria-label="Comparación de los seis criterios">{filas.map(([etiqueta, a, b]) =>
      <div className="comparison-row" key={etiqueta}><h3>{etiqueta}</h3><p><small>{etiquetaCarrera(izquierda)}</small>{a || 'Dato no disponible'}</p>
        <p><small>{etiquetaCarrera(derecha)}</small>{b || 'Dato no disponible'}</p></div>)}</section>
    <div className="comparison-notes"><div><Icono nombre="clock" /><p><strong>Diferencia de duración</strong>
      {duracion === null ? 'No disponible: falta información.' : duracion === 0 ? 'Ambas alternativas tienen la misma duración informada.' : `${etiquetaCarrera(derecha)} tiene ${Math.abs(duracion)} meses ${duracion > 0 ? 'más' : 'menos'} que ${etiquetaCarrera(izquierda)}.`}</p></div>
      <div><Icono nombre="coins" /><p><strong>Diferencia de importes mensuales</strong>
        {costo === null ? 'No disponible: falta información.' : Number(costo) === 0 ? 'Los importes mensuales informados son iguales.' : `${etiquetaCarrera(derecha)} tiene S/ ${Math.abs(Number(costo)).toLocaleString('es-PE')} ${Number(costo) > 0 ? 'más' : 'menos'} que ${etiquetaCarrera(izquierda)} por mes.`}
      </p></div></div>
    <div className="cost-conditions"><Icono nombre="info" /><div><strong>Condiciones de los costos</strong>
      {[izquierda, derecha].map(c => <p key={c.id}>{etiquetaCarrera(c)} · {c.fuentes.find(s => s.campo === 'Costo')?.estado || 'Condiciones pendientes de verificar'}</p>)}
      <p>Se contrastan importes de enseñanza en soles por mes. No representan el costo total de estudiar.</p></div></div>
    <PanelRecomendacionIA identificadores={identificadores} nombres={[etiquetaCarrera(izquierda), etiquetaCarrera(derecha)]} />
  </>
}

export function PaginaComparar() {
  const { identificadores, limpiar } = useComparacionCarreras()
  return <><div className="breadcrumb"><Link to="/">Explorar</Link><span>/</span>Comparador</div>
    <section className="compare-hero"><div><p className="eyebrow">DOS OPCIONES, LOS MISMOS CRITERIOS</p>
      <h1>Compara tu próximo paso.</h1><p>Revisa las diferencias y consulta las fuentes de cada alternativa.</p></div>
      {identificadores.length > 0 && <button className="button" onClick={limpiar}>Limpiar selección</button>}</section>
    {identificadores.length !== 2 ? <section className="empty-state"><span className="state-icon"><Icono nombre="compass" /></span>
      <h2>{identificadores.length ? 'Falta una alternativa' : 'Elige dos alternativas para empezar'}</h2>
      <p>Selecciona exactamente dos opciones diferentes desde el catálogo o su ficha académica.</p>
      <Link className="button primary" to="/">Explorar carreras <Icono nombre="arrow" /></Link></section>
      : <ContenidoComparacion key={identificadores.join(':')} identificadores={identificadores} />}
  </>
}
