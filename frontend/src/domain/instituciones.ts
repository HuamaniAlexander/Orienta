import type { Carrera } from './carrera'

const nombres: Record<string, string> = {
  UTP: 'Universidad Tecnológica del Perú',
  UNMSM: 'Universidad Nacional Mayor de San Marcos',
  UNI: 'Universidad Nacional de Ingeniería',
  PUCP: 'Pontificia Universidad Católica del Perú',
  UPC: 'Universidad Peruana de Ciencias Aplicadas',
}
export const nombreInstitucion = (codigo: string) => nombres[codigo] || codigo
export const logoInstitucion = (codigo: string) => nombres[codigo] ? `/instituciones/${codigo.toLowerCase()}.${codigo === 'UNI' ? 'png' : 'svg'}` : null
export const etiquetaCarrera = (c: Carrera) => `${c.nombre} · ${nombreInstitucion(c.institucion)}`
