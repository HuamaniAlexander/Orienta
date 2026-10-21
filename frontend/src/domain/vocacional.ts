export interface OpcionVocacional { id: string; texto: string }
export interface PreguntaVocacional { id: string; seccion: string; texto: string; contexto: string; opciones: OpcionVocacional[] }
export interface Cuestionario {
  version: string; preguntas: PreguntaVocacional[]; aviso: string
  programas: { id: string; nombre: string; institucion: string }[]
}
export interface FactorPreferencia { factor: string; descripcion: string; contribucion: number; valor: number }
export interface ResultadoVocacional {
  estado: string; explicacion: string; recomendada: string | null; idRegistro: string | null
  factores: FactorPreferencia[]; factoresContrarios: FactorPreferencia[]; incertidumbres: string[]
  modelo: { version: string; algoritmo: string; significadoMargen: string } | null
}
