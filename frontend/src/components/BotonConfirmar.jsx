import { useState } from 'react'
import { useT } from '../i18n/useT'

/** Botón que pide confirmación en la propia página antes de ejecutar `onConfirmar`. */
export default function BotonConfirmar({ children, onConfirmar, className = 'boton-peligro', disabled, ariaLabel }) {
  const [preguntando, setPreguntando] = useState(false)
  const t = useT()

  if (!preguntando) {
    return (
      <button
        type="button"
        className={className}
        disabled={disabled}
        aria-label={ariaLabel}
        onClick={() => setPreguntando(true)}
      >
        {children}
      </button>
    )
  }
  return (
    <span className="confirmar" role="group" aria-label={t('confirmar.seguro')}>
      <span>{t('confirmar.seguro')}</span>
      <button
        type="button"
        className="boton-peligro"
        onClick={() => {
          setPreguntando(false)
          onConfirmar()
        }}
      >
        {t('confirmar.si')}
      </button>
      <button type="button" className="boton-secundario" onClick={() => setPreguntando(false)}>
        {t('confirmar.no')}
      </button>
    </span>
  )
}
