"""
Lógica de autenticación compartida por TODOS los métodos.

Acá vive la regla de negocio: "¿estas credenciales corresponden a un usuario?".

Dos protecciones globales (aplican a TODOS los métodos con login):

1. Timing attack: cuando el email no existe, igual corremos verify_password
   contra DUMMY_HASH. Así "email inexistente" tarda lo mismo que "contraseña
   incorrecta" y un atacante no puede medir la diferencia.

2. Rate limiting: contamos intentos fallidos por email (app.rate_limit).
   Superado el máximo → 429. El login exitoso resetea el contador.
"""

from typing import Literal

from fastapi import HTTPException, status

from app import rate_limit, security, storage
from app.config import LOGIN_RATE_WINDOW_MINUTES
from app.models import User


def authenticate_user(email: str, password: str) -> User | None:
    """Verifica credenciales. Devuelve el User o None (mensaje genérico).

    NUNCA devuelve un 401 acá: la capa HTTP lo traduce. (Lección Módulo 04.)
    """
    email = email.lower().strip()

    user = storage.get_user_by_email(email)
    if user is None:
        # ⏱️ Timing attack mitigation: verificamos contra un hash señuelo
        # para que la respuesta tarde lo mismo que un password inválido.
        security.verify_password(password, security.DUMMY_HASH)
        return None

    if not security.verify_password(password, user.password_hash):
        return None

    return user


def verify_login(
    email: str,
    password: str,
    www_authenticate: Literal["Bearer", "Basic"] | None = None,
) -> User:
    """Verifica credenciales con rate limiting. Lanza 401 (fallo) o 429 (bloqueado).

    El orden es importante (por eso está acá y no replicado en cada router):
      1. ¿Está bloqueado por intentos fallidos? → 429 ANTES de tocar Argon2
         (un atacante no puede forzar el hash caro en bucle).
      2. ¿Credenciales válidas? → 401 genérico + anotamos el fallo.
      3. ¿Login exitoso? → reseteamos el contador y devolvemos el User.
    """
    if rate_limit.is_blocked(email):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos fallidos. Esperá y volvé a intentar.",
            headers={"Retry-After": str(LOGIN_RATE_WINDOW_MINUTES * 60)},
        )

    user = authenticate_user(email, password)
    if user is None:
        rate_limit.register_failure(email)
        headers = {"WWW-Authenticate": www_authenticate} if www_authenticate else None
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers=headers,
        )

    rate_limit.clear_failures(email)
    return user