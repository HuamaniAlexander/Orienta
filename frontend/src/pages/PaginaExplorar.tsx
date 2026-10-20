import { useSearchParams } from 'react-router-dom'
import { useRecurso } from '../hooks/useRecurso'
import { TarjetaCarrera } from '../components/TarjetaCarrera'
import { EstadoError, Cargando } from '../components/EstadosConsulta'
import { Icono } from '../components/Icono'
import { Filtros } from '../components/Filtros'
import { nombresFiltros } from '../domain/filtros'
import { FormularioBusqueda } from '../components/FormularioBusqueda'
import type { ResultadoCatalogo, Facetas } from '../domain/carrera'

export function PaginaExplorar() {
  const [parametros, establecerParametros] = useSearchParams()
  const q = parametros.get('q') || ''
  const pagina = Math.max(1, Math.min(10000, Math.floor(Number(parametros.get('pagina')) || 1)))
  const consulta = new URLSearchParams({ pagina: String(pagina), limite: '12' })
  for (const clave of ['q', 'tipo', 'modalidad', 'ubicacion']) {
    if (parametros.get(clave)) consulta.set(clave, parametros.get(clave)!)
  }
  const { resultado, reintentar } = useRecurso<ResultadoCatalogo>(`/carreras?${consulta}`)
  const filtros = useRecurso<Facetas>('/filtros')
  function cambiar(clave: string, valor: string) {
    const siguiente = new URLSearchParams(parametros)
    siguiente.delete('pagina')
    if (valor) siguiente.set(clave, valor); else siguiente.delete(clave)
    establecerParametros(siguiente)
  }
  const activo = ['q', ...Object.keys(nombresFiltros)].filter(clave => parametros.get(clave))
  const limpiarFiltros = () => establecerParametros(parametros.has('sustituir') ? { sustituir: parametros.get('sustituir')! } : {})
  const busquedaRegreso = parametros.toString() ? `?${parametros}` : ''
  return <>
    <div className="breadcrumb">Inicio <span>/</span> Explorar</div>
    <section className="hero"><div><p className="eyebrow">EXPLORA TUS POSIBILIDADES</p>
      <h1>Tu futuro empieza explorando.</h1>
      <p>Conoce alternativas académicas y descubre lo que te importa.</p></div>
      <div className="hero-note"><Icono nombre="compass" /><span>Una decisión informada<br /><strong>empieza con información clara.</strong></span></div>
    </section>
    <FormularioBusqueda key={q} valorInicial={q} alBuscar={valor => cambiar('q', valor)} />
    <div className="catalog-layout">
    <Filtros valores={parametros} facetas={filtros.resultado.estado === 'success' ? filtros.resultado.datos : undefined}
      alCambiar={cambiar} limpiar={limpiarFiltros} consultaFallida={filtros.resultado.estado === 'error'} reintentar={filtros.reintentar} />
    <section className="catalog-results" aria-labelledby="catalog-title"><div className="section-heading"><div>
      <h2 id="catalog-title">Explora alternativas</h2><p>Encuentra una opción para tu próximo paso.</p>
    </div>{resultado.estado === 'success' && <span className="count" role="status">{resultado.datos.total} {resultado.datos.total === 1 ? 'alternativa' : 'alternativas'}</span>}</div>
      {activo.length > 0 && <div className="active-filters" aria-label="Filtros activos">
        {activo.map(clave => <button key={clave} onClick={() => cambiar(clave, '')}
          aria-label={`Quitar ${clave === 'q' ? 'búsqueda' : nombresFiltros[clave as keyof typeof nombresFiltros]}: ${parametros.get(clave)}`}>
          {parametros.get(clave)} <span aria-hidden="true">×</span></button>)}
      </div>}
      {resultado.estado === 'loading' && <Cargando />}
      {resultado.estado === 'error' && <EstadoError reintentar={reintentar} />}
      {resultado.estado === 'success' && <>
        {resultado.datos.total === 0 ? <div className="empty-state"><span className="state-icon"><Icono nombre="busqueda" /></span>
          <h2>{activo.length ? 'No encontramos coincidencias' : 'El catálogo aún está vacío'}</h2>
          <p>{activo.length ? 'Prueba con otro nombre o cambia los filtros de tu búsqueda.' : 'Las alternativas aparecerán cuando se importe información académica.'}</p>
          {activo.length > 0 && <button className="button primary" onClick={limpiarFiltros}>Limpiar búsqueda y filtros</button>}
        </div> : <>
          {resultado.datos.elementos.length === 0 ? <div className="empty-state"><h2>Esta página no tiene resultados</h2>
            <button className="button primary" onClick={() => cambiar('pagina', '1')}>Volver a la primera página</button></div>
            : <div className="career-grid">{resultado.datos.elementos.map(c => <TarjetaCarrera key={c.id} carrera={c} busqueda={busquedaRegreso} />)}</div>}
          {resultado.datos.total > 12 && <nav className="pagination" aria-label="Paginación del catálogo">
            <button className="button" disabled={pagina <= 1} onClick={() => establecerParametros(anterior => {
              const siguiente = new URLSearchParams(anterior); siguiente.set('pagina', String(pagina - 1)); return siguiente
            })}>Anterior</button>
            <span>Página {pagina} de {Math.ceil(resultado.datos.total / 12)}</span>
            <button className="button" disabled={pagina * 12 >= resultado.datos.total} onClick={() => establecerParametros(anterior => {
              const siguiente = new URLSearchParams(anterior); siguiente.set('pagina', String(pagina + 1)); return siguiente
            })}>Siguiente</button>
          </nav>}
        </>}
      </>}
    </section></div>
  </>
}
