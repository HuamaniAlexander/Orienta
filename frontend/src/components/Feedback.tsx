import { Icon } from './Icon'

export function Loading({ detail = false }: { detail?: boolean }) {
  return <div role="status" aria-label="Cargando información" className="skeleton-grid">
    {Array.from({ length: detail ? 2 : 6 }, (_, i) => <div key={i} className="skeleton-card">
      <div className="skeleton short" /><div className="skeleton" /><div className="skeleton" />
    </div>)}<span className="sr-only">Cargando información…</span>
  </div>
}

export function ErrorState({ retry, message }: { retry: () => void; message?: string }) {
  return <section className="empty-state" role="alert">
    <span className="state-icon"><Icon name="info" /></span>
    <h2>No pudimos cargar la información</h2>
    <p>{message || 'Revisa tu conexión a internet y vuelve a intentarlo.'}</p>
    <button className="button primary" onClick={retry}><Icon name="reset" /> Reintentar</button>
  </section>
}
