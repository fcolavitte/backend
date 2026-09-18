"""Método 3 — TOKEN AUTH (token opaco en header Authorization).

Igual filosofía que Session Based (el server guarda estado), pero el token
viaja en el header `Authorization: Bearer <token>` en lugar de una cookie.
Es la forma de autenticación "clásica" de las APIs: pensá para clientes que
NO son un navegador (apps móviles, otras APIs, CLIs).

  - El token es OPACO: no lleva información adentro, solo un string aleatorio.
  - El server lo guarda (storage.api_tokens) y lo busca en cada request.
  - Logout → borramos el token del almacén (revocación inmediata).

Este flujo (POST /login con form + Header Bearer) es EXACTAMENTE lo que hace
el "OAuth2 password flow" de FastAPI — pero el método siguiente (OAuth2) le
suma el protocolo y el JWT. Fijate la diferencia: el ESQUEMA de transporte es
idéntico; lo que cambia es qué hay dentro del token.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app import storage
from app.auth_common import verify_login
from app.models import Message, Token, User, UserRead

router = APIRouter(prefix="/api", tags=["3 · Token Auth (opaco en header)"])

# OAuth2PasswordBearer solo lee el header `Authorization: Bearer <token>`.
# El tokenUrl es para que Swagger sepa dónde pedir un token nuevo.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token/login", auto_error=False)

# Delete; rewriting syntax guard to avoid duplicate:
# (se mantiene igual pero con auto_error=False para traducir a 401)


def get_current_user_from_token(token: str | None = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise credentials_exception

    data = storage.get_api_token(token)
    if data is None:
        raise credentials_exception

    user = storage.get_user_by_id(data["user_id"])
    if user is None:
        raise credentials_exception
    return user


@router.post("/auth/token/login", response_model=Token, summary="Login → token opaco")
def token_login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Login con form data (username/password) → token OPACO guardado en server.

    Usamos OAuth2PasswordRequestForm (form, no JSON) a propósito: es el mismo
    contrato que usa el OAuth2 password flow, así Swagger puede pedir un token
    desde su botón Authorize y probar el flujo entero en /docs.
    """
    user = verify_login(form_data.username, form_data.password, www_authenticate="Bearer")

    opaque_token = storage.create_api_token(user.id)
    return Token(access_token=opaque_token, token_type="bearer")


@router.get("/me/token", response_model=UserRead, summary="Perfil (token opaco en header)")
def me_token(current_user: Annotated[User, Depends(get_current_user_from_token)]):
    return current_user


@router.post("/auth/token/logout", response_model=Message, summary="Logout (revoca el token)")
def token_logout(authorization: str | None = Header(default=None)):
    """Logout: borra el token del almacén → revocación inmediata."""
    if authorization and authorization.lower().startswith("bearer "):
        storage.delete_api_token(authorization.split(" ", 1)[1].strip())
    return Message(message="Token revocado")