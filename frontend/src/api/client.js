// Único módulo que habla con la API. El resto de la app usa `api.*`.

const BASE = '/api'

let token = null
let idioma = 'es'
let alPerderSesion = null

export class ApiError extends Error {
  constructor(status, code, message, details) {
    super(message || code)
    this.status = status
    this.code = code
    this.details = details
  }
}

export function setToken(nuevo) {
  token = nuevo
}

export function getToken() {
  return token
}

export function setIdioma(nuevo) {
  idioma = nuevo
}

/** Se llama cuando la API responde 401 `no_autenticado` (token caducado o inválido). */
export function setAlPerderSesion(callback) {
  alPerderSesion = callback
}

async function request(method, path, body) {
  const headers = { 'Accept-Language': idioma }
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (token) headers.Authorization = `Bearer ${token}`

  let respuesta
  try {
    respuesta = await fetch(`${BASE}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch {
    throw new ApiError(0, 'error_red')
  }

  if (respuesta.status === 204) return null
  const datos = await respuesta.json().catch(() => null)

  if (!respuesta.ok) {
    const error = datos?.error ?? {}
    const apiError = new ApiError(respuesta.status, error.code ?? 'error_interno', error.message, error.details)
    if (apiError.code === 'no_autenticado') {
      token = null
      alPerderSesion?.()
    }
    throw apiError
  }
  return datos
}

export const api = {
  registro: (datos) => request('POST', '/auth/registro', datos),
  login: (email, password) => request('POST', '/auth/login', { email, password }),
  yo: () => request('GET', '/auth/yo'),

  crearPiso: (datos) => request('POST', '/pisos', datos),
  unirse: (codigo) => request('POST', '/pisos/unirse', { codigo }),
  miPiso: () => request('GET', '/pisos/mio'),
  expulsar: (usuarioId) => request('DELETE', `/pisos/mio/miembros/${usuarioId}`),
  abandonar: () => request('POST', '/pisos/mio/abandonar'),
  regenerarCodigo: () => request('POST', '/pisos/mio/codigo'),

  avisos: () => request('GET', '/avisos'),
  publicarAviso: (texto) => request('POST', '/avisos', { texto }),
  borrarAviso: (id) => request('DELETE', `/avisos/${id}`),
}
