import type { Carrera } from '../domain/carrera'
import { portadaCarrera } from '../domain/portadas'

export function ImagenCarrera({ carrera }: { carrera: Carrera }) {
  return <img className="imagen-profesion" src={`/imagenes/${portadaCarrera(carrera)}.webp`}
    alt={`Actividad formativa relacionada con ${carrera.nombre}`} width="1536" height="1024"
    loading="lazy" decoding="async" onError={evento => {
      if (!evento.currentTarget.src.endsWith('/imagenes/negocios.webp')) evento.currentTarget.src = '/imagenes/negocios.webp'
    }} />
}
