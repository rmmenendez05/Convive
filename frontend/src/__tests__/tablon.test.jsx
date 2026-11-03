import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { api, ApiError } from '../api/client'
import { ANA, LUIS, aviso, piso, renderApp, yo } from './utils'

vi.mock('../api/client', async (orig) => (await import('./mockApi')).mockApi(orig))

const MARTA = { id: 3, email: 'marta@test.com', nombre: 'Marta' }

beforeEach(() => vi.resetAllMocks())

function sesionDe(usuario, rol) {
  api.yo.mockResolvedValue(yo(usuario, 10, rol))
  api.miPiso.mockResolvedValue(piso({ miembros: [LUIS, MARTA], conCodigo: rol === 'admin' }))
}

function avisoConTexto(texto) {
  return screen.getByText(texto).closest('li')
}

describe('US4 · tablón de avisos', () => {
  it('muestra los avisos y el vacío', async () => {
    sesionDe(LUIS, 'miembro')
    api.avisos.mockResolvedValue([])
    renderApp('/piso', { token: 't' })
    expect(await screen.findByText('Todavía no hay avisos.')).toBeInTheDocument()
  })

  it('publicar añade el aviso arriba y limpia el campo', async () => {
    sesionDe(LUIS, 'miembro')
    api.avisos.mockResolvedValue([aviso(1, 'viejo', ANA)])
    api.publicarAviso.mockResolvedValue(aviso(2, 'Mañana viene el fontanero', LUIS, '2026-11-03T12:00:00Z'))
    const usuario = userEvent.setup()
    renderApp('/piso', { token: 't' })

    const campo = await screen.findByLabelText('Escribe un aviso para el piso…')
    await usuario.type(campo, 'Mañana viene el fontanero')
    await usuario.click(screen.getByRole('button', { name: 'Publicar' }))

    await screen.findByText('Mañana viene el fontanero')
    const textos = screen.getAllByRole('listitem').map((li) => li.querySelector('.aviso-texto')?.textContent).filter(Boolean)
    expect(textos).toEqual(['Mañana viene el fontanero', 'viejo'])
    expect(campo).toHaveValue('')
    expect(api.publicarAviso).toHaveBeenCalledWith('Mañana viene el fontanero')
  })

  it('cuenta los caracteres restantes sobre 280', async () => {
    sesionDe(LUIS, 'miembro')
    api.avisos.mockResolvedValue([])
    const usuario = userEvent.setup()
    renderApp('/piso', { token: 't' })
    expect(await screen.findByText('280 caracteres restantes')).toBeInTheDocument()
    await usuario.type(screen.getByLabelText('Escribe un aviso para el piso…'), 'hola')
    expect(screen.getByText('276 caracteres restantes')).toBeInTheDocument()
    expect(screen.getByLabelText('Escribe un aviso para el piso…')).toHaveAttribute('maxLength', '280')
  })

  it('muestra el error al publicar', async () => {
    sesionDe(LUIS, 'miembro')
    api.avisos.mockResolvedValue([])
    api.publicarAviso.mockRejectedValue(new ApiError(400, 'datos_invalidos', 'Los datos enviados no son válidos'))
    const usuario = userEvent.setup()
    renderApp('/piso', { token: 't' })
    await usuario.type(await screen.findByLabelText('Escribe un aviso para el piso…'), 'x')
    await usuario.click(screen.getByRole('button', { name: 'Publicar' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Los datos enviados no son válidos')
  })

  it('un miembro solo puede borrar sus propios avisos', async () => {
    sesionDe(LUIS, 'miembro')
    api.avisos.mockResolvedValue([aviso(1, 'de Luis', LUIS), aviso(2, 'de Marta', MARTA)])
    api.borrarAviso.mockResolvedValue(null)
    const usuario = userEvent.setup()
    renderApp('/piso', { token: 't' })

    await screen.findByText('de Luis')
    expect(within(avisoConTexto('de Marta')).queryByRole('button', { name: 'Borrar' })).not.toBeInTheDocument()
    await usuario.click(within(avisoConTexto('de Luis')).getByRole('button', { name: 'Borrar' }))

    expect(api.borrarAviso).toHaveBeenCalledWith(1)
    expect(screen.queryByText('de Luis')).not.toBeInTheDocument()
  })

  it('el admin puede borrar cualquier aviso', async () => {
    sesionDe(ANA, 'admin')
    api.avisos.mockResolvedValue([aviso(1, 'de Luis', LUIS), aviso(2, 'de Marta', MARTA)])
    renderApp('/piso', { token: 't' })
    await screen.findByText('de Luis')
    expect(screen.getAllByRole('button', { name: 'Borrar' })).toHaveLength(2)
  })
})
