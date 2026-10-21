export function urlFuenteSegura(referencia: string | null): string | null {
  if (!referencia) return null
  try {
    const direccion = new URL(referencia)
    return ['https:', 'http:'].includes(direccion.protocol) && !direccion.username && !direccion.password ? direccion.href : null
  } catch { return null }
}

export function etiquetaCosto(valor: string | null): string {
  if (valor === null) return 'Dato no disponible'
  const importe = Number(valor)
  return Number.isFinite(importe)
    ? `${new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN', maximumFractionDigits: 2 }).format(importe)} / mes`
    : 'Dato no disponible'
}

export function etiquetaRevision(valor: string | null): string {
  if (!valor) return 'Sin fecha registrada'
  return new Intl.DateTimeFormat('es-PE', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' })
    .format(new Date(`${valor}T00:00:00Z`))
}
