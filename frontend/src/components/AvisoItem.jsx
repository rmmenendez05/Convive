import { useLang } from '../context/LangContext'

export default function AvisoItem({ aviso, puedeBorrar, onBorrar }) {
  const { idioma, t } = useLang()
  const fecha = new Intl.DateTimeFormat(idioma, { dateStyle: 'medium', timeStyle: 'short' }).format(
    new Date(aviso.creado_en),
  )
  return (
    <li className="aviso">
      <p className="aviso-texto">{aviso.texto}</p>
      <div className="aviso-meta">
        <span>
          {aviso.autor.nombre} · <time dateTime={aviso.creado_en}>{fecha}</time>
        </span>
        {puedeBorrar && (
          <button type="button" className="boton-enlace" onClick={() => onBorrar(aviso.id)}>
            {t('tablon.borrar')}
          </button>
        )}
      </div>
    </li>
  )
}
