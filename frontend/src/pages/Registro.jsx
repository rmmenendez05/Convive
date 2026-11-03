import { useActionState } from 'react'
import { Link, useNavigate } from 'react-router'
import { api } from '../api/client'
import FormError from '../components/FormError'
import { useAuth } from '../context/AuthContext'
import { useT } from '../i18n/useT'

const VACIO = { nombre: '', email: '', error: null }

export default function Registro() {
  const { iniciarSesion } = useAuth()
  const navigate = useNavigate()
  const t = useT()

  const [estado, registrar, enviando] = useActionState(async (_previo, formData) => {
    const datos = {
      nombre: formData.get('nombre'),
      email: formData.get('email'),
      password: formData.get('password'),
    }
    try {
      await api.registro(datos)
      await iniciarSesion(datos.email, datos.password)
      navigate('/bienvenida', { replace: true })
      return VACIO
    } catch (error) {
      return { nombre: datos.nombre, email: datos.email, error }
    }
  }, VACIO)

  return (
    <section className="tarjeta tarjeta-acceso">
      <h1>{t('registro.titulo')}</h1>
      <form action={registrar} className="formulario">
        <label>
          {t('registro.nombre')}
          <input name="nombre" required maxLength={40} autoComplete="given-name" defaultValue={estado.nombre} />
        </label>
        <label>
          {t('registro.email')}
          <input name="email" type="email" required autoComplete="email" defaultValue={estado.email} />
        </label>
        <label>
          {t('registro.password')}
          <input name="password" type="password" required minLength={8} autoComplete="new-password" />
          <small className="tenue">{t('registro.ayudaPassword')}</small>
        </label>
        <FormError error={estado.error} />
        <button type="submit" disabled={enviando}>
          {enviando ? t('comun.enviando') : t('registro.crear')}
        </button>
      </form>
      <p>
        {t('registro.yaTengo')} <Link to="/login">{t('registro.irLogin')}</Link>
      </p>
    </section>
  )
}
