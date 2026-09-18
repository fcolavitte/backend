"""Método 4 — JWT en header Authorization (stateless).

El método estrella de FastAPI. Diferencias con Token Auth (método 3):

  - El token NO es opaco: es un JWT firmado que LLEVA LA INFORMACIÓN adentro
    (header.payload.signature). El server lo decodifica y verifica la firma.
  - NO hay estado en el server: no guardamos nada en storage. El "estado"
    viaja dentro del token firmado. Escala horizontal sin almacén compartido.
  - Revocación: DIFÍCIL. El token vale hasta que expira ("exp"). Para
    revocar antes hay que armar una blacklist (que reintroduce estado).

Lección: JWT es un FORMATO de token, no un protocolo. Acá usamos un login
JSON simple a mano (sin protocolo OAuth2). El método 6 muestra el mismo JWT
pero emitido por un flujo OAuth2.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from jwt import InvalidTokenError

from app import storage, security
from app.auth_common import verify_login
from app.models import Token, User, UserRead

router = APIRouter(prefix="/api", tags=["4 · JWT (header)"])

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user_from_jwt(
    request: Request,
    credentials: dict | None = Depends(bearer_scheme),
) -> User:
    """Dependencia que protege rutas con JWT (header).

    decode_token verifica la firma y la expiración. La excepción del JWT se
    captura ACÁ (capa HTTP) y se traduce a 401 — el security.py no sabe de
    HTTP (misma lección del Módulo 04).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise credentials_exception

    try:
        payload = security.decode_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (InvalidTokenError, KeyError, ValueError):
        raise credentials_exception

    user = storage.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user


@router.post("/auth/jwt/login", response_model=Token, summary="Login → JWT (header)")
def jwt_login(body: dict):
    """Login JSON simple → JWT firmado.

    NO guardamos nada en el server: el token ES la credencial. El cliente lo
    manda en `Authorization: Bearer <token>` en cada request.

    ⚠️ El payload del JWT está solo CODIFICADO (base64), no cifrado: cualquiera
    puede leerlo. Por eso NUNCA pongas secretos adentro (contraseñas, datos
    sensibles). Solo lo mínimo para identificar (sub) + exp/iat.
    """
    email = body.get("email", "")
    password = body.get("password", "")

    user = verify_login(email, password, www_authenticate="Bearer")

    access_token = security.create_access_token(subject=str(user.id))
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me/jwt", response_model=UserRead, summary="Perfil (JWT en header)")
def me_jwt(current_user: Annotated[User, Depends(get_current_user_from_jwt)]):
    return current_user