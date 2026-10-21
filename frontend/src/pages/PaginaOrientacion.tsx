import { Link } from 'react-router-dom'
import { useComparacionCarreras } from '../application/seleccion'
import { CuestionarioVocacional } from '../components/CuestionarioVocacional'

export function PaginaOrientacion() {
  const { identificadores } = useComparacionCarreras()
  return <><h1>Mi orientación</h1>{identificadores.length === 2
    ? <CuestionarioVocacional key={identificadores.join(':')} identificadores={identificadores} />
    : <section className="empty-state"><h2>Selecciona dos carreras para conocerte mejor</h2><p>El cuestionario utiliza los cursos y las condiciones de las ofertas que elijas.</p><Link className="button primary" to="/">Explorar carreras</Link></section>}</>
}
