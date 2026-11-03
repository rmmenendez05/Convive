# Convive Constitution

## Core Principles

### I. Arquitectura API REST + SPA

- El backend MUST exponer una API REST en JSON bajo el prefijo `/api`.
- El frontend MUST ser una aplicación web que consume exclusivamente esa API.
- El repositorio MUST tener dos carpetas de primer nivel: `backend/` y `frontend/`.
- Las llamadas a la API desde el frontend MUST centralizarse en un único módulo cliente.

Razón: separar responsabilidades permite probar y desplegar cada parte de forma independiente.

### II. Pila tecnológica fijada

- Backend: Python 3.12, FastAPI y SQLAlchemy. Dependencias fijadas (versión exacta) en
  `requirements.txt`.
- Frontend: React 19 con Vite, solo componentes funcionales y hooks, React Router para la
  navegación.
- Base de datos: SQLite con migraciones Alembic versionadas en el repositorio. No se permite
  modificar el esquema sin una migración.
- No se introducen frameworks o librerías que sustituyan a los anteriores sin enmendar esta
  constitución.

Razón: una pila cerrada evita decisiones divergentes entre funcionalidades.

### III. Tests obligatorios (NO NEGOCIABLE)

- Todo endpoint MUST tener tests automatizados de su caso feliz y de cada error documentado.
- Backend con pytest; frontend con Vitest y React Testing Library.
- Cada criterio de aceptación MUST estar cubierto por al menos un test.
- Una tarea solo se considera terminada con todos los tests en verde; no se empieza la
  siguiente con tests fallando.

Razón: los criterios de aceptación solo son verificables si existen tests que los comprueben.

### IV. Seguridad y aislamiento por piso

- Las contraseñas MUST guardarse con hash (bcrypt o argon2); nunca en texto plano.
- Todos los endpoints, salvo registro e inicio de sesión, MUST exigir autenticación por token
  (JWT o sesión).
- Un usuario MUST ver y modificar únicamente datos de su propio piso. Ningún endpoint devuelve
  datos de otro piso.
- Ningún secreto se escribe en el código; toda configuración sensible llega por variables de
  entorno.

Razón: la app maneja datos personales y económicos de convivientes.

### V. Contratos consistentes: errores y dinero

- Todo error MUST responder con el formato `{ "error": { "code": "...", "message": "..." } }`
  y el código HTTP correcto (400, 401, 403, 404, 409).
- Los importes MUST representarse en céntimos como enteros; nunca en coma flotante.
- La moneda es única: euros.

Razón: un contrato uniforme simplifica el cliente y evita errores de redondeo.

### VI. Código limpio y spec viva

- Nombres claros y funciones pequeñas.
- Sin lógica de negocio en los controladores (routers): vive en la capa de servicios.
- Si cambia el comportamiento, la especificación MUST actualizarse en el mismo cambio; spec y
  código no pueden divergir.
- Ante una ambigüedad no resuelta en la spec, se pregunta antes de suponer.

Razón: la especificación es la fuente de verdad del proyecto (Spec-Driven Development).

## Despliegue y configuración

- Toda la aplicación MUST levantarse con `docker compose up --build`, sin instalar nada más
  que Docker.
- Servicio `backend`: imagen basada en `python:3.12-slim`, expone el puerto 8000.
- Servicio `frontend`: build multi-etapa (Node para compilar, Nginx para servir), expone el
  puerto 5173 u 80 y redirige `/api` al backend.
- El fichero SQLite vive en un volumen de Docker: los datos persisten tras `docker compose down`
  y un nuevo `up`.
- El repositorio incluye `.env.example` con todas las variables necesarias.
- El README MUST explicar cómo arrancar con Docker y cómo ejecutar los tests de backend y
  frontend.

## Flujo de desarrollo

- Se sigue el flujo de Spec Kit: constitución → especificación → aclaraciones → plan → tareas →
  implementación.
- Primero se implementa el núcleo; el módulo de gastos se añade después, como cambio sobre el
  núcleo terminado y con tests en verde.
- Definición de terminado: criterios de aceptación con test y en verde, arranque con Docker,
  persistencia de datos verificada, aislamiento por piso garantizado y spec actualizada.

## Governance

- Esta constitución prevalece sobre cualquier otra práctica o decisión del proyecto. Ningún
  plan, tarea o implementación puede contradecirla.
- Cada plan (`/speckit-plan`) MUST incluir una comprobación explícita de cumplimiento; cualquier
  desviación se justifica por escrito o se rechaza.
- Enmiendas: se proponen como cambio en este fichero, indicando motivo e impacto, y se
  actualiza la versión según SemVer:
  - MAJOR: eliminar o redefinir un principio de forma incompatible.
  - MINOR: añadir un principio o sección, o ampliar materialmente una regla.
  - PATCH: aclaraciones y correcciones de redacción.
- La guía de desarrollo en tiempo de ejecución está en `docs/SPECS.md` y en los artefactos de
  `specs/`.

**Version**: 1.0.0 | **Ratified**: 2026-11-03 | **Last Amended**: 2026-11-03
