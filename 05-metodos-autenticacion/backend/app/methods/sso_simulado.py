"""Método 7 — SSO (Single Sign-On), simulado con flujo OIDC.

SSO NO es un método más del mismo nivel: es la EXPERIENCIA de loguearse
una vez en un proveedor (Google, Keycloak, tu empresa) y acceder a VARIOS
servicios sin volver a loguearse. Se IMPLEMENTA con protocolos: OIDC
(sobre OAuth 2.0) o SAML. OIDC emite un id_token que ES un JWT.

Como no podemos levantar un Keycloak/Google real en un módulo autocontenido,
lo simulamos de forma didáctica y HONESTA:

  - POST /api/sso/simulate  → actúa como el IdP: emite un JWT con claims
    estándar de OIDC (iss, aud, sub, email, name, exp). En la vida real
    este token lo emite Google/Keycloak y firma con SU clave (JWKS).
  - GET  /api/me/sso        → actúa como el servicio: valida el token del
    tercero (firma, issuer, audiencia, expiración) y hace "just-in-time
    provisioning": si el email no existe, crea el usuario local.

Las piezas del SSO que SÍ están de verdad acá:
  - El token lo emite un "tercero" (otra identidad = claims de OIDC).
  - Validamos iss (¿viene del IdP que espero?) y aud (¿fue emitido PARA
    nuestra app?). Esos checks son OBLIGATORIOS en producción.
  - El usuario local se crea al vuelo (JIT provisioning) — patrón real.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jwt import InvalidTokenError

from app import security, storage
from app.config import SSO_CLIENT_ID, SSO_ISSUER
from app.models import Message, SSOExplain, Token, User, UserRead
from pydantic import EmailStr

router = APIRouter(prefix="/api", tags=["7 · SSO (OIDC simulado)"])

bearer_scheme = HTTPBearer(auto_error=False)


@router.get("/sso/explain", response_model=SSOExplain, summary="¿Qué es SSO? (flujo OIDC)")
def sso_explain():
    """El flujo OIDC de verdad (authorization code), en 7 pasos."""
    return SSOExplain(
        flow="OIDC authorization code flow (simulado para el ejemplo)",
        steps=[
            "1. El usuario entra a TU app y clickea 'Login with IdP'.",
            "2. Tu app redirige al IdP: /authorize?client_id=...&redirect_uri=...",
            "3. El usuario se autentica EN EL IdP (o ya tiene sesión → SSO).",
            "4. El IdP redirige a tu app con un code (corto, de un solo uso).",
            "5. Tu app cambia el code por tokens: POST /token (code + client_secret).",
            "6. El IdP devuelve id_token (JWT con iss/aud/sub/email) + access_token.",
            '7. Tu app VALIDA el id_token (firma, iss, aud, exp) y confía: "es el user".',
        ],
    )


@router.post("/sso/simulate", response_model=Token, summary="El IdP emite un id_token (simulado)")
def sso_simulate(body: dict):
    """Simula al proveedor de identidad (Google/Keycloak) emitiendo un JWT.

    En producción este token lo emite el IdP REAL, firmado con SU clave
    (los servicios lo validan contra el JWKS público del proveedor). Acá
    firmamos con nuestra clave para no depender de infra, pero los CLAIMS
    son los reales del estándar OIDC:

      - iss: quién emitió el token (el IdP).
      - aud: PARA QUIÉN fue emitido (nuestra app cliente).
      - sub: el identificador del usuario EN EL IdP.
      - email, name: claims de perfil (solo con el scope adecuado).
    """
    email = body.get("email", "")
    name = body.get("name", "Usuario SSO")

    if not email:
        raise HTTPException(status_code=422, detail="email es requerido")

    # El IdP NO conoce el id local: usa su propio sub (el email acá).
    # Nuestra app mapeará ese sub → usuario local (JIT provisioning).
    id_token = security.create_access_token(
        subject=email,
        extra_claims={"name": name, "email": email},
        issuer=SSO_ISSUER,
        audience=SSO_CLIENT_ID,
        expires_minutes=5,  # id_tokens de corta vida
    )
    return Token(access_token=id_token, token_type="id_token")


def get_current_user_from_sso(credentials: dict | None = Depends(bearer_scheme)) -> User:
    """Valida el token del TERCERO y resuelve el usuario local (JIT).

    Los 3 checks OBLIGATORIOS de OIDC:
      - firma + exp  → decode_token (con algorithms explícito)
      - iss          → el token debe venir del IdP que espero
      - aud          → el token debe estar emitido PARA NUESTRA app

    Just-in-time provisioning: si el email aún no tiene usuario local,
    lo creamos con un password aleatorio (el usuario nunca usará password
    acá: entra SIEMPRE por SSO).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token SSO inválido",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise credentials_exception

    try:
        payload = security.decode_token(
            credentials.credentials,
            issuer=SSO_ISSUER,
            audience=SSO_CLIENT_ID,
        )
        email = payload["email"]
    except (InvalidTokenError, KeyError, ValueError):
        raise credentials_exception

    user = storage.get_user_by_email(email)
    if user is None:
        # JIT provisioning: el usuario entra por SSO, no por password.
        import secrets  # noqa: PLC0415

        from app.models import UserCreate  # noqa: PLC0415

        user = storage.create_user(
            UserCreate(
                email=email,
                name=payload.get("name", email),
                password=secrets.token_urlsafe(16),
            )
        )
    return user


@router.get("/me/sso", response_model=UserRead, summary="Perfil (SSO — token de IdP validado)")
def me_sso(current_user: Annotated[User, Depends(get_current_user_from_sso)]):
    return current_user