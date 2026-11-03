import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api, ApiError, getToken, setAlPerderSesion, setIdioma, setToken } from '../api/client'

function respuesta(status, cuerpo) {
  return { status, ok: status >= 200 && status < 300, json: () => Promise.resolve(cuerpo) }
}

describe('cliente de la API', () => {
  let fetchMock

  beforeEach(() => {
    fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)
    setToken(null)
    setIdioma('es')
    setAlPerderSesion(null)
  })
  afterEach(() => vi.unstubAllGlobals())

  it('envía token, idioma y JSON a /api', async () => {
    fetchMock.mockResolvedValue(respuesta(201, { id: 1 }))
    setToken('abc')
    setIdioma('en')
    await expect(api.publicarAviso('hola')).resolves.toEqual({ id: 1 })
    const [url, opciones] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/avisos')
    expect(opciones.method).toBe('POST')
    expect(opciones.headers).toMatchObject({
      Authorization: 'Bearer abc',
      'Accept-Language': 'en',
      'Content-Type': 'application/json',
    })
    expect(JSON.parse(opciones.body)).toEqual({ texto: 'hola' })
  })

  it('no envía Authorization sin token', async () => {
    fetchMock.mockResolvedValue(respuesta(200, {}))
    await api.login('a@b.com', 'x')
    expect(fetchMock.mock.calls[0][1].headers.Authorization).toBeUndefined()
  })

  it('devuelve null en respuestas 204', async () => {
    fetchMock.mockResolvedValue({ status: 204, ok: true, json: () => Promise.reject(new Error('sin cuerpo')) })
    await expect(api.borrarAviso(3)).resolves.toBeNull()
    expect(fetchMock.mock.calls[0][0]).toBe('/api/avisos/3')
  })

  it('convierte el formato de error en ApiError', async () => {
    fetchMock.mockResolvedValue(respuesta(409, { error: { code: 'ya_tiene_piso', message: 'Ya perteneces a un piso' } }))
    const error = await api.crearPiso({ nombre: 'x' }).catch((e) => e)
    expect(error).toBeInstanceOf(ApiError)
    expect(error).toMatchObject({ status: 409, code: 'ya_tiene_piso', message: 'Ya perteneces a un piso' })
  })

  it('ante 401 no_autenticado borra el token y avisa', async () => {
    const perder = vi.fn()
    setAlPerderSesion(perder)
    setToken('caducado')
    fetchMock.mockResolvedValue(respuesta(401, { error: { code: 'no_autenticado', message: 'x' } }))
    await expect(api.yo()).rejects.toMatchObject({ code: 'no_autenticado' })
    expect(getToken()).toBeNull()
    expect(perder).toHaveBeenCalledOnce()
  })

  it('credenciales_invalidas no cierra la sesión', async () => {
    const perder = vi.fn()
    setAlPerderSesion(perder)
    fetchMock.mockResolvedValue(respuesta(401, { error: { code: 'credenciales_invalidas', message: 'x' } }))
    await expect(api.login('a@b.com', 'mal')).rejects.toMatchObject({ code: 'credenciales_invalidas' })
    expect(perder).not.toHaveBeenCalled()
  })

  it('un fallo de red da error_red', async () => {
    fetchMock.mockRejectedValue(new TypeError('Failed to fetch'))
    await expect(api.avisos()).rejects.toMatchObject({ status: 0, code: 'error_red' })
  })
})
