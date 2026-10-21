import type { Carrera } from './carrera'

export function portadaCarrera(carrera: Carrera) {
  const texto = `${carrera.nombre} ${carrera.detalles?.area_conocimiento || ''}`.toLocaleLowerCase('es')
  if (/gastronom|cocina|culinari|panader/.test(texto)) return 'gastronomia'
  if (/psicol/.test(texto)) return 'psicologia'
  if (/arquitect|diseño de interiores/.test(texto)) return 'arquitectura'
  if (/mecánic|mecanic|automotriz/.test(texto)) return 'mecanica'
  if (/medicin|odont|obstetr|farm|nutric|terapia/.test(texto)) return 'medicina'
  if (/software|sistemas|comput|informát|ciber|datos/.test(texto)) return 'tecnologia'
  if (/salud|medicin|enferm|farm|obstetr|odont|nutric|psicol|terapia/.test(texto)) return 'enfermeria'
  if (/diseño|comunic|arte|publicidad|arquitect/.test(texto)) return 'creatividad'
  if (/ingenier|mecánic|electr|industrial|constr|manten/.test(texto)) return 'ingenieria'
  return 'negocios'
}
