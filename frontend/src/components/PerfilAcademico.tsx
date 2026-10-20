import type { DetallesCarrera } from '../domain/carrera'
import { urlFuenteSegura } from '../domain/presentacion'

export function PerfilAcademico({ detalles }: { detalles: DetallesCarrera }) {
  return <section className="panel perfil-academico">
    <h2>Conoce la carrera</h2><p>{detalles.descripcion}</p>
    <h3>Cursos principales</h3>
    <div className="etiquetas-tarjeta">{detalles.cursos_principales.map(curso =>
      <span className="tag" key={curso}>{curso}</span>)}</div>
    <h3>Actividades profesionales</h3>
    <ul>{detalles.actividades_profesionales.map(actividad => <li key={actividad}>{actividad}</li>)}</ul>
    <h3>Perfil de ingreso</h3><p>{detalles.perfil_ingreso}</p>
    <h3>Sede</h3><p>{detalles.nombre_sede} · {detalles.direccion}</p>
    {detalles.sede_modelada_por_catalogo_institucional && <p className="nota-procedencia">
      La sede fue modelada en el catálogo: confirma que la carrera se ofrece en este local.</p>}
    <h3>Inversión total estimada</h3>
    <p>S/ {detalles.costos.inversion_total_estimativa_soles.toLocaleString('es-PE')} · Incluye los componentes
      calculados de matrícula, pensiones y materiales del catálogo; no es un tarifario oficial.</p>
    <h3>Fuentes institucionales</h3>
    {detalles.fuentes.map(referencia => {
      const enlace = urlFuenteSegura(referencia)
      return enlace ? <p key={referencia}><a href={enlace} target="_blank" rel="noopener noreferrer">
        {referencia} ↗</a></p> : null
    })}
    {detalles.nota_documental && <p className="nota-procedencia">{detalles.nota_documental}</p>}
  </section>
}
