"""
Capa de seguridad — hash de contraseñas + tokens JWT.

COMPLETÁ las funciones marcadas con TODO. Este es EL archivo de la clase:
acá vivís las dos operaciones más importantes de la seguridad de usuarios.

Hay dos responsabilidades separadas (y no mezclarlas es la lección):

    1. HASH de contraseñas (Argon2, vía pwdlib).
       NUNCA guardamos la contraseña en texto plano. Guardamos un hash:
       una función irreversible que nos deja VERIFICAR ("esta contraseña
       coincide con este hash?") pero no RECUPERAR la contraseña original.

    2. JWT: crear y decodificar tokens FIRMADOS.
       El token es un string que el server firma con el SECRET_KEY. Quien
       no tenga la clave no puede fabricar ni alterar un token válido.
"""

from datetime import datetime, timedelta, timezone

import jwt

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY

# pwdlib configura el hashing con el algoritmo RECOMENDADO (Argon2id).
# Argon2 es el ganador del Password Hashing Competition: diseñado para ser
# lento y costoso, lo que hace inviable el brute-force con GPUs.
# Es la misma librería y API que recomienda la doc oficial de FastAPI hoy.
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Convierte una contraseña en texto plano en un hash irreversible.

    Pista: `password_hash.hash(password)`.
    """
    raise NotImplementedError("TODO: implementar hash_password")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con un hash.

    Pista: `password_hash.verify(plain_password, hashed_password)`.
    Devuelve True/False — NUNCA lanza si no coincide.
    """
    raise NotImplementedError("TODO: implementar verify_password")


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    """
    Crea un JWT firmado para el usuario identificado por `subject`.

    El token lleva dos claims importantes:
      - "sub"  → el subject (identificador del usuario)
      - "exp"  → la expiración (momento en que el token deja de valer)

    Pistas:
      1. Armá un dict `payload` con "sub" = subject.
      2. Calculá la expiración:
           expire = datetime.now(timezone.utc) + timedelta(minutes=...)
         usando `expires_minutes` o, si es None, ACCESS_TOKEN_EXPIRE_MINUTES.
      3. Agregá `payload["exp"] = expire`.
      4. `return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)`.

    ⚠️ Importante: usá `datetime.now(timezone.utc)`. Sin timezone, el cálculo
    de expiración es frágil y rompe en distintos husos horarios.
    """
    raise NotImplementedError("TODO: implementar create_access_token")


def decode_token(token: str) -> dict:
    """
    Decodifica y VERIFICA la firma de un JWT.

    Pista: `return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])`.

    ⚠️ CRÍTICO: `algorithms=[ALGORITHM]` va EXPLÍCITO. Si no lo pasás,
    permitís el "algorithm confusion attack" (un atacante puede forzar
    algoritmos asimétricos que el server no debería aceptar). Siempre
    declarás qué algoritmos son válidos.

    Si el token expiró o la firma es inválida, `jwt.decode` lanza una
    excepción (`jwt.ExpiredSignatureError`, `jwt.InvalidTokenError`...).
    NO la captures acá: dejala propagar. El que la captura y la traduce a
    401 es `get_current_user` (la capa HTTP). Igual que el 404 del Módulo 03:
    la seguridad no decide status codes, el controller sí.
    """
    raise NotImplementedError("TODO: implementar decode_token")
