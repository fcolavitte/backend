"""
Capa de presentación (Controller) — endpoints de AUTENTICACIÓN.

COMPLETÁ los endpoints marcados con TODO. Acá viven:
  - POST /api/auth/register → crea un usuario (devuelve 201)
  - POST /api/auth/login    → verifica credenciales y devuelve un JWT

El controller recibe el request, delega en el service y traduce el
resultado a HTTP. NO hashea, NO habla con la base, NO verifica contraseñas:
solo traduce `User`/`None` a status codes y JSON.

MIRÁ `health_controller.py` (resuelto) para ver cómo recibir el service
con `Depends(get_auth_service)`.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_auth_service
from app.models.user import Token, UserCreate, UserLogin, UserRead
from app.security import create_access_token
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(body: UserCreate, service: AuthService = Depends(get_auth_service)):
    """
    POST /api/auth/register — crea un usuario.

    - Si `service.register_user(body)` devuelve None → el email ya existe.
      Traducilo a un `409 Conflict` (el recurso ya existe).
    - Si devuelve un User → lo devolvés (FastAPI lo serializa con UserRead,
      que NO incluye el hash).
    """
    raise NotImplementedError("TODO: implementar register")


@router.post("/login", response_model=Token)
def login(body: UserLogin, service: AuthService = Depends(get_auth_service)):
    """
    POST /api/auth/login — verifica credenciales y emite un JWT.

    - Si `service.authenticate_user(body.email, body.password)` devuelve None
      → credenciales inválidas. Devuelve un `401` con mensaje GENÉRICO:
      "Email o contraseña incorrectos". NUNCA digas "el email no existe" o
      "la contraseña es incorrecta" por separado: eso es user enumeration.
    - Si devuelve un User → creá el token con
      `create_access_token(str(user.id))` y devolvé `Token(access_token=..., token_type="bearer")`.

    🧠 El `sub` del token es el ID del usuario (como string). Por eso en
    `get_current_user` se hace `int(payload["sub"])`.
    """
    raise NotImplementedError("TODO: implementar login")
