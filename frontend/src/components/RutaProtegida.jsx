import { Navigate } from 'react-router'
import { useAuth } from '../context/AuthContext'
import { useT } from '../i18n/useT'

/**
 * Controla el acceso según la sesión y el piso:
 * - sin sesión → /login
 * - `conPiso` y sin piso → /bienvenida
 * - `sinPiso` y con piso → /piso
 */
export default function RutaProtegida({ conPiso = false, sinPiso = false, children }) {
  const { token, usuario, cargando } = useAuth()
  const t = useT()

  if (!token) return <Navigate to="/login" replace />
  if (cargando || !usuario) return <p className="cargando">{t('comun.cargando')}</p>
  if (conPiso && !usuario.piso_id) return <Navigate to="/bienvenida" replace />
  if (sinPiso && usuario.piso_id) return <Navigate to="/piso" replace />
  return children
}

/** Para /login y /registro: si ya hay sesión, se va al inicio. */
export function SoloVisitantes({ children }) {
  const { token } = useAuth()
  return token ? <Navigate to="/" replace /> : children
}
