import { Link } from 'react-router-dom'
import { useRecurso } from '../hooks/useRecurso'
import { LogoInstitucion } from '../components/LogoInstitucion'
import { Cargando, EstadoError } from '../components/EstadosConsulta'

interface Institucion {
  nombre: string; ofertas: number; gestion: string; tipo: string; distritos: string[]
}
export function PaginaInstituciones() {
  const { resultado, reintentar } = useRecurso<Institucion[]>('/instituciones')
  return <><section className="encabezado-instituciones"><h1>Instituciones para tu futuro</h1>
    <p>Universidades e institutos del catálogo de Lima Norte y universidades nacionales cercanas.</p></section>
    {resultado.estado === 'loading' && <Cargando />}
    {resultado.estado === 'error' && <EstadoError reintentar={reintentar} />}
    {resultado.estado === 'success' && <><p className="resumen-instituciones">{resultado.datos.length} instituciones · {resultado.datos.reduce((total, institucion) => total + institucion.ofertas, 0)} ofertas académicas</p>
      <div className="rejilla-instituciones">{resultado.datos.map(institucion => <article className="tarjeta-institucion" key={institucion.nombre}>
        <LogoInstitucion codigo={institucion.nombre} /><h2>{institucion.nombre}</h2>
        <div className="etiquetas-tarjeta"><span className="tag">{institucion.tipo}</span><span className="tag modalidad">{institucion.gestion === 'publica' ? 'Pública' : institucion.gestion === 'privada' ? 'Privada' : 'Sin gestión registrada'}</span></div>
        <p>{institucion.distritos.join(' · ')}</p><p>{institucion.ofertas} ofertas académicas</p>
        <Link className="button" to={`/?institucion=${encodeURIComponent(institucion.nombre)}`}>Explorar carreras →</Link>
      </article>)}</div></>}
  </>
}
