export interface Fuente {
  campo: string
  referencia: string | null
  estado: string
}

export interface Carrera {
  id: string
  nombre: string
  institucion: string
  tipoFormacion: string | null
  modalidad: string | null
  ubicacion: string | null
  duracionMeses: number | null
  costoMensualSoles: string | null
  requisitos: string | null
  campoLaboral: string | null
  fechaRevision: string | null
  fuentes: Fuente[]
}

export interface ResultadoCatalogo {
  elementos: Carrera[]
  total: number
  pagina: number
  limite: number
  modoDatos: 'postgres' | 'demo'
}

export interface Facetas {
  tipo: string[]
  modalidad: string[]
  ubicacion: string[]
}
