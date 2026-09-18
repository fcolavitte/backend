"""
Capa de seguridad — hash de contraseñas (Argon2) + tokens.

Este archivo es la criptografía pura del módulo: NO sabe de HTTP, NO sabe de
cookies, NO sabe de routers. Solo define primitivas reutilizables por TODOS
los métodos de autenticación.

Buenas prácticas de la industria (2026):
  - Hash: pwdlib + Argon2id (ganador del Password Hashing Competition).
    NUNCA texto plano, NUNCA MD5/SHA1 (son rápidos → brute-force trivial).
  - JWT: pyjwt (el recomendado por la doc oficial de FastAPI, no python-jose).
  - algorithms=[...] SIEMPRE explícito (anti algorithm-confusion attack).
  - timezone.utc en la expiración (en lugar de datetime.now() a secas).
"""

from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe

import jwt
from pwdlib import PasswordHash

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY

# pwdlib configura el hash con el algoritmo RECOMENDADO (Argon2id).
# Es la misma librería y API que recomienda el tutorial oficial de FastAPI.
password_hash = PasswordHash.recommended()

# Hash "señuelo" para mitigar timing attacks: el login verifica SIEMPRE
# contra un hash, incluso cuando el usuario no existe. Así "email no existe"
# tarda lo mismo que "contraseña mal".
DUMMY_HASH = password_hash.hash("contraseña-señuelo-que-nadie-usa")


# ── Hash de contraseñas ────────────────────────────────────────────────────


def hash_password(password: str) -> str:
    """Convierte una contraseña en un hash Argon2id irreversible."""
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """¿Coincide la contraseña en texto plano con el hash guardado?

    Devuelve True/False. NUNCA lanza excepción si no coincide.
    """
    return password_hash.verify(plain_password, hashed_password)


# ── Tokens opacos (para Session Based y Token Auth) ────────────────────────


def new_opaque_token() -> str:
    """Genera un token opaco aleatorio (para sesiones y tokens opacos).

    `secrets.token_urlsafe` es criptográficamente seguro: 32 bytes aleatorios.
    Un token "opaco" es una cadena sin significado: el server lo guarda en su
    almacén y lo busca cuando llega. No lleva información adentro.
    """
    return token_urlsafe(32)


# ── JWT ────────────────────────────────────────────────────────────────────


def create_access_token(
    subject: str,
    extra_claims: dict | None = None,
    expires_minutes: int | None = None,
    issuer: str | None = None,
    audience: str | None = None,
) -> str:
    """Crea un JWT firmado.

    Claims importantes:
      - "sub": subject (el identificador del usuario).
      - "exp": expiración (momento en que el token deja de valer).
      - "iat": momento de emisión.
      - "iss"/"aud" (opcionales): issuer/audiencia — CLAVE en SSO/OIDC.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: dict = {
        "sub": subject,
        "iat": now,
        "exp": expire,
    }
    if extra_claims:
        payload.update(extra_claims)
    if issuer:
        payload["iss"] = issuer
    if audience:
        payload["aud"] = audience

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(
    token: str,
    *,
    issuer: str | None = None,
    audience: str | None = None,
) -> dict:
    """Decodifica y VERIFICA la firma de un JWT.

    - `algorithms=[ALGORITHM]` explícito: SIEMPRE. Sin esto, un atacante puede
      forzar algoritmos asimétricos (algorithm confusion attack).
    - Si expiró o la firma es inválida, lanza jwt.InvalidTokenError.
      NO capturamos acá: la capa HTTP decide cómo traducirla (401, 403...).
    - Issuer/audience se validan acá cuando el token lo requiere (SSO).

    Este archivo NO sabe de HTTP: no devuelve status codes, las excepciones
    se propagan y las traduce quien corresponda.
    """
    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
        issuer=issuer,
        audience=audience,
        options={"require": ["sub", "exp"]},
    )