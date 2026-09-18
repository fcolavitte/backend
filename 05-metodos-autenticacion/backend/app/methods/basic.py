"""Método 1 — BASIC AUTH (RFC 7617).

El más simple y el más limitado: el cliente manda email:password en CADA
request, codificados en base64 dentro del header `Authorization: Basic ...`.

⚠️ OJO: base64 NO es cifrado. Es codificación. Cualquiera puede decodificarlo:

    echo -n "demo@ejemplo.com:demo12345" | base64

Por eso Basic Auth SOLO es aceptable sobre HTTPS (que sí cifra el canal), y
normalmente para integraciones internas / primeros pasos, no para productos
con usuarios finales.

No hay "login" previo: cada request lleva las credenciales. No hay logout
del lado del servidor (el cliente solo deja de mandarlas).
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.auth_common import authenticate_user
from app.models import UserRead

router = APIRouter(prefix="/api/me", tags=["1 · Basic Auth"])

# Este objeto declara el security scheme "HTTPBasic" en el OpenAPI, así
# Swagger muestra un botón "Authorize" para este método.
basic_scheme = HTTPBasic()


@router.get(
    "/basic",
    response_model=UserRead,
    summary="Acceso con Basic Auth (credenciales en cada request)",
)
def me_basic(credentials: Annotated[HTTPBasicCredentials, Depends(basic_scheme)]):
    """Manda email:password en el header, en CADA request.

    El navegador/curl lo codifica en base64 y lo agrega por vos. Acá solo
    verificamos las credenciales, como en un login, pero esto pasa en
    CADA request, no una sola vez.
    """
    user = authenticate_user(credentials.username, credentials.password)
    if user is None:
        # WWW-Authenticate: Basic es OBLIGATORIO en el 401 de Basic Auth:
        # le dice al cliente "respondé con credenciales Basic".
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user