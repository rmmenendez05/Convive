import { screen, within } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api/client'
import { ANA, LUIS, piso, renderApp, yo } from './utils'

vi.mock('../api/client', async (orig) => (await import('./mockApi')).mockApi(orig))

beforeEach(() => {
  vi.resetAllMocks()
  api.avisos.mockResolvedValue([])
})

describe('US3 · ver mi piso', () => {
  it('lista los miembros con su rol', async () => {
    api.yo.mockResolvedValue(yo(LUIS, 10, 'miembro'))
    api.miPiso.mockResolvedValue(piso({ conCodigo: false }))
    renderApp('/piso', { token: 't' })

    const seccion = (await screen.findByRole('heading', { name: 'Miembros' })).closest('section')
    const lista = within(seccion)
    expect(lista.getByText('Ana')).toBeInTheDocument()
    expect(lista.getByText('Administrador')).toBeInTheDocument()
    expect(lista.getByText(/Luis/)).toBeInTheDocument()
    expect(lista.getByText('Miembro')).toBeInTheDocument()
    expect(lista.getByText('(tú)')).toBeInTheDocument()
  })

  it('el admin ve el código de invitación', async () => {
    api.yo.mockResolvedValue(yo(ANA, 10, 'admin'))
    api.miPiso.mockResolvedValue(piso())
    renderApp('/piso', { token: 't' })
    expect(await screen.findByTestId('codigo-invitacion')).toHaveTextContent('K7Q2M9XA')
  })

  it('un miembro no ve el código', async () => {
    api.yo.mockResolvedValue(yo(LUIS, 10, 'miembro'))
    api.miPiso.mockResolvedValue(piso({ conCodigo: false }))
    renderApp('/piso', { token: 't' })
    await screen.findByRole('heading', { name: 'Calle Mayor 3' })
    expect(screen.queryByTestId('codigo-invitacion')).not.toBeInTheDocument()
    expect(screen.queryByText('Código de invitación')).not.toBeInTheDocument()
  })
})
