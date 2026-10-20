import { logoInstitucion, nombreInstitucion } from '../domain/instituciones'

export function LogoInstitucion({ codigo }: { codigo: string }) {
  const origenImagen = logoInstitucion(codigo)
  return origenImagen ? <img className={`university-logo university-${codigo.toLowerCase()}`} src={origenImagen}
    alt={nombreInstitucion(codigo)} width="128" height="54" loading="lazy" /> : null
}
