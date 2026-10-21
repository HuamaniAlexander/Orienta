import { LogoInstitucion } from './LogoInstitucion'
import { nombreInstitucion } from '../domain/instituciones'
import { Link } from 'react-router-dom'
import type { Carrera } from '../domain/carrera'
import { Icono } from './Icono'
import { SeleccionarCarrera } from './SeleccionarCarrera'
import { portadaCarrera } from '../domain/portadas'

export function TarjetaCarrera({ carrera, busqueda = '' }: { carrera: Carrera; busqueda?: string }) {
  return <article className="career-card">
    <div className={`portada-carrera portada-${portadaCarrera(carrera)}`} aria-hidden="true" />
    <div className="contenido-tarjeta">
    <h3>{carrera.nombre}</h3>
    <div className="institucion-tarjeta"><LogoInstitucion codigo={carrera.institucion} /><p className="institution-name">{nombreInstitucion(carrera.institucion)}</p></div>
    <p className="ubicacion-tarjeta"><Icono nombre="pin" />{carrera.ubicacion || 'Dato no disponible'}</p>
    <div className="etiquetas-tarjeta"><span className="tag">{carrera.tipoFormacion || 'Tipo no disponible'}</span><span className="tag modalidad">{carrera.modalidad || 'Sin modalidad'}</span></div>
    <p className="descripcion-tarjeta">{carrera.detalles?.descripcion || carrera.campoLaboral || 'Consulta la ficha académica y sus fuentes.'}</p>
    <div className="acciones-tarjeta"><Link className="card-link" aria-label="Ver ficha académica" to={`/carreras/${carrera.id}${busqueda}`}>Ver ficha <Icono nombre="arrow" /></Link><SeleccionarCarrera id={carrera.id} /></div>
    </div>
  </article>
}
