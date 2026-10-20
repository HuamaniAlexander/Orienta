import type { Career } from '../domain/career'
export const career: Career = {
  id: 'C01', name: 'Ingeniería de Software', institution: 'UTP', training_type: 'Universitaria',
  modality: 'Presencial', location: 'Campus Lima Norte', duration_months: 60,
  monthly_cost_pen: '775', requirements: 'Secundaria completa', employment: 'Software',
  reviewed_on: '2026-10-13', sources: [{ field: 'Costo', reference: 'Referencia del usuario', status: 'Estimado' }],
}
