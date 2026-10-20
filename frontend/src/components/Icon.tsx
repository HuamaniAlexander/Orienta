const paths = {
  sparkles: 'm12 2 2.5 7.5L22 12l-7.5 2.5L12 22l-2.5-7.5L2 12l7.5-2.5L12 2 M20 2v4 M18 4h4',
  compare: 'M4 4h6v16H4Z M14 4h6v16h-6Z M7 8v5 M17 8v8',
  compass: 'm12 2 3 7 7 3-7 3-3 7-3-7-7-3 7-3 3-7Z M9 15l6-6',
  search: 'M21 21l-5-5 M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0',
  arrow: 'M4 12h16 m-6-6 6 6-6 6',
  pin: 'M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0Z M15 10a3 3 0 1 1-6 0 3 3 0 0 1 6 0',
  screen: 'M3 3h18v14H3Z M8 21h8 M12 17v4',
  clock: 'M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0 M12 6v6l4 2',
  filter: 'M3 6h18 M3 12h18 M3 18h18 M7 3v6 M16 9v6 M9 15v6',
  info: 'M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0 M12 11v6 M12 7v1',
  book: 'M4 3h13l3 3v15H4Z M8 8h8 M8 12h8 M8 16h5',
  user: 'M20 21v-2a6 6 0 0 0-6-6h-4a6 6 0 0 0-6 6v2 M16 5a4 4 0 1 1-8 0 4 4 0 0 1 8 0',
  reset: 'M3 10a9 9 0 1 1 0 5 M3 3v7h7',
  external: 'M14 3h7v7 M21 3 10 14 M10 3H3v18h18v-7',
  check: 'm5 12 4 4L19 6',
  briefcase: 'M3 7h18v14H3Z M8 7V3h8v4 M3 12h18 M10 12v3h4v-3',
  coins: 'M20 5c0 2-16 2-16 0s16-2 16 0Z M4 5v14c0 3 16 3 16 0V5 M4 10c0 3 16 3 16 0 M4 15c0 3 16 3 16 0',
} as const

export type IconName = keyof typeof paths
export function Icon({ name, className = '' }: { name: IconName; className?: string }) {
  return <svg className={`icon ${className}`} viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"
    aria-hidden="true"><path d={paths[name]} /></svg>
}
