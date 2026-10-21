import { LogoInstitucion } from './LogoInstitucion'
import { nombreInstitucion, etiquetaCarrera } from '../domain/instituciones'
import { Link } from 'react-router-dom'
import { useComparacionCarreras } from '../application/seleccion'
import { useRecurso } from '../hooks/useRecurso'
import type { Carrera } from '../domain/carrera'
import { Icono } from './Icono'

function CarreraSeleccionada({ id }: { id: string }) {
  const { alternar } = useComparacionCarreras()
  const { resultado } = useRecurso<Carrera>(`/carreras/${encodeURIComponent(id)}`)
  return <div className="tray-item">{resultado.estado === 'success' && <LogoInstitucion codigo={resultado.datos.institucion} />}<div>
    <strong>{resultado.estado === 'success' ? resultado.datos.nombre : `Alternativa ${id}`}</strong>
    <small>{resultado.estado === 'success' ? nombreInstitucion(resultado.datos.institucion) : resultado.estado === 'error' ? 'Revisa la disponibilidad' : 'Cargando…'}</small>
  </div><button onClick={() => alternar(id)} aria-label={`Quitar ${resultado.estado === 'success' ? etiquetaCarrera(resultado.datos) : id}`}>×</button></div>
}
export function BandejaComparacion() {
  const { identificadores, mensaje } = useComparacionCarreras()
  return <>{mensaje && <p className="selection-message" role="alert">{mensaje}</p>}
    {identificadores.length > 0 && <section className="comparison-tray" aria-label="Tu comparación">
      <div className="tray-title"><Icono nombre="compass" /><div><strong>Tu comparación</strong><small>{identificadores.length} de 2 seleccionadas</small></div></div>
      <div className="tray-items">{identificadores.map(id => <CarreraSeleccionada key={id} id={id} />)}</div>
      <Link className="button primary" to="/comparar" aria-label={identificadores.length === 2 ? 'Comparar alternativas' : 'Ver selección'}>
        <span className="tray-action-long">{identificadores.length === 2 ? 'Comparar alternativas' : 'Ver selección'}</span>
        <span className="tray-action-short" aria-hidden="true">{identificadores.length === 2 ? 'Comparar' : 'Selección'}</span><Icono nombre="arrow" /></Link>
    </section>}</>
}
