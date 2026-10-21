import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'

import { ContextoComparacion } from './seleccion'
export function ProveedorComparacion({ children }: { children: ReactNode }) {
  const [identificadores, establecerIdentificadores] = useState<string[]>(() => {
    try {
      const guardada: unknown = JSON.parse(sessionStorage.getItem('orienta-comparison') || '[]')
      return Array.isArray(guardada) && guardada.length <= 2 && guardada.every(id => typeof id === 'string' && /^[A-Za-z0-9_-]{1,150}$/.test(id))
        ? [...new Set(guardada)] : []
    } catch { return [] }
  })
  const [mensaje, establecerMensaje] = useState('')
  useEffect(() => {
    try { sessionStorage.setItem('orienta-comparison', JSON.stringify(identificadores)) } catch { /* Funciona aunque el almacenamiento no esté disponible. */ }
  }, [identificadores])
  function alternar(id: string, sustituirEn?: number) {
    if (sustituirEn !== undefined && identificadores.includes(id) && identificadores[sustituirEn] !== id) {
      establecerMensaje('Esta alternativa ya está seleccionada. Elige otra diferente.'); return
    }
    if (sustituirEn !== undefined && sustituirEn >= 0 && sustituirEn < identificadores.length) {
      establecerIdentificadores(identificadores.map((valor, indice) => indice === sustituirEn ? id : valor))
    } else if (identificadores.includes(id)) establecerIdentificadores(identificadores.filter(valor => valor !== id))
    else if (identificadores.length < 2) establecerIdentificadores([...identificadores, id])
    else { establecerMensaje('Ya elegiste dos alternativas. Quita o sustituye una para elegir otra.'); return }
    establecerMensaje('')
  }
  return <ContextoComparacion.Provider value={{ identificadores, alternar, limpiar: () => { establecerIdentificadores([]); establecerMensaje('') }, mensaje }}>{children}</ContextoComparacion.Provider>
}
