import { useEffect, useState } from 'react'
import { readApi } from '../adapters/api'

type Resource<T> = { status: 'loading' } | { status: 'error'; error: Error }
  | { status: 'success'; data: T }

export function useResource<T>(path: string) {
  const [attempt, setAttempt] = useState(0)
  const key = `${path}:${attempt}`
  const [stored, setStored] = useState<{ key: string; result: Resource<T> }>({ key: '', result: { status: 'loading' } })
  useEffect(() => {
    const controller = new AbortController()
    readApi<T>(path, controller.signal).then(data => {
      if (!controller.signal.aborted) setStored({ key, result: { status: 'success', data } })
    }).catch((error: unknown) => {
      if (!controller.signal.aborted) setStored({ key, result: { status: 'error',
        error: error instanceof Error ? error : new Error('Error de conexión') } })
    })
    return () => controller.abort()
  }, [path, key])
  const result: Resource<T> = stored.key === key ? stored.result : { status: 'loading' }
  return { result, retry: () => setAttempt(value => value + 1) }
}
