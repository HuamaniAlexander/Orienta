export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

const base = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')

export async function readApi<T>(path: string, signal: AbortSignal): Promise<T> {
  const response = await fetch(`${base}/api${path}`, {
    signal: AbortSignal.any([signal, AbortSignal.timeout(12000)]),
    headers: { Accept: 'application/json' },
  })
  if (!response.ok) {
    throw new ApiError(response.status, response.status === 404
      ? 'Esta oferta no está disponible.'
      : 'No pudimos consultar la información. Inténtalo nuevamente.')
  }
  return response.json() as Promise<T>
}
