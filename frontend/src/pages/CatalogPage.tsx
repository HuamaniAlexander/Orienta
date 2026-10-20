import { useSearchParams } from 'react-router-dom'
import { useResource } from '../application/useResource'
import { CareerCard } from '../components/CareerCard'
import { ErrorState, Loading } from '../components/Feedback'
import { Icon } from '../components/Icon'
import { Filters } from '../components/Filters'
import { filterNames } from '../domain/filters'
import { SearchForm } from '../components/SearchForm'
import type { CatalogResult, Facets } from '../domain/career'

export function CatalogPage() {
  const [params, setParams] = useSearchParams()
  const q = params.get('q') || ''
  const page = Math.max(1, Math.min(10000, Math.floor(Number(params.get('pagina')) || 1)))
  const query = new URLSearchParams({ pagina: String(page), limite: '12' })
  for (const key of ['q', 'tipo', 'modalidad', 'ubicacion']) {
    if (params.get(key)) query.set(key, params.get(key)!)
  }
  const { result, retry } = useResource<CatalogResult>(`/carreras?${query}`)
  const filters = useResource<Facets>('/filtros')
  function change(key: string, value: string) {
    const next = new URLSearchParams(params)
    next.delete('pagina')
    if (value) next.set(key, value); else next.delete(key)
    setParams(next)
  }
  const active = ['q', ...Object.keys(filterNames)].filter(key => params.get(key))
  const returnSearch = params.toString() ? `?${params}` : ''
  return <>
    <div className="breadcrumb">Inicio <span>/</span> Explorar</div>
    <section className="hero"><div><p className="eyebrow">EXPLORA TUS POSIBILIDADES</p>
      <h1>Tu futuro empieza explorando.</h1>
      <p>Conoce alternativas académicas y descubre lo que te importa.</p></div>
      <div className="hero-note"><Icon name="compass" /><span>Una decisión informada<br /><strong>empieza con información clara.</strong></span></div>
    </section>
    <SearchForm key={q} initial={q} onSearch={value => change('q', value)} />
    <div className="catalog-layout">
    <Filters values={params} facets={filters.result.status === 'success' ? filters.result.data : undefined}
      onChange={change} clear={() => setParams({})} failed={filters.result.status === 'error'} retry={filters.retry} />
    <section className="catalog-results" aria-labelledby="catalog-title"><div className="section-heading"><div>
      <h2 id="catalog-title">Explora alternativas</h2><p>Encuentra una opción para tu próximo paso.</p>
    </div>{result.status === 'success' && <span className="count" role="status">{result.data.total} {result.data.total === 1 ? 'alternativa' : 'alternativas'}</span>}</div>
      {active.length > 0 && <div className="active-filters" aria-label="Filtros activos">
        {active.map(key => <button key={key} onClick={() => change(key, '')}
          aria-label={`Quitar ${key === 'q' ? 'búsqueda' : filterNames[key as keyof typeof filterNames]}: ${params.get(key)}`}>
          {params.get(key)} <span aria-hidden="true">×</span></button>)}
      </div>}
      {result.status === 'loading' && <Loading />}
      {result.status === 'error' && <ErrorState retry={retry} />}
      {result.status === 'success' && <>
        {result.data.data_mode === 'demo' && <div className="demo-notice"><Icon name="info" />
          Demostración con datos de la PoC. Los estados de verificación corresponden al archivo fuente.</div>}
        {result.data.total === 0 ? <div className="empty-state"><span className="state-icon"><Icon name="search" /></span>
          <h2>{active.length ? 'No encontramos coincidencias' : 'El catálogo aún está vacío'}</h2>
          <p>{active.length ? 'Prueba con otro nombre o cambia los filtros de tu búsqueda.' : 'Las alternativas aparecerán cuando se importe información académica.'}</p>
          {active.length > 0 && <button className="button primary" onClick={() => setParams({})}>Limpiar búsqueda y filtros</button>}
        </div> : <>
          <div className="career-grid">{result.data.items.map(c => <CareerCard key={c.id} career={c} search={returnSearch} />)}</div>
          {result.data.total > 12 && <nav className="pagination" aria-label="Paginación del catálogo">
            <button className="button" disabled={page <= 1} onClick={() => setParams(prev => {
              const next = new URLSearchParams(prev); next.set('pagina', String(page - 1)); return next
            })}>Anterior</button>
            <span>Página {page} de {Math.ceil(result.data.total / 12)}</span>
            <button className="button" disabled={page * 12 >= result.data.total} onClick={() => setParams(prev => {
              const next = new URLSearchParams(prev); next.set('pagina', String(page + 1)); return next
            })}>Siguiente</button>
          </nav>}
        </>}
      </>}
    </section></div>
  </>
}
