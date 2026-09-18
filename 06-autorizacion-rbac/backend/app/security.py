"""
Capa de seguridad — hash de contraseñas (Argon2) + JWT con claims de autorización.

Es la MISMA criptografía del módulo 05, con un agregado clave: el access token
ahora lleva claim de AUTORIZACIÓN:

    {
      "sub": "1",            # quién sos (autenticación)
      "role": "admin",       # qué rol tiene el usuario al emitir el token
      "tenant_id": 1,        # de qué empresa es
      "scope": "read write", # qué puede hacer ESTE token (lo limita el login)
      "iat": ..., "exp": ...
    }

⚠️ IMPORTANTE (lección central del módulo): el rol viaja en el token como
   REFERENCIA, pero la autorización SIEMPRE relee el rol actualizado del
   usuario en storage (dependencies.get_current_user). Por qué: si un admin
   degrada a alguien, el cambio tiene que ser efectivo en el MISMO request,
   no cuando expire el token. El único claim que la autorización lee del
   token es `scope` — porque el scope es del TOKEN, no del usuario.

Este archivo NO se modifica en la entrega.
"""

from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY

password_hash = PasswordHash.recommended()

# Hash "señuelo" anti timing attack (misma técnica que el módulo 05).
DUMMY_HASH = password_hash.hash("contraseña-señuelo-que-nadie-usa")


# ── Hash de contraseñas ────────────────────────────────────────────────────


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


# ── JWT ────────────────────────────────────────────────────────────────────


def create_access_token(subject: str, extra_claims: dict | None = None) -> str:
    """Crea un JWT firmado. `extra_claims` lleva role/tenant_id/scope al token.

    El payload está solo CODIFICADO (base64), no cifrado: NUNCA pongas
    secretos adentro. Role/tenant/scope no son secretos: son datos de
    autorización que la rutas releen (y revalidan contra storage).
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: dict = {
        "sub": subject,
        "iat": now,
        "exp": expire,
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Decodifica y VERIFICA la firma. Lanza jwt.InvalidTokenError si es inválido.

    NO capturamos acá: la capa HTTP (dependencies.get_current_user) traduce
    la excepción a 401. Security no sabe de HTTP (lección Módulo 04).
    """
    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
        options={"require": ["sub", "exp"]},
    )