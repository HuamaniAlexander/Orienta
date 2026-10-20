import { Icono } from './Icono'

export function Cargando({ detalle = false }: { detalle?: boolean }) {
  return <div role="status" aria-label="Cargando información" className="skeleton-grid">
    {Array.from({ length: detalle ? 2 : 6 }, (_, i) => <div key={i} className="skeleton-card">
      <div className="skeleton short" /><div className="skeleton" /><div className="skeleton" />
    </div>)}<span className="sr-only">Cargando información…</span>
  </div>
}

export function EstadoError({ reintentar, mensaje }: { reintentar: () => void; mensaje?: string }) {
  return <section className="empty-state" role="alert">
    <span className="state-icon"><Icono nombre="info" /></span>
    <h2>No pudimos cargar la información</h2>
    <p>{mensaje || 'Revisa tu conexión a internet y vuelve a intentarlo.'}</p>
    <button className="button primary" onClick={reintentar}><Icono nombre="reset" /> Reintentar</button>
  </section>
}
