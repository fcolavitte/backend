"""
Configuración de la aplicación — variables de entorno y constantes.

Acá viven los valores que NO deben ir hardcodeados en el código, en
especial los secretos. Salen del `.env` (o variables de entorno) y se
leen UNA sola vez al importar.

La regla de oro de seguridad que inaugura este módulo:
    >>> NUNCA un secreto en el código fuente. <<<
    El `SECRET_KEY` firma los tokens. Si viaja en el repo (git), cualquiera
    que lo vea puede fabricar tokens válidos y suplantar a otro usuario.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# ── JWT ──────────────────────────────────────────────────────
# La clave con la que se firman (y verifican) los tokens.
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-cambiar-en-produccion")

# Algoritmo de firma. HS256 = HMAC-SHA256 (clave simétrica).
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Vida útil de un access token, en minutos.
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
