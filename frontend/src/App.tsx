import { BrowserRouter, Link, NavLink, Route, Routes, useLocation } from 'react-router-dom'
import { useEffect, useRef } from 'react'
import { Icon } from './components/Icon'
import { CatalogPage } from './pages/CatalogPage'
import { CareerPage } from './pages/CareerPage'

function Layout() {
  const { pathname } = useLocation()
  const main = useRef<HTMLElement>(null)
  useEffect(() => {
    document.title = pathname.startsWith('/carreras/') ? 'Ficha académica | ORIENTA' : 'Explorar carreras | ORIENTA'
    main.current?.focus()
    window.scrollTo(0, 0)
  }, [pathname])
  return <><a href="#contenido" className="skip-link">Saltar al contenido</a>
    <header className="site-header"><div className="header-inner">
      <Link to="/" className="brand" aria-label="ORIENTA, inicio"><span className="brand-symbol"><Icon name="compass" /></span>ORIENTA<span className="brand-dot">.</span></Link>
      <nav aria-label="Navegación principal"><NavLink to="/" end><Icon name="compass" />Explorar carreras</NavLink></nav>
      <div className="visitor"><span className="visitor-icon"><Icon name="user" /></span><span>Modo visitante<small>Sin cuenta, sin barreras</small></span></div>
    </div></header>
    <main id="contenido" ref={main} tabIndex={-1} className="page-shell"><Routes>
      <Route path="/" element={<CatalogPage />} />
      <Route path="/carreras/:id" element={<CareerPage />} />
      <Route path="*" element={<section className="empty-state"><h1>Página no disponible</h1><Link to="/" className="button primary">Volver a explorar</Link></section>} />
    </Routes></main>
    <footer className="site-footer"><span className="footer-brand">ORIENTA</span><span>Información clara para tu próximo paso.</span><span>MVP 1 · Proyecto académico UTP</span></footer>
  </>
}

export default function App() { return <BrowserRouter><Layout /></BrowserRouter> }
