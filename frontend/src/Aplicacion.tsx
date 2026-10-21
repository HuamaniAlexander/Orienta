import { PaginaInstituciones } from './pages/PaginaInstituciones'
import { BrowserRouter, Link, NavLink, Route, Routes, useLocation } from 'react-router-dom'
import { useEffect, useRef } from 'react'
import { Icono } from './components/Icono'
import { PaginaExplorar } from './pages/PaginaExplorar'
import { PaginaCarrera } from './pages/PaginaCarrera'
import { PaginaComparar } from './pages/PaginaComparar'
import { ProveedorComparacion } from './application/ProveedorComparacion'
import { useComparacionCarreras } from './application/seleccion'
import { BandejaComparacion } from './components/BandejaComparacion'

function Disposicion() {
  const { pathname } = useLocation()
  const { identificadores } = useComparacionCarreras()
  const contenidoPrincipal = useRef<HTMLElement>(null)
  useEffect(() => {
    document.title = pathname.startsWith('/carreras/') ? 'Ficha académica | ORIENTA'
      : pathname === '/comparar' ? 'Comparador | ORIENTA' : pathname === '/instituciones' ? 'Instituciones | ORIENTA' : 'Explorar carreras | ORIENTA'
    contenidoPrincipal.current?.focus()
    window.scrollTo(0, 0)
  }, [pathname])
  return <><a href="#contenido" className="skip-link">Saltar al contenido</a>
    <header className="site-header"><div className="header-inner">
      <Link to="/" className="brand" aria-label="ORIENTA, inicio"><span className="brand-symbol"><Icono nombre="compass" /></span>ORIENTA<span className="brand-dot">.</span></Link>
      <nav aria-label="Navegación principal"><NavLink to="/" end><Icono nombre="busqueda" />Explorar</NavLink>
        <NavLink to="/comparar"><Icono nombre="compare" />Comparador <span className="nav-count">{identificadores.length}</span></NavLink><NavLink to="/instituciones"><Icono nombre="institucion" />Instituciones</NavLink></nav>
      <div className="visitor"><span className="visitor-icon"><Icono nombre="usuario" /></span><span>Modo visitante<small>Sin cuenta, sin barreras</small></span></div>
    </div></header>
    <main id="contenido" ref={contenidoPrincipal} tabIndex={-1} className="page-shell"><Routes>
      <Route path="/" element={<PaginaExplorar />} />
      <Route path="/carreras/:id" element={<PaginaCarrera />} />
      <Route path="/instituciones" element={<PaginaInstituciones />} />
      <Route path="/comparar" element={<PaginaComparar />} />
      <Route path="*" element={<section className="empty-state"><h1>Página no disponible</h1><Link to="/" className="button primary">Volver a explorar</Link></section>} />
    </Routes></main>{pathname !== '/comparar' && <BandejaComparacion />}
    <footer className="site-footer"><span className="footer-brand">ORIENTA</span><span>Información clara para tu próximo paso.</span><span>MVP 1 · Proyecto académico UTP</span></footer>
  </>
}

export default function Aplicacion() { return <BrowserRouter><ProveedorComparacion><Disposicion /></ProveedorComparacion></BrowserRouter> }
