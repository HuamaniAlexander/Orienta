import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './catalogo.css'
import './ficha.css'
import './comparacion.css'
import './analisis.css'
import './tipografia.css'
import Aplicacion from './Aplicacion'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Aplicacion />
  </StrictMode>,
)
