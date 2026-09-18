"""Método 5 — COOKIE BASED AUTH (JWT en cookie httpOnly).

El mismo JWT del método 4, pero el VEHÍCULO cambia: en vez del header
`Authorization`, el token viaja en una cookie httpOnly.

¿Por qué importa el vehículo?

  - Header + localStorage (SPA): simple, pero vulnerable a XSS (un script
    inyectado lee el localStorage y roba el token).
  - Cookie httpOnly: el JS NO la puede leer → mitiga XSS. PERO abre CSRF
    (el navegador envía la cookie automáticamente en requests cross-site),
    que se mitiga con SameSite + token anti-CSRF.

Es un tradeoff: elegís QUÉ ataque mitigás (XSS vs CSRF). Ninguna es "la
mejor" en abstracto — depende de tu amenaza.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import APIKeyCookie
from jwt import InvalidTokenError

from app import storage, security
from app.auth_common import verify_login
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, COOKIE_SECURE
from app.models import Message, Token, User, UserRead

router = APIRouter(prefix="/api", tags=["5 · Cookie Based (JWT en cookie)"])

access_cookie = APIKeyCookie(name="access_token", auto_error=False)


def get_current_user_from_jwt_cookie(token: str | None = Depends(access_cookie)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
    )
    if token is None:
        raise credentials_exception

    try:
        payload = security.decode_token(token)
        user_id = int(payload["sub"])
    except (InvalidTokenError, KeyError, ValueError):
        raise credentials_exception

    user = storage.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user


@router.post("/auth/jwt-cookie/login", response_model=Token, summary="Login → JWT en cookie httpOnly")
def jwt_cookie_login(body: dict, response: Response):
    email = body.get("email", "")
    password = body.get("password", "")

    user = verify_login(email, password)

    access_token = security.create_access_token(subject=str(user.id))
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=COOKIE_SECURE,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    # Devolvemos el token igual (por si un cliente lo quiere guardar),
    # pero el vehículo canónico de este método es la cookie.
    return Token(access_token=access_token, token_type="cookie")


@router.get("/me/jwt-cookie", response_model=UserRead, summary="Perfil (JWT en cookie)")
def me_jwt_cookie(current_user: Annotated[User, Depends(get_current_user_from_jwt_cookie)]):
    return current_user


@router.post("/auth/jwt-cookie/logout", response_model=Message, summary="Logout (borra cookie)")
def jwt_cookie_logout(response: Response):
    """Logout: borra la cookie. El JWT sigue siendo válido hasta exp.

    Esta es la diferencia con Session Based: acá NO hay estado en el server
    para borrar. El "logout" solo saca la cookie del navegador; si alguien
    copió el JWT, sigue valiendo hasta que expire.
    """
    response.delete_cookie("access_token")
    return Message(message="Cookie eliminada (el JWT sigue válido hasta expirar)")