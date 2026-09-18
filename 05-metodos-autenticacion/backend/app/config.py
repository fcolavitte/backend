"""
Configuración del módulo 05.

Todo tiene DEFAULTS de desarrollo para que el ejemplo corra sin .env.
En producción, cada valor sale de variables de entorno o un secret manager.

REGLAS:
  - SECRET_KEY: en producción es OBLIGATORIA vía entorno. Si falta, la app
    NO arranca (fail-loud): un default silencioso en prod sería una bomba.
  - COOKIE_SECURE: en producción (HTTPS) debe ser "true". En dev local (http)
    queda "false" para que las cookies funcionen.
"""

import os

# ──────────────────────────────────────────────────────────────────────────
# Entorno
# ──────────────────────────────────────────────────────────────────────────
# "development" (default) | "production" | "testing"
ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").lower()
IS_PRODUCTION: bool = ENVIRONMENT == "production"

# ──────────────────────────────────────────────────────────────────────────
# JWT
# ──────────────────────────────────────────────────────────────────────────
_SECRET_KEY = os.getenv("SECRET_KEY")
if not _SECRET_KEY:
    if IS_PRODUCTION:
        # Fail-loud: sin SECRET_KEY no hay firma segura → no se puede arrancar.
        raise RuntimeError(
            "SECRET_KEY es OBLIGATORIA en producción. Generala con: "
            "openssl rand -hex 32   y pasala por variable de entorno o "
            "secret manager. NUNCA hardcodeada en el código."
        )
    # Solo para desarrollo local. Generá la tuya con `openssl rand -hex 32`.
    _SECRET_KEY = "dev-only-9f8e7d6c5b4a3210-no-usar-en-produccion-cambiar-ya"
SECRET_KEY: str = _SECRET_KEY

ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# ──────────────────────────────────────────────────────────────────────────
# Cookies (Session Based y JWT en cookie)
# ──────────────────────────────────────────────────────────────────────────
# secure=True → la cookie solo viaja por HTTPS. En producción: COOKIE_SECURE=true.
# En dev local con http://127.0.0.1 la cookie con secure=True NO se guarda.
COOKIE_SECURE: bool = os.getenv("COOKIE_SECURE", "false").lower() == "true"

# ──────────────────────────────────────────────────────────────────────────
# Sesiones server-side (cookie session) y tokens opacos
# ──────────────────────────────────────────────────────────────────────────
SESSION_EXPIRE_MINUTES: int = int(os.getenv("SESSION_EXPIRE_MINUTES", str(60 * 24)))  # 1 día
TOKEN_EXPIRE_MINUTES: int = int(os.getenv("TOKEN_EXPIRE_MINUTES", "120"))

# ──────────────────────────────────────────────────────────────────────────
# Rate limiting del login (anti brute-force / credential stuffing)
# ──────────────────────────────────────────────────────────────────────────
LOGIN_MAX_FAILED_ATTEMPTS: int = int(os.getenv("LOGIN_MAX_FAILED_ATTEMPTS", "5"))
LOGIN_RATE_WINDOW_MINUTES: int = int(os.getenv("LOGIN_RATE_WINDOW_MINUTES", "15"))

# ──────────────────────────────────────────────────────────────────────────
# SSO simulado (flujo OIDC)
# ──────────────────────────────────────────────────────────────────────────
SSO_CLIENT_ID: str = os.getenv("SSO_CLIENT_ID", "mi-app-cliente")
SSO_ISSUER: str = os.getenv("SSO_ISSUER", "https://idp.ejemplo.com")

# Usuario demo con el que arranca el storage (para probar todo sin registrarse)
DEMO_EMAIL: str = os.getenv("DEMO_EMAIL", "demo@ejemplo.com")
DEMO_PASSWORD: str = os.getenv("DEMO_PASSWORD", "demo12345")