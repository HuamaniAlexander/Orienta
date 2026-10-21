import type { Carrera } from './carrera'

const nombres: Record<string, string> = {
  UTP: 'Universidad Tecnológica del Perú',
  UNMSM: 'Universidad Nacional Mayor de San Marcos',
  UNI: 'Universidad Nacional de Ingeniería',
  PUCP: 'Pontificia Universidad Católica del Perú',
  UPC: 'Universidad Peruana de Ciencias Aplicadas',
}
export const nombreInstitucion = (codigo: string) => nombres[codigo] || codigo
const marcasCatalogo: Record<string, string> = {
  "Universidad Privada del Norte": "/instituciones/upn-oficial.svg",
  "Universidad César Vallejo": "/instituciones/ucv-marca.ico",
  "Universidad Continental": "/instituciones/continental-oficial.svg",
  "Universidad de Ciencias y Humanidades": "/instituciones/uch-oficial.webp",
  "Universidad Católica Sedes Sapientiae": "/instituciones/ucss-marca.png",
  "Universidad Científica del Sur": "/instituciones/cientifica-oficial.svg",
  "Universidad San Ignacio de Loyola": "/instituciones/usil-marca.webp",
  "Universidad Privada Norbert Wiener": "/instituciones/wiener-oficial.svg",
  "Universidad Nacional del Callao": "/instituciones/unac-marca.png",
  "IESTP Carlos Cueto Fernandini": "/instituciones/cueto-marca.png",
  "Cibertec": "/instituciones/cibertec-marca.svg",
  "IDAT": "/instituciones/idat-oficial.png",
  "CERTUS": "/instituciones/certus-oficial.png",
  "Zegel": "/instituciones/zegel-marca.png",
  "Instituto Daniel Alcides Carrión": "/instituciones/carrion-oficial.svg",
  "INTECI – Instituto de Profesiones Empresariales": "/instituciones/inteci-oficial.png"
}
const codigoInstitucion = (valor: string) => Object.keys(nombres).find(clave => clave === valor || nombres[clave] === valor)
export const logoInstitucion = (codigo: string) => marcasCatalogo[codigo] || (codigoInstitucion(codigo) ? `/instituciones/${codigoInstitucion(codigo)!.toLowerCase()}.${codigoInstitucion(codigo) === 'UNI' ? 'png' : 'svg'}` : null)
export const etiquetaCarrera = (c: Carrera) => `${c.nombre} · ${nombreInstitucion(c.institucion)}`
