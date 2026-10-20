import { LogoInstitucion } from './LogoInstitucion'
import { nombreInstitucion } from '../domain/instituciones'
import { Link } from 'react-router-dom'
import type { Carrera } from '../domain/carrera'
import { Icono } from './Icono'
import { SeleccionarCarrera } from './SeleccionarCarrera'

export function TarjetaCarrera({ carrera, busqueda = '' }: { carrera: Carrera; busqueda?: string }) {
  return <article className="career-card">
    <div className="card-top"><LogoInstitucion codigo={carrera.institucion} />
      <div><p className="institution-name">{nombreInstitucion(carrera.institucion)}</p>
        <span className="tag">{carrera.tipoFormacion || 'Tipo no disponible'}</span></div>
    </div>
    <SeleccionarCarrera id={carrera.id} />
    <h3>{carrera.nombre}</h3>
    <div className="card-facts"><div><Icono nombre="pin" /><span><small>Ubicación</small>
      {carrera.ubicacion || 'Dato no disponible'}</span></div>
      <div><Icono nombre="screen" /><span><small>Modalidad</small>
        {carrera.modalidad || 'Dato no disponible'}</span></div></div>
    <Link className="card-link" to={`/carreras/${carrera.id}${busqueda}`}>Ver ficha académica <Icono nombre="arrow" /></Link>
  </article>
}
