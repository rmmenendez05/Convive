import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { api, ApiError } from '../api/client'
import { ANA, LUIS, piso, renderApp, yo } from './utils'

vi.mock('../api/client', async (orig) => (await import('./mockApi')).mockApi(orig))

beforeEach(() => {
  vi.resetAllMocks()
  api.avisos.mockResolvedValue([])
})

describe('US2 · crear un piso o unirse', () => {
  it('crear piso lleva a /piso', async () => {
    api.yo.mockResolvedValueOnce(yo(ANA)).mockResolvedValue(yo(ANA, 10, 'admin'))
    api.crearPiso.mockResolvedValue(piso({ miembros: [] }))
    api.miPiso.mockResolvedValue(piso({ miembros: [] }))
    const usuario = userEvent.setup()
    renderApp('/bienvenida', { token: 't' })

    await usuario.type(await screen.findByLabelText('Nombre del piso'), 'Calle Mayor 3')
    await usuario.click(screen.getByRole('button', { name: 'Crear piso' }))

    expect(await screen.findByRole('heading', { name: 'Calle Mayor 3' })).toBeInTheDocument()
    expect(api.crearPiso).toHaveBeenCalledWith({ nombre: 'Calle Mayor 3', direccion: null })
  })

  it('unirse con código lleva a /piso', async () => {
    api.yo.mockResolvedValueOnce(yo(LUIS)).mockResolvedValue(yo(LUIS, 10, 'miembro'))
    api.unirse.mockResolvedValue(piso({ conCodigo: false }))
    api.miPiso.mockResolvedValue(piso({ conCodigo: false }))
    const usuario = userEvent.setup()
    renderApp('/bienvenida', { token: 't' })

    await usuario.type(await screen.findByLabelText('Código de invitación'), 'k7q2m9xa')
    await usuario.click(screen.getByRole('button', { name: 'Unirme' }))

    expect(await screen.findByRole('heading', { name: 'Calle Mayor 3' })).toBeInTheDocument()
    expect(api.unirse).toHaveBeenCalledWith('k7q2m9xa')
  })

  it('muestra codigo_invalido', async () => {
    api.yo.mockResolvedValue(yo(LUIS))
    api.unirse.mockRejectedValue(new ApiError(404, 'codigo_invalido', 'No hay ningún piso con ese código'))
    const usuario = userEvent.setup()
    renderApp('/bienvenida', { token: 't' })

    await usuario.type(await screen.findByLabelText('Código de invitación'), 'ZZZZZZZZ')
    await usuario.click(screen.getByRole('button', { name: 'Unirme' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('No hay ningún piso con ese código')
  })

  it('con piso, /bienvenida redirige a /piso', async () => {
    api.yo.mockResolvedValue(yo(ANA, 10, 'admin'))
    api.miPiso.mockResolvedValue(piso())
    renderApp('/bienvenida', { token: 't' })
    expect(await screen.findByRole('heading', { name: 'Calle Mayor 3' })).toBeInTheDocument()
  })

  it('sin piso, /piso redirige a /bienvenida', async () => {
    api.yo.mockResolvedValue(yo(ANA))
    renderApp('/piso', { token: 't' })
    expect(await screen.findByRole('heading', { name: 'Hola, Ana' })).toBeInTheDocument()
  })
})
