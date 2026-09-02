"""
Inyección de dependencias — el "cableado" entre capas + AUTENTICACIÓN.

Como en el Módulo 03, acá CONECTAMOS las capas. Pero ahora agregamos una
pieza nueva: la dependencia que PROTEGE rutas.

    get_session          → crea una Session por request
    get_user_repository  → recibe la Session, devuelve un repository
    get_auth_service     → recibe el repository, devuelve un service
    get_current_user     → recibe el token + el repository, devuelve el User

La última es LA lección de hoy: cómo un endpoint sabe QUIÉN está hablando.

COMPLETÁ únicamente `get_current_user`. El resto ya viene cableado.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlmodel import Session

from app.database import engine
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.security import decode_token
from app.services.auth_service import AuthService

# El "extractor" de tokens. Le dice a FastAPI: "buscá el token en el header
# `Authorization: Bearer <token>`". El `tokenUrl` es la ruta del login (la
# que emite tokens) — aparece en el botón "Authorize" del Swagger.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_session():
    """Una Session nueva por cada request."""
    with Session(engine) as session:
        yield session


def get_user_repository(session: Session = Depends(get_session)) -> UserRepository:
    """Construye el repository con la Session del request."""
    return UserRepository(session)


def get_auth_service(
    repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    """Construye el service con su repository."""
    return AuthService(repository)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    repository: UserRepository = Depends(get_user_repository),
) -> User:
    """
    Protege una ruta: resuelve QUIÉN es el usuario a partir del token.

    Es una dependencia: cualquier endpoint que la pida en `Depends()` queda
    protegido (si falla, el endpoint nunca se ejecuta).

    Pasos (desarrollá cada uno):
      1. Intentá `payload = decode_token(token)`.
      2. Si `decode_token` lanza un error (firma inválida, expirado...),
         levantá un 401. Capturá la excepción del JWT con:
             `from jwt import InvalidTokenError`  →  `except InvalidTokenError:`
         El 401 debe incluir el header `WWW-Authenticate: Bearer` (lo pide
         la especificación HTTP).
      3. Sacá el `sub` del payload y convertilo a int: ese es el user id.
         (En `create_access_token` guardaste el id como subject.)
      4. Buscá el user: `repository.get_by_id(user_id)`.
      5. Si no existe → 401 (token válido pero usuario borrado/inexistente).
      6. Devolvé el user.

    Pista de la exception:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    🧠 ¿Dónde vive el 401? Acá, que es la capa HTTP. `decode_token` solo
    deja propagar la excepción del JWT; la traducción a status code la hacés
    vos acá. Es EXACTAMENTE el mismo criterio que el 404 del Módulo 03.
    """
    raise NotImplementedError("TODO: implementar get_current_user")
