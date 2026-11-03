import { useAuth } from '../context/AuthContext'
import { useT } from '../i18n/useT'
import SelectorIdioma from './SelectorIdioma'

export default function Layout({ children }) {
  const { token, usuario, cerrarSesion } = useAuth()
  const t = useT()
  return (
    <div className="app">
      <header className="cabecera">
        <div className="marca">
          <span className="logo" aria-hidden="true">⌂</span>
          <span>{t('app.nombre')}</span>
        </div>
        <div className="cabecera-acciones">
          <SelectorIdioma />
          {token && (
            <>
              {usuario && <span className="usuario-actual">{usuario.nombre}</span>}
              <button type="button" className="boton-secundario" onClick={cerrarSesion}>
                {t('comun.salir')}
              </button>
            </>
          )}
        </div>
      </header>
      <main className="contenido">{children}</main>
    </div>
  )
}
