# Quickstart: Núcleo de Convive

## Arrancar

```bash
cp .env.example .env          # cambia JWT_SECRET por un valor largo y aleatorio
docker compose up --build
```

- Frontend: http://localhost:5173
- API: http://localhost:5173/api (a través de Nginx) o http://localhost:8000/api (directo)

## Tests

```bash
docker compose run --rm backend pytest
docker run --rm -v "$PWD/frontend":/app -w /app node:22-alpine sh -c "npm ci && npm test"
# o, en local con Node 22: cd frontend && npm ci && npm test
```

En local sin Docker: `cd backend && pip install -r requirements.txt && pytest`.

## Validación manual (recorrido de las historias)

1. **US1**: en `/registro` crea "Ana" (`ana@test.com`, `secreto123`). Repite el registro → aviso
   "Ya existe una cuenta con ese email". Inicia sesión con contraseña errónea → "Email o
   contraseña incorrectos".
2. **US2**: Ana llega a `/bienvenida`, crea el piso "Calle Mayor 3" y ve su código. En otra
   ventana privada, registra a "Luis" y únete con el código (en minúsculas también vale).
3. **US3**: Luis ve el piso con Ana (admin) y él (miembro) pero no ve el código.
4. **US4**: Luis publica "Mañana viene el fontanero". Ana lo ve arriba del tablón. Luis no puede
   borrar avisos de Ana; Ana sí puede borrar el de Luis.
5. **US5**: Ana regenera el código (el viejo da "No hay ningún piso con ese código"). Registra a
   "Marta" y únela. Ana expulsa a Marta (sus avisos desaparecen). Ana abandona → Luis pasa a
   admin. Luis abandona → el piso se elimina.
6. **Idioma**: cambia a English con el selector; textos y errores salen en inglés y se mantiene
   al recargar.
7. **Persistencia**: `docker compose down && docker compose up` → las cuentas y avisos siguen.

## Comprobaciones rápidas con curl

```bash
curl -s -X POST localhost:8000/api/auth/login -H 'Content-Type: application/json' \
  -H 'Accept-Language: en' -d '{"email":"x@x.com","password":"malamala"}'
# {"error":{"code":"credenciales_invalidas","message":"Incorrect email or password"}}
```
