export interface Source {
  field: string
  reference: string | null
  status: string
}

export interface Career {
  id: string
  name: string
  institution: string
  training_type: string | null
  modality: string | null
  location: string | null
  duration_months: number | null
  monthly_cost_pen: string | null
  requirements: string | null
  employment: string | null
  reviewed_on: string | null
  sources: Source[]
}

export interface CatalogResult {
  items: Career[]
  total: number
  pagina: number
  limite: number
  data_mode: 'postgres' | 'demo'
}

export interface Facets {
  tipo: string[]
  modalidad: string[]
  ubicacion: string[]
}
