import { institutionLogo, institutionName } from '../domain/institutions'

export function InstitutionLogo({ code }: { code: string }) {
  const src = institutionLogo(code)
  return src ? <img className={`university-logo university-${code.toLowerCase()}`} src={src}
    alt={institutionName(code)} width="128" height="54" loading="lazy" /> : null
}
