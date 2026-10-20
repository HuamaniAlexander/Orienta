import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'

import { ComparisonContext } from './selection'
export function ComparisonProvider({ children }: { children: ReactNode }) {
  const [ids, setIds] = useState<string[]>(() => {
    try {
      const saved: unknown = JSON.parse(sessionStorage.getItem('orienta-comparison') || '[]')
      return Array.isArray(saved) && saved.length <= 2 && saved.every(id => typeof id === 'string' && /^[A-Za-z0-9_-]{1,30}$/.test(id))
        ? [...new Set(saved)] : []
    } catch { return [] }
  })
  const [message, setMessage] = useState('')
  useEffect(() => {
    try { sessionStorage.setItem('orienta-comparison', JSON.stringify(ids)) } catch { /* Works without storage. */ }
  }, [ids])
  function toggle(id: string, replaceAt?: number) {
    if (replaceAt !== undefined && ids.includes(id) && ids[replaceAt] !== id) {
      setMessage('Esta alternativa ya está seleccionada. Elige otra diferente.'); return
    }
    if (replaceAt !== undefined && replaceAt >= 0 && replaceAt < ids.length) {
      setIds(ids.map((value, index) => index === replaceAt ? id : value))
    } else if (ids.includes(id)) setIds(ids.filter(value => value !== id))
    else if (ids.length < 2) setIds([...ids, id])
    else { setMessage('Ya elegiste dos alternativas. Quita o sustituye una para elegir otra.'); return }
    setMessage('')
  }
  return <ComparisonContext.Provider value={{ ids, toggle, clear: () => { setIds([]); setMessage('') }, message }}>{children}</ComparisonContext.Provider>
}
