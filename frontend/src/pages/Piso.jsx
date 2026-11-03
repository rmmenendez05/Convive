import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router'
import { api } from '../api/client'
import BotonConfirmar from '../components/BotonConfirmar'
import FormError from '../components/FormError'
import ListaMiembros from '../components/ListaMiembros'
import Tablon from '../components/Tablon'
import { useAuth } from '../context/AuthContext'
import { useT } from '../i18n/useT'

export default function Piso() {
  const { usuario, refrescar } = useAuth()
  const navigate = useNavigate()
  const t = useT()
  const [piso, setPiso] = useState(null)
  const [avisos, setAvisos] = useState([])
  const [error, setError] = useState(null)

  const cargar = useCallback(async () => {
    const [datosPiso, datosAvisos] = await Promise.all([api.miPiso(), api.avisos()])
    setPiso(datosPiso)
    setAvisos(datosAvisos)
  }, [])

  // Ejecuta una acción y muestra su error; si el usuario ya no tiene piso, vuelve a bienvenida.
  const ejecutar = useCallback(
    async (accion) => {
      setError(null)
      try {
        await accion()
      } catch (e) {
        if (e.code === 'sin_piso') {
          await refrescar()
          navigate('/bienvenida', { replace: true })
          return
        }
        setError(e)
      }
    },
    [navigate, refrescar],
  )

  useEffect(() => {
    ejecutar(cargar)
  }, [ejecutar, cargar])

  if (!piso) {
    return error ? <FormError error={error} /> : <p className="cargando">{t('comun.cargando')}</p>
  }

  // El rol sale del piso recién cargado (puede haber cambiado por un traspaso).
  const soyAdmin = piso.miembros.some((m) => m.usuario_id === usuario.id && m.rol === 'admin')

  const expulsar = (id) => ejecutar(async () => {
    await api.expulsar(id)
    await cargar()
  })
  const regenerar = () => ejecutar(async () => {
    const { codigo_invitacion } = await api.regenerarCodigo()
    setPiso((p) => ({ ...p, codigo_invitacion }))
  })
  const abandonar = () => ejecutar(async () => {
    await api.abandonar()
    await refrescar()
    navigate('/bienvenida', { replace: true })
  })
  const publicar = async (texto) => {
    const aviso = await api.publicarAviso(texto)
    setAvisos((lista) => [aviso, ...lista])
  }
  const borrarAviso = (id) => ejecutar(async () => {
    await api.borrarAviso(id)
    setAvisos((lista) => lista.filter((a) => a.id !== id))
  })

  return (
    <div className="piso">
      <section className="intro">
        <h1>{piso.nombre}</h1>
        {piso.direccion && <p className="tenue">{piso.direccion}</p>}
      </section>
      <FormError error={error} />
      <div className="rejilla-piso">
        <Tablon
          avisos={avisos}
          usuarioId={usuario.id}
          soyAdmin={soyAdmin}
          onPublicar={publicar}
          onBorrar={borrarAviso}
        />
        <aside className="columna-lateral">
          <section className="tarjeta">
            <h2>{t('piso.miembros')}</h2>
            <ListaMiembros
              miembros={piso.miembros}
              usuarioId={usuario.id}
              soyAdmin={soyAdmin}
              onExpulsar={expulsar}
            />
          </section>
          {soyAdmin && (
            <section className="tarjeta">
              <h2>{t('piso.codigo')}</h2>
              <p className="codigo" data-testid="codigo-invitacion">{piso.codigo_invitacion}</p>
              <p className="tenue">{t('piso.codigoAyuda')}</p>
              <BotonConfirmar className="boton-secundario" onConfirmar={regenerar}>
                {t('piso.regenerar')}
              </BotonConfirmar>
            </section>
          )}
          <BotonConfirmar onConfirmar={abandonar}>{t('piso.abandonar')}</BotonConfirmar>
        </aside>
      </div>
    </div>
  )
}
