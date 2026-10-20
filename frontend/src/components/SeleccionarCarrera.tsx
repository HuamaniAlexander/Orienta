import { useNavigate, useSearchParams } from 'react-router-dom'
import { useComparacionCarreras } from '../application/seleccion'
import { Icono } from './Icono'

export function SeleccionarCarrera({ id }: { id: string }) {
  const { identificadores, alternar } = useComparacionCarreras()
  const [parametros] = useSearchParams()
  const navegar = useNavigate()
  const sinProcesar = parametros.get('sustituir')
  const indice = sinProcesar === '0' || sinProcesar === '1' ? Number(sinProcesar) : undefined
  const seleccionado = identificadores.includes(id)
  const bloqueado = indice !== undefined && seleccionado && identificadores[indice] !== id
  return <button className={`select-career ${seleccionado ? 'selected' : ''}`} aria-pressed={seleccionado}
    disabled={bloqueado} onClick={() => {
      alternar(id, indice)
      if (indice !== undefined && !bloqueado) navegar('/comparar')
    }}><span className="selection-box">{<Icono nombre={seleccionado ? "check" : "compare"} />}</span>
      {indice !== undefined ? 'Elegir alternativa' : seleccionado ? 'Seleccionada' : 'Comparar'}</button>
}
