"""Hash de contraseñas (Argon2id) y tokens JWT."""

from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.core.config import settings

_hasher = PasswordHasher()
# Hash de una contraseña cualquiera para igualar tiempos cuando el email no existe.
HASH_FICTICIO = _hasher.hash("contraseña-ficticia-para-igualar-tiempos")
ALGORITMO = "HS256"


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verificar_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def crear_token(usuario_id: int, ahora: datetime | None = None) -> tuple[str, datetime]:
    ahora = ahora or datetime.now(timezone.utc)
    expira = ahora + timedelta(hours=settings.jwt_expires_hours)
    payload = {"sub": str(usuario_id), "iat": ahora, "exp": expira}
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITMO), expira


def leer_token(token: str) -> int | None:
    """Devuelve el id de usuario del token, o None si no es válido o ha caducado."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITMO])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None
