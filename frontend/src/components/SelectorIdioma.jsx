import { useLang } from '../context/LangContext'

export default function SelectorIdioma() {
  const { idioma, setIdioma, t } = useLang()
  return (
    <label className="selector-idioma">
      <span className="sr-only">{t('comun.idioma')}</span>
      <select aria-label={t('comun.idioma')} value={idioma} onChange={(e) => setIdioma(e.target.value)}>
        <option value="es">Español</option>
        <option value="en">English</option>
      </select>
    </label>
  )
}
