import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router'
import { AppRoutes } from '../App'
import Layout from '../components/Layout'
import { AuthProvider } from '../context/AuthContext'
import { LangProvider } from '../context/LangContext'

export const ANA = { id: 1, email: 'ana@test.com', nombre: 'Ana' }
export const LUIS = { id: 2, email: 'luis@test.com', nombre: 'Luis' }

export function yo(usuario, pisoId = null, rol = null) {
  return { ...usuario, piso_id: pisoId, rol }
}

export function piso({ admin = ANA, miembros = [LUIS], conCodigo = true } = {}) {
  return {
    id: 10,
    nombre: 'Calle Mayor 3',
    direccion: null,
    ...(conCodigo ? { codigo_invitacion: 'K7Q2M9XA' } : {}),
    miembros: [
      { usuario_id: admin.id, nombre: admin.nombre, rol: 'admin', unido_en: '2026-11-01T10:00:00Z' },
      ...miembros.map((m, i) => ({
        usuario_id: m.id,
        nombre: m.nombre,
        rol: 'miembro',
        unido_en: `2026-11-0${i + 2}T10:00:00Z`,
      })),
    ],
  }
}

export function aviso(id, texto, autor, creado = '2026-11-03T10:00:00Z') {
  return { id, texto, autor: { id: autor.id, nombre: autor.nombre }, creado_en: creado }
}

/** Renderiza la app completa en `ruta`. Con `token`, simula una sesión guardada. */
export function renderApp(ruta, { token = null } = {}) {
  if (token) localStorage.setItem('convive.token', token)
  return render(
    <MemoryRouter initialEntries={[ruta]}>
      <LangProvider>
        <AuthProvider>
          <Layout>
            <AppRoutes />
          </Layout>
        </AuthProvider>
      </LangProvider>
    </MemoryRouter>,
  )
}
