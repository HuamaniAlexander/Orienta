import { Icono } from './Icono'
import { logoInstitucion, nombreInstitucion } from '../domain/instituciones'

export function LogoInstitucion({ codigo }: { codigo: string }) {
  const origenImagen = logoInstitucion(codigo)
  return origenImagen ? <img className={`university-logo university-${origenImagen.split('/').pop()?.split('.')[0]}`} src={origenImagen}
    alt={nombreInstitucion(codigo)} width="128" height="54" loading="lazy" /> : <span className="emblema-institucion" aria-hidden="true"><Icono nombre="institucion" /></span>
}
