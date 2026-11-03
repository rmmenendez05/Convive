import { useT } from '../i18n/useT'
import BotonConfirmar from './BotonConfirmar'

export default function ListaMiembros({ miembros, usuarioId, soyAdmin, onExpulsar }) {
  const t = useT()
  return (
    <ul className="lista-miembros">
      {miembros.map((m) => (
        <li key={m.usuario_id}>
          <span className="miembro-nombre">
            {m.nombre} {m.usuario_id === usuarioId && <span className="tenue">{t('piso.tu')}</span>}
          </span>
          <span className={`etiqueta etiqueta-${m.rol}`}>{t(`piso.${m.rol}`)}</span>
          {soyAdmin && m.usuario_id !== usuarioId && (
            <BotonConfirmar
              className="boton-peligro boton-pequeno"
              ariaLabel={`${t('piso.expulsar')} ${m.nombre}`}
              onConfirmar={() => onExpulsar(m.usuario_id)}
            >
              {t('piso.expulsar')}
            </BotonConfirmar>
          )}
        </li>
      ))}
    </ul>
  )
}
