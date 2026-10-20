import type { Carrera } from './carrera'

export function portadaCarrera(carrera: Carrera) {
  const texto = `${carrera.nombre} ${carrera.detalles?.area_conocimiento || ''}`.toLocaleLowerCase('es')
  if (/software|sistemas|comput|informát|ciber|datos/.test(texto)) return 'tecnologia'
  if (/salud|medicin|enferm|farm|obstetr|odont|nutric|psicol|terapia/.test(texto)) return 'salud'
  if (/diseño|comunic|arte|publicidad|arquitect/.test(texto)) return 'creatividad'
  if (/ingenier|mecánic|electr|industrial|constr|manten/.test(texto)) return 'ingenieria'
  return 'negocios'
}
