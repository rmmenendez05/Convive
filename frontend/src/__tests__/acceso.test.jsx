import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { api, ApiError } from '../api/client'
import { ANA, renderApp, yo } from './utils'

vi.mock('../api/client', async (orig) => (await import('./mockApi')).mockApi(orig))

beforeEach(() => vi.resetAllMocks())

async function rellenarRegistro(usuario) {
  await usuario.type(screen.getByLabelText('Nombre'), 'Ana')
  await usuario.type(screen.getByLabelText('Email'), 'ana@test.com')
  await usuario.type(screen.getByLabelText(/^Contraseña/), 'secreto123')
  await usuario.click(screen.getByRole('button', { name: 'Crear cuenta' }))
}

describe('US1 · registro e inicio de sesión', () => {
  it('registro correcto inicia sesión y lleva a bienvenida', async () => {
    api.registro.mockResolvedValue(ANA)
    api.login.mockResolvedValue({ token: 't1', usuario: ANA })
    api.yo.mockResolvedValue(yo(ANA))
    const usuario = userEvent.setup()
    renderApp('/registro')

    await rellenarRegistro(usuario)

    expect(await screen.findByRole('heading', { name: 'Hola, Ana' })).toBeInTheDocument()
    expect(api.registro).toHaveBeenCalledWith({ nombre: 'Ana', email: 'ana@test.com', password: 'secreto123' })
    expect(localStorage.getItem('convive.token')).toBe('t1')
  })

  it('muestra email_ya_registrado y conserva lo escrito', async () => {
    api.registro.mockRejectedValue(new ApiError(409, 'email_ya_registrado', 'Ya existe una cuenta con ese email'))
    const usuario = userEvent.setup()
    renderApp('/registro')

    await rellenarRegistro(usuario)

    expect(await screen.findByRole('alert')).toHaveTextContent('Ya existe una cuenta con ese email')
    expect(screen.getByLabelText('Email')).toHaveValue('ana@test.com')
    expect(api.login).not.toHaveBeenCalled()
  })

  it('login fallido muestra el mensaje genérico', async () => {
    api.login.mockRejectedValue(new ApiError(401, 'credenciales_invalidas', 'Email o contraseña incorrectos'))
    const usuario = userEvent.setup()
    renderApp('/login')

    await usuario.type(screen.getByLabelText('Email'), 'ana@test.com')
    await usuario.type(screen.getByLabelText('Contraseña'), 'malamala')
    await usuario.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Email o contraseña incorrectos')
    expect(localStorage.getItem('convive.token')).toBeNull()
  })

  it('login correcto con piso lleva a /piso', async () => {
    api.login.mockResolvedValue({ token: 't1', usuario: ANA })
    api.yo.mockResolvedValue(yo(ANA, 10, 'admin'))
    api.miPiso.mockResolvedValue({ id: 10, nombre: 'Calle Mayor 3', direccion: null, codigo_invitacion: 'K7Q2M9XA', miembros: [] })
    api.avisos.mockResolvedValue([])
    const usuario = userEvent.setup()
    renderApp('/login')

    await usuario.type(screen.getByLabelText('Email'), 'ana@test.com')
    await usuario.type(screen.getByLabelText('Contraseña'), 'secreto123')
    await usuario.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(await screen.findByRole('heading', { name: 'Calle Mayor 3' })).toBeInTheDocument()
  })

  it('sin sesión, una ruta protegida redirige a /login', () => {
    renderApp('/piso')
    expect(screen.getByRole('heading', { name: 'Inicia sesión' })).toBeInTheDocument()
  })

  it('con un token caducado vuelve a /login', async () => {
    api.yo.mockRejectedValue(new ApiError(401, 'no_autenticado'))
    renderApp('/piso', { token: 'caducado' })
    expect(await screen.findByRole('heading', { name: 'Inicia sesión' })).toBeInTheDocument()
    expect(localStorage.getItem('convive.token')).toBeNull()
  })

  it('cerrar sesión borra el token y vuelve a /login', async () => {
    api.yo.mockResolvedValue(yo(ANA))
    const usuario = userEvent.setup()
    renderApp('/bienvenida', { token: 't1' })
    await usuario.click(await screen.findByRole('button', { name: 'Cerrar sesión' }))
    expect(screen.getByRole('heading', { name: 'Inicia sesión' })).toBeInTheDocument()
    expect(localStorage.getItem('convive.token')).toBeNull()
  })
})
