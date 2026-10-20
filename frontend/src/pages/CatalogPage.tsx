import { useResource } from '../application/useResource'
import { CareerCard } from '../components/CareerCard'
import { ErrorState, Loading } from '../components/Feedback'
import { Icon } from '../components/Icon'
import type { CatalogResult } from '../domain/career'

export function CatalogPage() {
  const { result, retry } = useResource<CatalogResult>('/carreras?limite=100')
  return <>
    <div className="breadcrumb">Inicio <span>/</span> Explorar</div>
    <section className="hero"><div><p className="eyebrow">EXPLORA TUS POSIBILIDADES</p>
      <h1>Tu futuro empieza explorando.</h1>
      <p>Conoce alternativas académicas y descubre lo que te importa.</p></div>
      <div className="hero-note"><Icon name="compass" /><span>Una decisión informada<br /><strong>empieza con información clara.</strong></span></div>
    </section>
    <section aria-labelledby="catalog-title"><div className="section-heading"><div>
      <h2 id="catalog-title">Explora alternativas</h2><p>Información académica en un solo lugar.</p>
    </div>{result.status === 'success' && <span className="count">{result.data.total} alternativas</span>}</div>
      {result.status === 'loading' && <Loading />}
      {result.status === 'error' && <ErrorState retry={retry} />}
      {result.status === 'success' && <>
        {result.data.data_mode === 'demo' && <div className="demo-notice"><Icon name="info" />
          Demostración con datos de la PoC. Los estados de verificación corresponden al archivo fuente.</div>}
        {result.data.total === 0 ? <div className="empty-state"><h2>El catálogo aún está vacío</h2>
          <p>Las alternativas aparecerán cuando se importe información académica.</p></div>
          : <div className="career-grid">{result.data.items.map(c => <CareerCard key={c.id} career={c} />)}</div>}
      </>}
    </section>
  </>
}
