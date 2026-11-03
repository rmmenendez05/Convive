// Sustituye cada función de `api` por un vi.fn(); el resto del módulo es el real.
export async function mockApi(importOriginal) {
  const { vi } = await import('vitest')
  const real = await importOriginal()
  return { ...real, api: Object.fromEntries(Object.keys(real.api).map((k) => [k, vi.fn()])) }
}
