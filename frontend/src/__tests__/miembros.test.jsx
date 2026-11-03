import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api/client'
import { ANA, LUIS, piso, renderApp, yo } from './utils'

vi.mock('../api/client', async (orig) => (await import('./mockApi')).mockApi(orig))

beforeEach(() => {
  vi.resetAllMocks()
  api.avisos.mockResolvedValue([])
})

describe('US5 · gestionar los miembros', () => {
  it('un miembro no ve expulsar ni regenerar', async () => {
    api.yo.mockResolvedValue(yo(LUIS, 10, 'miembro'))
    api.miPiso.mockResolvedValue(piso({ conCodigo: false }))
    renderApp('/piso', { token: 't' })
    await screen.findByRole('heading', { name: 'Calle Mayor 3' })
    expect(screen.queryByRole('button', { name: /Expulsar/ })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Regenerar código' })).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Abandonar el piso' })).toBeInTheDocument()
  })

  it('el admin expulsa tras confirmar, y puede cancelar', async () => {
    api.yo.mockResolvedValue(yo(ANA, 10, 'admin'))
    api.miPiso.mockResolvedValueOnce(piso()).mockResolvedValue(piso({ miembros: [] }))
    api.expulsar.mockResolvedValue(null)
    const usuario = userEvent.setup()
    renderApp('/piso', { token: 't' })

    // No hay botón de expulsarse a sí misma.
    expect(await screen.findByRole('button', { name: 'Expulsar Luis' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Expulsar Ana' })).not.toBeInTheDocument()

    await usuario.click(screen.getByRole('button', { name: 'Expulsar Luis' }))
    await usuario.click(screen.getByRole('button', { name: 'No' }))
    expect(api.expulsar).not.toHaveBeenCalled()

    await usuario.click(screen.getByRole('button', { name: 'Expulsar Luis' }))
    await usuario.click(screen.getByRole('button', { name: 'Sí' }))
    expect(api.expulsar).toHaveBeenCalledWith(LUIS.id)
    expect(await screen.findByRole('heading', { name: 'Calle Mayor 3' })).toBeInTheDocument()
    await vi.waitFor(() => expect(screen.queryByText(/Luis/)).not.toBeInTheDocument())
  })

  it('el admin regenera el código', async () => {
    api.yo.mockResolvedValue(yo(ANA, 10, 'admin'))
    api.miPiso.mockResolvedValue(piso())
    api.regenerarCodigo.mockResolvedValue({ codigo_invitacion: 'NUEVO123' })
    const usuario = userEvent.setup()
    renderApp('/piso', { token: 't' })

    await usuario.click(await screen.findByRole('button', { name: 'Regenerar código' }))
    await usuario.click(screen.getByRole('button', { name: 'Sí' }))
    expect(await screen.findByTestId('codigo-invitacion')).toHaveTextContent('NUEVO123')
  })

  it('abandonar tras confirmar lleva a /bienvenida', async () => {
    api.yo.mockResolvedValueOnce(yo(LUIS, 10, 'miembro')).mockResolvedValue(yo(LUIS))
    api.miPiso.mockResolvedValue(piso({ conCodigo: false }))
    api.abandonar.mockResolvedValue(null)
    const usuario = userEvent.setup()
    renderApp('/piso', { token: 't' })

    await usuario.click(await screen.findByRole('button', { name: 'Abandonar el piso' }))
    await usuario.click(screen.getByRole('button', { name: 'Sí' }))

    expect(await screen.findByRole('heading', { name: 'Hola, Luis' })).toBeInTheDocument()
    expect(api.abandonar).toHaveBeenCalledOnce()
  })

  it('el miembro que hereda el admin ve las opciones de admin', async () => {
    // yo() aún dice "miembro", pero el piso recién cargado le da el rol de admin.
    api.yo.mockResolvedValue(yo(LUIS, 10, 'miembro'))
    api.miPiso.mockResolvedValue({ ...piso({ admin: LUIS, miembros: [] }) })
    renderApp('/piso', { token: 't' })
    expect(await screen.findByRole('button', { name: 'Regenerar código' })).toBeInTheDocument()
  })
})
