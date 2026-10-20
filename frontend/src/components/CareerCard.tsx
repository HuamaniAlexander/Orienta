import { Link } from 'react-router-dom'
import type { Career } from '../domain/career'
import { Icon } from './Icon'
import { SelectCareer } from './SelectCareer'

export function CareerCard({ career, search = '' }: { career: Career; search?: string }) {
  return <article className="career-card">
    <div className="card-top"><span className={`institution-mark ${career.institution === 'UTP' ? 'utp' : 'sanmarcos'}`}>
      {career.institution.slice(0, 3)}</span>
      <div><p className="institution-name">{career.institution}</p>
        <span className="tag">{career.training_type || 'Tipo no disponible'}</span></div>
    </div>
    <SelectCareer id={career.id} />
    <h3>{career.name}</h3>
    <div className="card-facts"><div><Icon name="pin" /><span><small>Ubicación</small>
      {career.location || 'Dato no disponible'}</span></div>
      <div><Icon name="screen" /><span><small>Modalidad</small>
        {career.modality || 'Dato no disponible'}</span></div></div>
    <Link className="card-link" to={`/carreras/${career.id}${search}`}>Ver ficha académica <Icon name="arrow" /></Link>
  </article>
}
