import { createContext, useContext } from 'react'
export interface Selection {
  ids: string[]
  toggle: (id: string, replaceAt?: number) => void
  clear: () => void
  message: string
}
export const ComparisonContext = createContext<Selection>({ ids: [], toggle: () => {}, clear: () => {}, message: '' })
export function useComparison() { return useContext(ComparisonContext) }
