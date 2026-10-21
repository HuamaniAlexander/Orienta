import { internalizarRespuesta, externalizarSolicitud } from './contratosApi'
export class ErrorApi extends Error {
  estado: number
  constructor(estado: number, mensaje: string) {
    super(mensaje)
    this.estado = estado
  }
}

const base = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')

export async function consultarApi<T>(ruta: string, senal: AbortSignal, cuerpo?: unknown): Promise<T> {
  const respuesta = await fetch(`${base}/api${ruta}`, {
    signal: AbortSignal.any([senal, AbortSignal.timeout(ruta.startsWith('/v1/') ? 30000 : 12000)]),
    method: cuerpo === undefined ? 'GET' : 'POST',
    body: cuerpo === undefined ? undefined : JSON.stringify(ruta.startsWith('/v1/') ? cuerpo : externalizarSolicitud(cuerpo)),
    headers: { Accept: 'application/json', ...(cuerpo === undefined ? {} : { 'Content-Type': 'application/json' }) },
  })
  if (!respuesta.ok) {
    throw new ErrorApi(respuesta.status, respuesta.status === 404
      ? 'Esta oferta no está disponible.'
      : 'No pudimos consultar la información. Inténtalo nuevamente.')
  }
  const datos = await respuesta.json()
  return ruta.startsWith('/v1/') ? datos as T : internalizarRespuesta<T>(datos)
}
