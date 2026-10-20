export function safeSourceUrl(reference: string | null): string | null {
  if (!reference) return null
  try {
    const url = new URL(reference)
    return ['https:', 'http:'].includes(url.protocol) && !url.username && !url.password ? url.href : null
  } catch { return null }
}

export function costLabel(value: string | null): string {
  if (value === null) return 'Dato no disponible'
  const amount = Number(value)
  return Number.isFinite(amount)
    ? `${new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN', maximumFractionDigits: 2 }).format(amount)} / mes`
    : 'Dato no disponible'
}

export function reviewLabel(value: string | null): string {
  if (!value) return 'Sin fecha registrada'
  return new Intl.DateTimeFormat('es-PE', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' })
    .format(new Date(`${value}T00:00:00Z`))
}
