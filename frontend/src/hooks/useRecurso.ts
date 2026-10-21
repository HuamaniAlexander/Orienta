import { useEffect, useState } from 'react'
import { consultarApi } from '../adapters/api'

type Recurso<T> = { estado: 'loading' } | { estado: 'error'; error: Error }
  | { estado: 'success'; datos: T }

export function useRecurso<T>(ruta: string, cuerpo?: unknown) {
  const carga = cuerpo === undefined ? undefined : JSON.stringify(cuerpo)
  const [intento, establecerIntento] = useState(0)
  const clave = `${ruta}:${carga}:${intento}`
  const [guardado, establecerGuardado] = useState<{ clave: string; resultado: Recurso<T> }>({ clave: '', resultado: { estado: 'loading' } })
  useEffect(() => {
    const controlador = new AbortController()
    consultarApi<T>(ruta, controlador.signal, carga === undefined ? undefined : JSON.parse(carga)).then(datos => {
      if (!controlador.signal.aborted) establecerGuardado({ clave, resultado: { estado: 'success', datos } })
    }).catch((error: unknown) => {
      if (!controlador.signal.aborted) establecerGuardado({ clave, resultado: { estado: 'error',
        error: error instanceof Error ? error : new Error('Error de conexión') } })
    })
    return () => controlador.abort()
  }, [ruta, carga, clave])
  const resultado: Recurso<T> = guardado.clave === clave ? guardado.resultado : { estado: 'loading' }
  return { resultado, reintentar: () => establecerIntento(valor => valor + 1) }
}
