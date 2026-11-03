import { useActionState } from 'react'
import { useNavigate } from 'react-router'
import { api } from '../api/client'
import FormError from '../components/FormError'
import { useAuth } from '../context/AuthContext'
import { useT } from '../i18n/useT'

export default function Bienvenida() {
  const { usuario, refrescar } = useAuth()
  const navigate = useNavigate()
  const t = useT()

  async function entrarAlPiso(peticion) {
    try {
      await peticion()
      await refrescar()
      navigate('/piso', { replace: true })
      return null
    } catch (error) {
      return error
    }
  }

  const [errorCrear, crear, creando] = useActionState(
    (_previo, formData) =>
      entrarAlPiso(() =>
        api.crearPiso({ nombre: formData.get('nombre'), direccion: formData.get('direccion') || null }),
      ),
    null,
  )
  const [errorUnirse, unirse, uniendo] = useActionState(
    (_previo, formData) => entrarAlPiso(() => api.unirse(formData.get('codigo'))),
    null,
  )

  return (
    <div className="bienvenida">
      <section className="intro">
        <h1>{t('bienvenida.titulo', { nombre: usuario.nombre })}</h1>
        <p>{t('bienvenida.texto')}</p>
      </section>
      <div className="rejilla-2">
        <section className="tarjeta">
          <h2>{t('bienvenida.crearTitulo')}</h2>
          <form action={crear} className="formulario">
            <label>
              {t('bienvenida.nombrePiso')}
              <input name="nombre" required maxLength={60} />
            </label>
            <label>
              {t('bienvenida.direccion')}
              <input name="direccion" maxLength={200} />
            </label>
            <FormError error={errorCrear} />
            <button type="submit" disabled={creando}>
              {creando ? t('comun.enviando') : t('bienvenida.crear')}
            </button>
          </form>
        </section>
        <section className="tarjeta">
          <h2>{t('bienvenida.unirseTitulo')}</h2>
          <form action={unirse} className="formulario">
            <label>
              {t('bienvenida.codigo')}
              <input name="codigo" required maxLength={8} className="input-codigo" autoComplete="off" />
            </label>
            <FormError error={errorUnirse} />
            <button type="submit" disabled={uniendo}>
              {uniendo ? t('comun.enviando') : t('bienvenida.unirse')}
            </button>
          </form>
        </section>
      </div>
    </div>
  )
}
