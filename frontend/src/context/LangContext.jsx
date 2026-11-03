import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { setIdioma as setIdiomaApi } from '../api/client'
import es from '../i18n/es'
import en from '../i18n/en'

export const IDIOMAS = { es, en }
export const IDIOMA_POR_DEFECTO = 'es'
const CLAVE = 'convive.lang'

function idiomaGuardado() {
  try {
    const guardado = localStorage.getItem(CLAVE)
    return guardado in IDIOMAS ? guardado : IDIOMA_POR_DEFECTO
  } catch {
    return IDIOMA_POR_DEFECTO
  }
}

function buscar(diccionario, clave) {
  return clave.split('.').reduce((nodo, parte) => nodo?.[parte], diccionario)
}

export function traducir(idioma, clave, vars = {}) {
  const texto = buscar(IDIOMAS[idioma], clave) ?? buscar(IDIOMAS[IDIOMA_POR_DEFECTO], clave) ?? clave
  return texto.replace(/\{(\w+)\}/g, (_, nombre) => vars[nombre] ?? `{${nombre}}`)
}

const LangContext = createContext(null)

export function LangProvider({ children }) {
  const [idioma, setIdiomaEstado] = useState(idiomaGuardado)
  setIdiomaApi(idioma)

  useEffect(() => {
    document.documentElement.lang = idioma
  }, [idioma])

  const setIdioma = useCallback((nuevo) => {
    if (!(nuevo in IDIOMAS)) return
    try {
      localStorage.setItem(CLAVE, nuevo)
    } catch {
      // Sin almacenamiento disponible: el idioma solo dura esta sesión.
    }
    setIdiomaApi(nuevo)
    setIdiomaEstado(nuevo)
  }, [])

  const valor = useMemo(
    () => ({ idioma, setIdioma, t: (clave, vars) => traducir(idioma, clave, vars) }),
    [idioma, setIdioma],
  )
  return <LangContext.Provider value={valor}>{children}</LangContext.Provider>
}

export function useLang() {
  const ctx = useContext(LangContext)
  if (!ctx) throw new Error('useLang debe usarse dentro de <LangProvider>')
  return ctx
}
