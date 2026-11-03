# Convive

App web para que los compañeros de piso organicen la convivencia: cuentas, pisos con código de
invitación, gestión de miembros y un tablón de avisos. Interfaz en español e inglés.

- **Backend**: Python 3.12, FastAPI, SQLAlchemy, Alembic, SQLite (`backend/`)
- **Frontend**: React 19, Vite, React Router (`frontend/`)
- **Documentación**: [docs/](docs/README.md) · especificación en [docs/SPECS.md](docs/SPECS.md) ·
  artefactos de Spec Kit en [specs/](specs/001-nucleo-convive/)

## Arrancar con Docker

Solo necesitas Docker.

```bash
cp .env.example .env
# Edita .env y pon un JWT_SECRET largo y aleatorio, por ejemplo:
#   python3 -c "import secrets; print(secrets.token_urlsafe(48))"
docker compose up --build
```

- App: <http://localhost:5173>
- API: <http://localhost:5173/api> (a través de Nginx) o <http://localhost:8000/api> (directa)
- Documentación interactiva de la API: <http://localhost:8000/api/docs>

La base de datos SQLite vive en el volumen `convive-data`, así que los datos se conservan tras
`docker compose down` y un nuevo `up`. Para borrarlos: `docker compose down -v`.

Las migraciones (`alembic upgrade head`) se aplican solas al arrancar el backend.

## Tests

### Con Docker

```bash
# Backend (pytest)
docker compose run --rm backend pytest

# Frontend (Vitest + React Testing Library). node_modules va en un volumen aparte
# para no tocar el de tu máquina.
docker run --rm -v "$PWD/frontend":/app -v /app/node_modules -w /app node:22-alpine \
  sh -c "npm ci && npm test"
```

### En local

```bash
# Backend: Python 3.12
cd backend
python3.12 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest

# Frontend: Node 22
cd frontend
npm ci
npm test
```

## Desarrollo sin Docker

```bash
# Terminal 1: API en http://localhost:8000
cd backend && . .venv/bin/activate
alembic upgrade head
uvicorn app.main:app --reload

# Terminal 2: frontend en http://localhost:5173 (Vite redirige /api al puerto 8000)
cd frontend && npm run dev
```

## Estructura

```text
backend/
  app/core/       configuración, BD, errores, i18n, seguridad
  app/models/     modelos SQLAlchemy
  app/schemas/    validación de entrada y salida (Pydantic)
  app/services/   lógica de negocio
  app/routers/    endpoints HTTP (sin lógica)
  alembic/        migraciones
  tests/          pytest
frontend/
  src/api/        cliente único de la API
  src/context/    sesión (AuthContext) e idioma (LangContext)
  src/i18n/       textos en español e inglés
  src/components/ componentes reutilizables
  src/pages/      pantallas: Login, Registro, Bienvenida, Piso
  src/__tests__/  Vitest + React Testing Library
```
