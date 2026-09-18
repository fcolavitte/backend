"""Método 2 — SESSION BASED AUTH (cookie con id de sesión, estado en server).

El clásico "viejo y confiable" de la web:

  1. POST /api/auth/session/login  → verificamos credenciales, generamos un
     TOKEN OPACO (aleatorio, sin significado) y lo GUARDAMOS en el server
     (storage.sessions). Respondemos con una cookie `session_id`.
  2. Cada request → el navegador reenvía la cookie. Nosotros BUSCAMOS el
     token en nuestro almacén: "ah, sos el user 1". (lookup en server)
  3. POST /api/auth/session/logout → borramos la sesión del almacén.
     REVOCACIÓN INMEDIATA: la ventaja #1 de server-side.

La cookie es solo el VEHÍCULO: el id de sesión podría viajar también en un
header. Lo que define a Session Based es que el ESTADO vive en el server.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import APIKeyCookie

from app import storage
from app.auth_common import verify_login
from app.config import COOKIE_SECURE, SESSION_EXPIRE_MINUTES
from app.models import Message, Token, User, UserRead

router = APIRouter(prefix="/api", tags=["2 · Session Based (cookie)"])

# Lee la cookie `session_id` en cada request. auto_error=False para
# traducir a 401 nosotros (y no un 403 automático de FastAPI).
session_cookie = APIKeyCookie(name="session_id", auto_error=False)


def get_current_user_from_session(
    request: Request,
    session_id: str | None = Depends(session_cookie),
) -> User:
    """Dependencia que protege rutas con session based.

    Traduce la ausencia/invalidez de la sesión a un 401. El storage borra
    sesiones expiradas solas (revocación implícita por tiempo).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sesión inválida o expirada",
    )
    if session_id is None:
        raise credentials_exception

    data = storage.get_session(session_id)
    if data is None:
        raise credentials_exception

    user = storage.get_user_by_id(data["user_id"])
    if user is None:
        raise credentials_exception
    return user


@router.post("/auth/session/login", response_model=Token, summary="Login con sesión (cookie)")
def session_login(body: dict, response: Response):
    """Login: verifica credenciales, crea la sesión en el SERVER y la
    guarda en una cookie httpOnly.

    `httponly=True` → el JavaScript del navegador NO puede leer la cookie
    (mitiga XSS: un script inyectado no puede robar la sesión).
    `samesite="lax"` → mitiga CSRF (la cookie no viaja en requests cross-site).
    `secure=COOKIE_SECURE` → config-driven: false en dev (http), true en
    producción (HTTPS). La cookie con secure=True NO se guarda sobre http.
    """
    email = body.get("email", "")
    password = body.get("password", "")

    # verify_login: rate limit + timing attack + 401/429 genéricos.
    user = verify_login(email, password)

    session_token = storage.create_session(user.id)
    response.set_cookie(
        key="session_id",
        value=session_token,
        httponly=True,
        samesite="lax",
        secure=COOKIE_SECURE,
        max_age=SESSION_EXPIRE_MINUTES * 60,
    )
    return Token(access_token=session_token, token_type="cookie_session")


@router.get("/me/session", response_model=UserRead, summary="Perfil (session based)")
def me_session(current_user: Annotated[User, Depends(get_current_user_from_session)]):
    return current_user


@router.post("/auth/session/logout", response_model=Message, summary="Logout (borra la sesión)")
def session_logout(
    response: Response,
    request: Request,
    session_id: str | None = Depends(session_cookie),
):
    """Logout: borra la sesión del SERVER (revocación inmediata) y la cookie.

    Esto es lo que un JWT no puede hacer tan fácil: acá, el token dejó de
    valer EN EL MISMO INSTANTE porque ya no está en el almacén.
    """
    if session_id:
        storage.delete_session(session_id)
    response.delete_cookie("session_id")
    return Message(message="Sesión cerrada")