import { useActionState } from 'react'
import { Link, useNavigate } from 'react-router'
import FormError from '../components/FormError'
import { useAuth } from '../context/AuthContext'
import { useT } from '../i18n/useT'

export default function Login() {
  const { iniciarSesion } = useAuth()
  const navigate = useNavigate()
  const t = useT()

  const [estado, entrar, enviando] = useActionState(async (_previo, formData) => {
    const email = formData.get('email')
    try {
      const yo = await iniciarSesion(email, formData.get('password'))
      navigate(yo.piso_id ? '/piso' : '/bienvenida', { replace: true })
      return { email, error: null }
    } catch (error) {
      return { email, error }
    }
  }, { email: '', error: null })

  return (
    <section className="tarjeta tarjeta-acceso">
      <h1>{t('login.titulo')}</h1>
      <p className="tenue">{t('app.lema')}</p>
      <form action={entrar} className="formulario">
        <label>
          {t('login.email')}
          <input name="email" type="email" autoComplete="email" required defaultValue={estado.email} />
        </label>
        <label>
          {t('login.password')}
          <input name="password" type="password" autoComplete="current-password" required />
        </label>
        <FormError error={estado.error} />
        <button type="submit" disabled={enviando}>
          {enviando ? t('comun.enviando') : t('login.entrar')}
        </button>
      </form>
      <p>
        {t('login.sinCuenta')} <Link to="/registro">{t('login.irRegistro')}</Link>
      </p>
    </section>
  )
}
