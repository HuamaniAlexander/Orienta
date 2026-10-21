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
  detalles?: DetallesCarrera
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
  gestion?: string[]
  area?: string[]
  institucion?: string[]
}

export interface DetallesCarrera {
  institucion_id: string; carrera_id: string; nombre_institucion: string; gestion: string
  tipo_institucion: string; nombre_sede: string; distrito: string; direccion: string
  area_conocimiento: string; descripcion: string; cursos_principales: string[]
  actividades_profesionales: string[]; habilidades_recomendadas: string[]
  intereses_relacionados: string[]; especializaciones_posibles: string[]
  ciclos_academicos: number; titulo_otorgado: string; perfil_ingreso: string
  fuentes: string[]; sitio_web: string; sede_modelada_por_catalogo_institucional: boolean
  nota_documental?: string; procedencia_comparacion: Record<string, string>
  costos: { matricula_por_ciclo_soles: number; pension_mensual_soles: number; inversion_total_estimativa_soles: number }
  ingresos_laborales: { etapa_inicial_soles: { min: number; max: number }; criterio: string }
}
