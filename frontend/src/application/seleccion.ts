import { createContext, useContext } from 'react'
export interface SeleccionComparacion {
  identificadores: string[]
  alternar: (id: string, sustituirEn?: number) => void
  limpiar: () => void
  mensaje: string
}
export const ContextoComparacion = createContext<SeleccionComparacion>({ identificadores: [], alternar: () => {}, limpiar: () => {}, mensaje: '' })
export function useComparacionCarreras() { return useContext(ContextoComparacion) }
