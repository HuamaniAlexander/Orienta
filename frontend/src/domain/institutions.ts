import type { Career } from './career'

const names: Record<string, string> = {
  UTP: 'Universidad Tecnológica del Perú',
  UNMSM: 'Universidad Nacional Mayor de San Marcos',
  UNI: 'Universidad Nacional de Ingeniería',
  PUCP: 'Pontificia Universidad Católica del Perú',
  UPC: 'Universidad Peruana de Ciencias Aplicadas',
}
export const institutionName = (code: string) => names[code] || code
export const institutionLogo = (code: string) => names[code] ? `/institutions/${code.toLowerCase()}.${code === 'UNI' ? 'png' : 'svg'}` : null
export const careerLabel = (c: Career) => `${c.name} · ${institutionName(c.institution)}`
