import { Link } from 'react-router-dom'
import { Icono } from '../components/Icono'

export function PaginaInicio() {
  return <><section className="inicio-vichy"><div><span className="etiqueta-seccion">TU PRÓXIMO PASO EMPIEZA AQUÍ</span>
    <h1>Conoce tus opciones.<br />Decide con información.</h1>
    <p>Explora carreras técnicas y universitarias, compara sus condiciones y reflexiona sobre tus intereses con ORIENTA.</p>
    <Link className="button primary" to="/">Explorar carreras <Icono nombre="arrow" /></Link><Link className="button" to="/instituciones">Ver instituciones</Link>
  </div><div className="imagen-inicio" role="img" aria-label="Estudiantes en un campus universitario" /></section>
  <section className="pasos-inicio" aria-label="Cómo utilizar ORIENTA"><article><Icono nombre="busqueda" /><h2>01. Explora</h2><p>Busca por carrera, institución o área y filtra según tus condiciones.</p></article>
    <article><Icono nombre="compare" /><h2>02. Compara</h2><p>Elige dos ofertas y revisa sus cursos, costos estimados, duración y fuentes.</p></article>
    <article><Icono nombre="compass" /><h2>03. Conoce tus prioridades</h2><p>Responde diez preguntas sobre tus intereses y las dos carreras seleccionadas.</p><Link to="/mi-orientacion">Ir a mi orientación →</Link></article></section></>
}
