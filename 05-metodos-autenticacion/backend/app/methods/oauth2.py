"""Método 6 — OAUTH 2.0 (password flow) con JWT como access token.

ESTE es el patrón que enseña el tutorial oficial de FastAPI ("OAuth2 with
Password, Bearer with JWT tokens"). Es la COMBINACIÓN de las piezas:

  - OAuth 2.0 = el PROTOCOLO (el flujo, los grant types, los endpoints /token).
  - JWT       = el FORMATO del access token.
  - Bearer    = el ESQUEMA de transporte (header Authorization).

Podés tener OAuth2 con tokens opacos (como el método 3), o OAuth2 con JWT
(acá). El protocolo no impone el formato del token: esa es la lección.

El "password flow" es solo UNO de los grant types de OAuth 2.0 (pensado para
apps de primera parte, donde el cliente es de confianza). Los flows de
terceros (authorization code + PKCE) son los que se usan para "Login with
Google/GitHub/..." — eso es SSO (método 7).
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import InvalidTokenError

from app import security
from app.auth_common import verify_login
from app.models import Token, User, UserRead

router = APIRouter(prefix="/api", tags=["6 · OAuth2 (password flow) + JWT"])

# Este es el scheme CANÓNICO del tutorial de FastAPI: el Swagger muestra el
# botón "Authorize" y la flecha verde si pegás un token válido.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/oauth2/token", auto_error=False)


def get_current_user_oauth2(token: str | None = Depends(oauth2_scheme)) -> User:
    """Igual que get_current_user_from_jwt: decodifica y verifica la firma.

    El token llega por el header Authorization: Bearer, lo decodificamos,
    y confiamos en que la firma + exp prueban quién es el usuario. No hay
    lookup en server: STATELESS.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise credentials_exception

    try:
        payload = security.decode_token(token)
        user_id = int(payload["sub"])
    except (InvalidTokenError, KeyError, ValueError):
        raise credentials_exception

    from app import storage  # import local para evitar ciclo

    user = storage.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user


@router.post("/auth/oauth2/token", response_model=Token, summary="OAuth2 password flow → JWT")
async def oauth2_token_login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """El endpoint /token del OAuth2 password flow.

    Contrato OAuth2 estándar:
      - POST, form-urlencoded (NO JSON) con username, password, grant_type.
      - Responde {"access_token": ..., "token_type": "bearer"}.

    Práctica de la industria (2026) con este patrón:
      - access token de corta vida (15-30 min) → acá 30 min.
      - refresh token de larga vida con rotación → fuera de alcance acá,
        pero es el siguiente paso real en producción.
      - hash con Argon2 (pwdlib), firma con pyjwt, algorithms explícito.
    """
    user = verify_login(form_data.username, form_data.password, www_authenticate="Bearer")

    access_token = security.create_access_token(subject=str(user.id))
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me/oauth2", response_model=UserRead, summary="Perfil (OAuth2 + JWT)")
def me_oauth2(current_user: Annotated[User, Depends(get_current_user_oauth2)]):
    return current_user