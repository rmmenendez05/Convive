import { useLang } from '../context/LangContext'

/** Devuelve la función de traducción `t(clave, vars)` del idioma activo. */
export function useT() {
  return useLang().t
}

/** Mensaje para un error de la API: el del servidor (ya en el idioma pedido) o el traducido del código. */
export function useMensajeError() {
  const t = useT()
  return (error) => {
    if (!error) return null
    if (error.code && error.code !== 'error_red' && error.message && error.message !== error.code) {
      return error.message
    }
    return t(`errores.${error.code ?? 'error_interno'}`)
  }
}
