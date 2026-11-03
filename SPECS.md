# Convive — Especificación para generar la aplicación

> Documento pensado para dárselo a un agente de IA (Claude Code, Copilot, Cursor…) siguiendo Spec-Driven Development.
> Está ordenado como el flujo de Spec-kit: **constitución → especificación → aclaraciones → plan → tareas**.
> Si usas Spec-kit, pega cada sección en su comando (`/speckit.constitution`, `/speckit.specify`, `/speckit.clarify`, `/speckit.plan`, `/speckit.tasks`).

---

## 0. Instrucciones para la IA

1. Lee el documento entero antes de escribir código.
2. La **constitución** (sección 1) es obligatoria: ninguna decisión puede contradecirla.
3. Implementa primero el **núcleo** (sección 2). El **módulo de gastos** (sección 3) va después, como un cambio sobre el núcleo ya terminado.
4. Si algo es ambiguo y no lo resuelve la sección 4, **pregunta antes de suponer**.
5. Cada tarea termina con sus tests en verde. No pases a la siguiente con tests fallando.
6. Si cambias el comportamiento, actualiza también este documento: la spec y el código no pueden divergir.

---

## 1. Constitución (reglas no negociables)

- **Arquitectura:** backend con API REST en JSON + frontend web que consume esa API. Repositorio con dos carpetas: `backend/` y `frontend/`.
- **Backend:** Python 3.12 con FastAPI y SQLAlchemy. Dependencias fijadas en `requirements.txt`. Tests con pytest.
- **Frontend:** React 19 con Vite. Componentes funcionales y hooks; React Router para la navegación. Las llamadas a la API se centralizan en un único módulo cliente. Tests con Vitest y React Testing Library.
- **Base de datos:** SQLite, con migraciones (Alembic) versionadas en el repo. El fichero de la base de datos vive en un volumen de Docker para no perder datos al reiniciar.
- **Docker:** toda la aplicación se levanta con `docker compose up --build`.
  - Servicio `backend`: imagen basada en `python:3.12-slim`, expone el puerto 8000.
  - Servicio `frontend`: build multi-etapa (Node para compilar, Nginx para servir), expone el puerto 5173 o 80 y redirige `/api` al backend.
  - Configuración por variables de entorno (`.env.example` en el repo); ningún secreto escrito en el código.
- **Tests obligatorios:** todo endpoint tiene tests automatizados de su caso feliz y de sus errores.
- **Seguridad:**
  - Contraseñas guardadas con hash (bcrypt o argon2). Nunca en texto plano.
  - Autenticación con token (JWT o sesión) en todos los endpoints salvo registro e inicio de sesión.
  - Un usuario solo ve y modifica datos de su propio piso.
- **Errores:** formato único `{ "error": { "code": "...", "message": "..." } }` con el código HTTP correcto (400, 401, 403, 404, 409).
- **Dinero:** importes en céntimos (enteros), nunca en coma flotante.
- **Código:** nombres claros, funciones pequeñas, sin lógica de negocio en los controladores.
- **Documentación:** README con cómo arrancar con Docker y cómo ejecutar los tests de backend y frontend.

---

## 2. Núcleo común (proyecto nuevo)

### 2.1 Visión

Convive es una app web para que los compañeros de piso organicen la convivencia sin grupos de WhatsApp caóticos.

### 2.2 Actores

| Actor | Descripción |
| --- | --- |
| Visitante | Persona sin sesión iniciada |
| Miembro | Usuario que pertenece a un piso |
| Administrador | Miembro que creó el piso; tiene permisos extra |

### 2.3 Historias de usuario y criterios de aceptación

**HU-01 · Registro**
Como visitante, quiero registrarme con email y contraseña para usar la app.
- Email válido y único; si ya existe → `409 email_ya_registrado`.
- Contraseña de al menos 8 caracteres; si no → `400`.
- Se guarda el hash de la contraseña, nunca el texto.

**HU-02 · Inicio de sesión**
Como visitante, quiero iniciar sesión para acceder a mi piso.
- Credenciales correctas → devuelve token.
- Credenciales incorrectas → `401` con mensaje genérico (no revelar si el email existe).

**HU-03 · Crear un piso**
Como usuario sin piso, quiero crear un piso para invitar a mis compañeros.
- Nombre obligatorio (1–60 caracteres); dirección opcional.
- Se genera un código de invitación único de 8 caracteres alfanuméricos.
- Quien lo crea pasa a ser administrador.
- Si el usuario ya pertenece a un piso → `409 ya_tiene_piso`.

**HU-04 · Unirse a un piso**
Como usuario sin piso, quiero unirme con un código de invitación.
- Código válido → el usuario pasa a ser miembro.
- Código inexistente → `404`.
- Un usuario solo puede estar en un piso a la vez → `409 ya_tiene_piso`.

**HU-05 · Ver el piso**
Como miembro, quiero ver el nombre del piso, sus miembros y sus roles.
- El código de invitación solo lo ve el administrador.

**HU-06 · Expulsar a un miembro**
Como administrador, quiero expulsar a un miembro del piso.
- Solo el administrador → si no, `403`.
- El administrador no puede expulsarse a sí mismo → `400`.

**HU-07 · Abandonar el piso**
Como miembro, quiero abandonar el piso.
- Ver la regla del administrador en la sección 4.

**HU-08 · Regenerar código de invitación**
Como administrador, quiero regenerar el código para que el anterior deje de valer.

**HU-09 · Publicar aviso**
Como miembro, quiero publicar un aviso corto en el tablón del piso.
- Texto obligatorio, máximo 280 caracteres.
- Se guardan autor y fecha.

**HU-10 · Ver el tablón**
Como miembro, quiero ver los avisos de mi piso, del más reciente al más antiguo.
- Nunca se muestran avisos de otros pisos.

**HU-11 · Borrar aviso**
Como autor del aviso o administrador, quiero borrarlo.
- Otro miembro → `403`.

### 2.4 Fuera de alcance del núcleo

Notificaciones push o por email, chat en tiempo real, app móvil, recuperación de contraseña, pagos reales.

---

## 3. Módulo de gastos compartidos (cambio sobre el núcleo)

> Implementar **después** de tener el núcleo terminado y con tests en verde. Describe solo lo que se añade o modifica.

### 3.1 Qué se añade

**HU-12 · Registrar un gasto**
Como miembro, quiero registrar un gasto indicando concepto, importe, quién pagó y entre quiénes se reparte.
- Importe > 0, en céntimos.
- Quien pagó y los participantes deben ser miembros del piso.
- Reparto a partes iguales; los céntimos sobrantes se asignan uno a uno a los primeros participantes por orden de alta.

**HU-13 · Ver gastos**
Como miembro, quiero ver la lista de gastos del piso, del más reciente al más antiguo.

**HU-14 · Ver saldos**
Como miembro, quiero ver cuánto debe o le deben a cada miembro.
- Saldo = lo que pagó − lo que le corresponde. La suma de todos los saldos es 0.

**HU-15 · Liquidar deudas**
Como miembro, quiero ver una propuesta de pagos mínimos para quedar a cero y registrar un pago entre dos miembros.
- Un pago registrado ajusta los saldos de ambos.

**HU-16 · Borrar un gasto**
Como quien lo registró o administrador, quiero borrar un gasto erróneo. Los saldos se recalculan.

### 3.2 Qué se modifica del núcleo

- **Expulsar o abandonar (HU-06, HU-07):** no se permite si el miembro tiene saldo distinto de 0 → `409 saldo_pendiente`.

---

## 4. Aclaraciones (decisiones tomadas)

| Pregunta | Decisión |
| --- | --- |
| ¿Qué pasa si el administrador abandona el piso? | El rol pasa al miembro más antiguo. Si era el único miembro, el piso se elimina con sus avisos. |
| ¿Puede haber varios administradores? | No, solo uno. |
| ¿Caduca el código de invitación? | No, pero el administrador puede regenerarlo (HU-08). |
| ¿Se pueden editar los avisos? | No, solo borrarlos. |
| ¿Moneda? | Solo euros. |
| ¿Qué pasa con los gastos de un miembro que se va? | No puede irse con saldo pendiente (sección 3.2); sus gastos históricos se conservan. |

---

## 5. Plan técnico

### 5.1 Modelo de datos

```
Usuario   (id, email UNIQUE, password_hash, nombre, creado_en)
Piso      (id, nombre, direccion NULL, codigo_invitacion UNIQUE, creado_en)
Miembro   (usuario_id PK/FK, piso_id FK, rol ['admin'|'miembro'], unido_en)
Aviso     (id, piso_id FK, autor_id FK, texto, creado_en)

-- Módulo de gastos
Gasto         (id, piso_id FK, concepto, importe_centimos, pagado_por FK, creado_por FK, creado_en)
Participacion (gasto_id FK, usuario_id FK, parte_centimos)
Pago          (id, piso_id FK, de_usuario FK, a_usuario FK, importe_centimos, creado_en)
```

`Miembro.usuario_id` es clave primaria: así se garantiza un piso por usuario.

### 5.2 Endpoints

| Método | Ruta | Descripción | HU |
| --- | --- | --- | --- |
| POST | `/api/auth/registro` | Crear cuenta | 01 |
| POST | `/api/auth/login` | Obtener token | 02 |
| POST | `/api/pisos` | Crear piso | 03 |
| POST | `/api/pisos/unirse` | Unirse con código | 04 |
| GET | `/api/pisos/mio` | Ver mi piso y miembros | 05 |
| DELETE | `/api/pisos/mio/miembros/{id}` | Expulsar miembro | 06 |
| POST | `/api/pisos/mio/abandonar` | Abandonar piso | 07 |
| POST | `/api/pisos/mio/codigo` | Regenerar código | 08 |
| POST | `/api/avisos` | Publicar aviso | 09 |
| GET | `/api/avisos` | Ver tablón | 10 |
| DELETE | `/api/avisos/{id}` | Borrar aviso | 11 |
| POST | `/api/gastos` | Registrar gasto | 12 |
| GET | `/api/gastos` | Ver gastos | 13 |
| GET | `/api/gastos/saldos` | Ver saldos y propuesta de liquidación | 14, 15 |
| POST | `/api/pagos` | Registrar pago | 15 |
| DELETE | `/api/gastos/{id}` | Borrar gasto | 16 |

### 5.3 Pantallas del frontend (React 19)

| Ruta | Pantalla | Contenido |
| --- | --- | --- |
| `/login`, `/registro` | Acceso | Formularios de inicio de sesión y registro |
| `/bienvenida` | Sin piso | Crear piso o unirse con código |
| `/piso` | Mi piso | Miembros, código (solo admin) y tablón de avisos |
| `/gastos` | Gastos | Lista, formulario de nuevo gasto, saldos y liquidación |

- Rutas protegidas: sin token se redirige a `/login`; con token pero sin piso, a `/bienvenida`.
- El token se guarda en memoria y en `localStorage`, y se envía en la cabecera `Authorization: Bearer`.
- Los formularios usan las Actions de React 19 (`useActionState`) para estados de envío y errores.

### 5.4 Estructura del repositorio

```
convive/
├── docker-compose.yml
├── .env.example
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic/
│   ├── app/          (main.py, models/, schemas/, routers/, services/)
│   └── tests/
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    ├── package.json
    └── src/          (api/, pages/, components/, context/)
```

---

## 6. Tareas (orden de implementación)

### Fase 1 · Núcleo
- [ ] T01 Estructura del repositorio (`backend/`, `frontend/`), dependencias, README y configuración de pytest y Vitest
- [ ] T01b Dockerfiles de backend y frontend, `docker-compose.yml` con volumen para SQLite y `.env.example`; comprobar que `docker compose up --build` levanta ambos servicios
- [ ] T02 Esquema de base de datos del núcleo
- [ ] T03 Registro e inicio de sesión con hash y token (HU-01, HU-02)
- [ ] T04 Middleware de autenticación y formato único de errores
- [ ] T05 Crear piso y unirse con código (HU-03, HU-04)
- [ ] T06 Ver piso, expulsar, abandonar y regenerar código (HU-05 a HU-08)
- [ ] T07 Tablón de avisos (HU-09 a HU-11)
- [ ] T08 Frontend del núcleo en React 19: cliente de API, rutas protegidas y pantallas de acceso, bienvenida y piso
- [ ] T09 Revisión: todos los criterios de aceptación cubiertos por tests

### Fase 2 · Módulo de gastos
- [ ] T10 Tablas de gastos, participaciones y pagos
- [ ] T11 Registrar, listar y borrar gastos con reparto exacto en céntimos (HU-12, HU-13, HU-16)
- [ ] T12 Cálculo de saldos y propuesta de liquidación mínima (HU-14, HU-15)
- [ ] T13 Bloquear expulsar/abandonar con saldo pendiente (sección 3.2)
- [ ] T14 Frontend de gastos en React 19 (pantalla `/gastos`)
- [ ] T15 Revisión final: tests en verde y spec actualizada

---

## 7. Definición de terminado

- Todos los criterios de aceptación tienen al menos un test y pasan.
- La app completa arranca con `docker compose up --build`, sin instalar nada más que Docker.
- Los datos persisten tras `docker compose down` y un nuevo `up`.
- Ningún endpoint devuelve datos de otro piso.
- Este documento refleja el comportamiento real del código.