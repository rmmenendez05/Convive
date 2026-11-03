import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { api, setAlPerderSesion, setToken as setTokenApi } from '../api/client'

const CLAVE = 'convive.token'
const AuthContext = createContext(null)

function tokenGuardado() {
  try {
    return localStorage.getItem(CLAVE)
  } catch {
    return null
  }
}

function guardarToken(token) {
  try {
    if (token) localStorage.setItem(CLAVE, token)
    else localStorage.removeItem(CLAVE)
  } catch {
    // Sin almacenamiento: el token solo vive en memoria.
  }
  setTokenApi(token)
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => {
    const inicial = tokenGuardado()
    setTokenApi(inicial)
    return inicial
  })
  const [usuario, setUsuario] = useState(null)
  const [cargando, setCargando] = useState(Boolean(token))

  const cerrarSesion = useCallback(() => {
    guardarToken(null)
    setToken(null)
    setUsuario(null)
    setCargando(false)
  }, [])

  const refrescar = useCallback(async () => {
    const yo = await api.yo()
    setUsuario(yo)
    return yo
  }, [])

  useEffect(() => {
    setAlPerderSesion(cerrarSesion)
    return () => setAlPerderSesion(null)
  }, [cerrarSesion])

  useEffect(() => {
    if (!token || usuario) return
    let cancelado = false
    api
      .yo()
      .then((yo) => !cancelado && setUsuario(yo))
      .catch(() => !cancelado && cerrarSesion())
      .finally(() => !cancelado && setCargando(false))
    return () => {
      cancelado = true
    }
  }, [token, usuario, cerrarSesion])

  const iniciarSesion = useCallback(async (email, password) => {
    const { token: nuevo } = await api.login(email, password)
    guardarToken(nuevo)
    const yo = await api.yo()
    setToken(nuevo)
    setUsuario(yo)
    setCargando(false)
    return yo
  }, [])

  const valor = useMemo(
    () => ({ token, usuario, cargando, iniciarSesion, cerrarSesion, refrescar }),
    [token, usuario, cargando, iniciarSesion, cerrarSesion, refrescar],
  )
  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth debe usarse dentro de <AuthProvider>')
  return ctx
}
