import { useActionState, useState } from 'react'
import { useT } from '../i18n/useT'
import AvisoItem from './AvisoItem'
import FormError from './FormError'

const MAX = 280

export default function Tablon({ avisos, usuarioId, soyAdmin, onPublicar, onBorrar }) {
  const t = useT()
  const [texto, setTexto] = useState('')
  const [error, publicar, enviando] = useActionState(async () => {
    try {
      await onPublicar(texto)
      setTexto('')
      return null
    } catch (e) {
      return e
    }
  }, null)

  return (
    <section className="tarjeta">
      <h2>{t('tablon.titulo')}</h2>
      <form action={publicar} className="form-aviso">
        <textarea
          name="texto"
          aria-label={t('tablon.placeholder')}
          placeholder={t('tablon.placeholder')}
          value={texto}
          maxLength={MAX}
          rows={3}
          onChange={(e) => setTexto(e.target.value)}
        />
        <div className="form-aviso-pie">
          <span className="tenue">{t('tablon.restantes', { n: MAX - texto.length })}</span>
          <button type="submit" disabled={enviando || !texto.trim()}>
            {enviando ? t('comun.enviando') : t('tablon.publicar')}
          </button>
        </div>
        <FormError error={error} />
      </form>
      {avisos.length === 0 ? (
        <p className="tenue">{t('tablon.vacio')}</p>
      ) : (
        <ul className="lista-avisos">
          {avisos.map((a) => (
            <AvisoItem key={a.id} aviso={a} puedeBorrar={soyAdmin || a.autor.id === usuarioId} onBorrar={onBorrar} />
          ))}
        </ul>
      )}
    </section>
  )
}
