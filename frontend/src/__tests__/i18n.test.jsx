import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { traducir } from '../context/LangContext'
import { renderApp } from './utils'

vi.mock('../api/client', async (orig) => (await import('./mockApi')).mockApi(orig))

describe('idioma', () => {
  it('es español por defecto', () => {
    renderApp('/login')
    expect(screen.getByRole('heading', { name: 'Inicia sesión' })).toBeInTheDocument()
    expect(document.documentElement.lang).toBe('es')
  })

  it('cambia a inglés y lo recuerda', async () => {
    const usuario = userEvent.setup()
    const { unmount } = renderApp('/login')
    await usuario.selectOptions(screen.getByLabelText('Idioma'), 'en')
    expect(screen.getByRole('heading', { name: 'Sign in' })).toBeInTheDocument()
    expect(localStorage.getItem('convive.lang')).toBe('en')
    unmount()

    renderApp('/login')
    expect(screen.getByRole('heading', { name: 'Sign in' })).toBeInTheDocument()
  })

  it('interpola variables y cae al español si falta una clave', () => {
    expect(traducir('en', 'tablon.restantes', { n: 3 })).toBe('3 characters left')
    expect(traducir('en', 'no.existe')).toBe('no.existe')
  })
})
