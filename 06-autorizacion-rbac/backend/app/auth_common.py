"""
Lógica de autenticación compartida por el módulo (login).

Igual que en el módulo 05, con la protección anti timing attack:
cuando el email no existe, igual corremos verify_password contra DUMMY_HASH
para que "email inexistente" tarde lo mismo que "contraseña incorrecta".

NOTA: el rate limiting del login (429) pertenece al módulo 05. Acá el foco
es la AUTORIZACIÓN; la autenticación ya fue evaluada y se reutiliza tal cual.

Este archivo NO se modifica en la entrega.
"""

from fastapi import HTTPException, status

from app import security, storage
from app.models import User


def authenticate_user(email: str, password: str) -> User | None:
    """Verifica credenciales. Devuelve el User o None (mensaje genérico).

    NUNCA devuelve un 401 acá: la capa HTTP (auth_controller) lo traduce.
    """
    email = email.lower().strip()

    user = storage.get_user_by_email(email)
    if user is None:
        # ⏱️ Timing attack mitigation: mismo costo que un password inválido.
        security.verify_password(password, security.DUMMY_HASH)
        return None

    if not security.verify_password(password, user.password_hash):
        return None

    return user


def verify_login(email: str, password: str) -> User:
    """Verifica credenciales y traduce el fallo a 401 (mensaje genérico)."""
    user = authenticate_user(email, password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user