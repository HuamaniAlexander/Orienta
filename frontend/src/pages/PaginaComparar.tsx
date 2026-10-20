import { useState } from 'react'
import { Link } from 'react-router-dom'
import { LogoInstitucion } from '../components/LogoInstitucion'
import { nombreInstitucion, etiquetaCarrera } from '../domain/instituciones'
import { portadaCarrera } from '../domain/portadas'
import { useComparacionCarreras } from '../application/seleccion'
import { useRecurso } from '../hooks/useRecurso'
import { EstadoError, Cargando } from '../components/EstadosConsulta'
import { Icono } from '../components/Icono'
import type { NombreIcono } from '../components/Icono'
import type { Carrera } from '../domain/carrera'
import { etiquetaCosto } from '../domain/presentacion'
import { PanelRecomendacionIA } from '../components/PanelRecomendacionIA'

export interface ResultadoComparacion {
  izquierda: Carrera; derecha: Carrera
  diferenciaDuracionMeses: number | null; diferenciaCostoMensualSoles: string | null
}
const pestanas: { nombre: string; icono: NombreIcono }[] = [
  { nombre: 'Información general', icono: 'compare' }, { nombre: 'Malla curricular', icono: 'book' },
  { nombre: 'Campo laboral', icono: 'briefcase' }, { nombre: 'Costo y duración', icono: 'clock' },
  { nombre: 'Recomendación IA', icono: 'sparkles' },
]
function TarjetaComparacion({ carrera: c, indice }: { carrera: Carrera; indice: number }) {
  return <article className="opcion-comparacion">
    <div className={`portada-carrera portada-${portadaCarrera(c)}`} aria-hidden="true" />
    <div className="identidad-comparacion"><LogoInstitucion codigo={c.institucion} /><div><h2>{c.nombre}</h2>
      <p>{nombreInstitucion(c.institucion)}</p><p><Icono nombre="pin" /> {c.ubicacion}</p>
      <div className="etiquetas-tarjeta"><span className="tag">{c.tipoFormacion}</span><span className="tag modalidad">{c.modalidad}</span></div></div></div>
    <p className="resumen-comparacion">{c.detalles?.descripcion || c.campoLaboral}</p>
    <dl className="datos-resumidos"><div><Icono nombre="clock" /><dt>Duración</dt><dd>{c.duracionMeses ? `${c.duracionMeses / 12} años` : 'Por confirmar'}</dd></div>
      <div><Icono nombre="coins" /><dt>Pensión mensual estimada</dt><dd>{etiquetaCosto(c.costoMensualSoles)}</dd></div>
      <div><Icono nombre="briefcase" /><dt>Campo laboral</dt><dd>{c.campoLaboral || 'Por confirmar'}</dd></div>
      <div><Icono nombre="book" /><dt>Formación</dt><dd>{c.detalles?.titulo_otorgado || c.tipoFormacion || 'Por confirmar'}</dd></div></dl>
    <div className="acciones-comparacion"><Link className="button primary" to={`/carreras/${c.id}`}>Ver ficha <Icono nombre="arrow" /></Link><Link className="button" to={`/?sustituir=${indice}`}>Cambiar carrera</Link></div>
  </article>
}
function ContenidoComparacion({ identificadores }: { identificadores: string[] }) {
  const [pestana, establecerPestana] = useState(0)
  const { resultado, reintentar } = useRecurso<ResultadoComparacion>('/comparaciones', { idsCarreras: identificadores })
  if (resultado.estado === 'loading') return <Cargando detalle />
  if (resultado.estado === 'error') return <EstadoError reintentar={reintentar} />
  const { izquierda, derecha, diferenciaDuracionMeses: duracion, diferenciaCostoMensualSoles: costo } = resultado.datos
  const carreras = [izquierda, derecha]
  const filasGenerales = [
    ['Tipo de formación', ...carreras.map(c => c.tipoFormacion)],
    ['Área de conocimiento', ...carreras.map(c => c.detalles?.area_conocimiento)],
    ['Duración', ...carreras.map(c => c.duracionMeses ? `${c.duracionMeses} meses` : null)],
    ['Modalidad', izquierda.modalidad, derecha.modalidad], ['Ubicación / sede', izquierda.ubicacion, derecha.ubicacion],
    ['Costo mensual de enseñanza', etiquetaCosto(izquierda.costoMensualSoles), etiquetaCosto(derecha.costoMensualSoles)],
    ['Requisitos de ingreso', izquierda.requisitos, derecha.requisitos], ['Campo laboral', izquierda.campoLaboral, derecha.campoLaboral],
  ]
  const filas = pestana === 1 ? [
    ['Cursos principales', ...carreras.map(c => c.detalles?.cursos_principales.join(', '))],
    ['Habilidades recomendadas', ...carreras.map(c => c.detalles?.habilidades_recomendadas.join(', '))],
    ['Título que otorga', ...carreras.map(c => c.detalles?.titulo_otorgado)],
  ] : pestana === 2 ? [
    ['Campo laboral', izquierda.campoLaboral, derecha.campoLaboral],
    ['Actividades profesionales', ...carreras.map(c => c.detalles?.actividades_profesionales.join('; '))],
    ['Especializaciones', ...carreras.map(c => c.detalles?.especializaciones_posibles.join(', '))],
  ] : pestana === 3 ? [
    filasGenerales[2], filasGenerales[5],
    ['Matrícula estimada por ciclo', ...carreras.map(c => c.detalles ? `S/ ${c.detalles.costos.matricula_por_ciclo_soles}` : null)],
    ['Inversión total estimada', ...carreras.map(c => c.detalles ? `S/ ${c.detalles.costos.inversion_total_estimativa_soles.toLocaleString('es-PE')}` : null)],
  ] : filasGenerales
  return <>
    <div className="cabecera-comparacion"><TarjetaComparacion carrera={izquierda} indice={0} /><span className="versus">VS</span><TarjetaComparacion carrera={derecha} indice={1} />
      <aside className="orientacion-resumen"><h2><Icono nombre="sparkles" /> Orientación de ORIENTA</h2><span className="tag">Diferencias para decidir</span>
        <h3>Tu elección empieza por tus prioridades</h3><p>Contrasta ambas carreras y revisa qué cambia en tu tiempo, presupuesto y formación.</p>
        <ul><li><Icono nombre="check" />{duracion === 0 ? 'Ambas carreras tienen la misma duración registrada. Compara horarios y carga académica.' : duracion === null ? 'Confirma la duración antes de planificar tus estudios.' : `${(izquierda.duracionMeses || 0) < (derecha.duracionMeses || 0) ? izquierda.nombre : derecha.nombre} tiene una duración menor; revisa también su nivel de formación.`}</li>
          <li><Icono nombre="check" />{Number(costo) === 0 && costo !== null ? 'Los importes mensuales informados son iguales.' : 'Compara pensiones, matrícula, materiales y traslados para calcular tu presupuesto.'}</li>
          <li><Icono nombre="check" />Revisa cursos y actividades profesionales para contrastar tus intereses.</li></ul>
        <a className="button" href="#orientacion-detallada"><Icono nombre="sparkles" /> Analizar los seis criterios</a>
        <p className="nota-procedencia">Los importes del catálogo ampliado son estimaciones; confirma tarifas y disponibilidad con cada institución.</p>
      </aside></div>
    <div className="pestanas-comparacion" role="tablist" aria-label="Detalles de la comparación">{pestanas.map((item, indice) => <button key={item.nombre} role="tab" id={`pestana-${indice}`} aria-selected={pestana === indice} aria-controls="detalle-comparacion" onClick={() => establecerPestana(indice)}><Icono nombre={item.icono} />{item.nombre}</button>)}</div>
    <section id="detalle-comparacion" role="tabpanel" aria-labelledby={`pestana-${pestana}`}>
      {pestana !== 4 && <section className="tabla-comparacion" aria-label="Comparación de los seis criterios"><h2><Icono nombre="book" /> Comparación detallada</h2><div className="contenedor-tabla"><table><thead><tr><th>Característica</th>{carreras.map(c => <th key={c.id}>{c.nombre}<small>{nombreInstitucion(c.institucion)}</small></th>)}</tr></thead><tbody>{filas.map(([etiqueta, a, b]) => <tr key={etiqueta}><th scope="row">{etiqueta}</th><td>{a || 'Dato no disponible'}</td><td>{b || 'Dato no disponible'}</td></tr>)}</tbody></table></div>
      <p className="nota-procedencia">Cursos y actividades: síntesis académica. Consulta la malla oficial en las fuentes de cada ficha.</p></section>}
    <div id="orientacion-detallada"><PanelRecomendacionIA identificadores={identificadores} nombres={carreras.map(etiquetaCarrera)} /></div>
    </section>
  </>
}
export function PaginaComparar() {
  const { identificadores, limpiar } = useComparacionCarreras()
  return <><section className="compare-hero"><div><h1>Comparar 2 carreras</h1><p>Analiza las diferencias entre dos carreras y contrasta seis criterios<br className="salto-escritorio" /> para descubrir cuál se adapta mejor a tus intereses, recursos y metas.</p></div>
    {identificadores.length > 0 && <div className="acciones-cabecera"><Link className="button" to="/">Cambiar carreras</Link><button className="button" onClick={limpiar}>Limpiar selección</button></div>}</section>
    {identificadores.length !== 2 ? <section className="empty-state"><span className="state-icon"><Icono nombre="compass" /></span><h2>{identificadores.length ? 'Falta una alternativa' : 'Elige dos alternativas para empezar'}</h2><p>Selecciona exactamente dos opciones diferentes desde el catálogo o su ficha académica.</p><Link className="button primary" to="/">Explorar carreras <Icono nombre="arrow" /></Link></section> : <ContenidoComparacion key={identificadores.join(':')} identificadores={identificadores} />}
  </>
}
