"""Mensajes de error en español e inglés. Los códigos no cambian con el idioma."""

IDIOMAS = ("es", "en")
IDIOMA_POR_DEFECTO = "es"

MENSAJES: dict[str, dict[str, str]] = {
    "datos_invalidos": {
        "es": "Los datos enviados no son válidos",
        "en": "The submitted data is not valid",
    },
    "no_autenticado": {"es": "Tienes que iniciar sesión", "en": "You need to sign in"},
    "credenciales_invalidas": {
        "es": "Email o contraseña incorrectos",
        "en": "Incorrect email or password",
    },
    "email_ya_registrado": {
        "es": "Ya existe una cuenta con ese email",
        "en": "An account with that email already exists",
    },
    "ya_tiene_piso": {"es": "Ya perteneces a un piso", "en": "You already belong to a flat"},
    "sin_piso": {
        "es": "Todavía no perteneces a ningún piso",
        "en": "You don't belong to a flat yet",
    },
    "codigo_invalido": {
        "es": "No hay ningún piso con ese código",
        "en": "There is no flat with that code",
    },
    "permiso_denegado": {
        "es": "No tienes permiso para hacer esto",
        "en": "You are not allowed to do this",
    },
    "no_puede_expulsarse": {
        "es": "No puedes expulsarte a ti mismo",
        "en": "You cannot remove yourself",
    },
    "miembro_no_encontrado": {
        "es": "Esa persona no es miembro del piso",
        "en": "That person is not a member of the flat",
    },
    "aviso_no_encontrado": {"es": "El aviso no existe", "en": "The notice does not exist"},
    "no_encontrado": {"es": "Recurso no encontrado", "en": "Resource not found"},
    "metodo_no_permitido": {"es": "Método no permitido", "en": "Method not allowed"},
    "error_interno": {
        "es": "Ha ocurrido un error inesperado",
        "en": "An unexpected error occurred",
    },
}


def idioma_de(accept_language: str | None) -> str:
    """Devuelve 'es' o 'en' según el primer idioma de la cabecera Accept-Language."""
    if not accept_language:
        return IDIOMA_POR_DEFECTO
    primero = accept_language.split(",")[0].split(";")[0].strip().lower()
    base = primero.split("-")[0]
    return base if base in IDIOMAS else IDIOMA_POR_DEFECTO


def mensaje(code: str, idioma: str) -> str:
    textos = MENSAJES.get(code, MENSAJES["error_interno"])
    return textos.get(idioma, textos[IDIOMA_POR_DEFECTO])
