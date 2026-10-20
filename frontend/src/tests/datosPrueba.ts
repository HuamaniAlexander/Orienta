import type { Carrera } from '../domain/carrera'
export const carrera: Carrera = {
  id: 'C01', nombre: 'Ingeniería de Software', institucion: 'UTP', tipoFormacion: 'Universitaria',
  modalidad: 'Presencial', ubicacion: 'Campus Lima Norte', duracionMeses: 60,
  costoMensualSoles: '775', requisitos: 'Secundaria completa', campoLaboral: 'Software',
  fechaRevision: '2026-10-13', fuentes: [{ campo: 'Costo', referencia: 'Referencia del usuario', estado: 'Estimado' }],
}
