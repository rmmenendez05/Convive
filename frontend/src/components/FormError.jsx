import { useMensajeError } from '../i18n/useT'

export default function FormError({ error }) {
  const mensajeDe = useMensajeError()
  if (!error) return null
  return (
    <p className="form-error" role="alert">
      {mensajeDe(error)}
    </p>
  )
}
