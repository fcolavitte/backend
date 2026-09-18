"""
Security headers — hardening de capa HTTP (producción).

Cada header responde a un ataque:

  - Strict-Transport-Security (HSTS): fuerza HTTPS en el navegador; mata el
    downgrade attack (que un MITM baje la conexión de https a http).
    ⚠️ Solo tiene sentido cuando el server ya sirve HTTPS. Lo enviamos
    siempre para que quede listo cuando haya TLS.
  - X-Content-Type-Options: nosniff → el navegador NO adivina el tipo MIME
    (evita que un archivo subido se ejecute como HTML/JS — el "sniffing").
  - X-Frame-Options: DENY → la app no se puede incrustar en un <iframe>
    (mata el clickjacking).
  - Referrer-Policy: no-referrer → el browser no filtra la URL de origen
    (evita que en la cabecera Referer se escape info sensible del path).
  - Cache-Control: no-store en /api/me/* → la respuesta con datos del
    usuario no queda cacheada ni en el browser ni en proxies
    (un "atrás" del browser no debe mostrar el perfil de otra sesión).

Esto es un middleware ASGI puro: corre en el punto más externo, antes de
cualquier router, y agrega los headers a TODAS las respuestas.

En producción se puede (y se debe) hacer también en el reverse proxy
(nginx/traefik) o en un WAF — dos capas de defensa.
"""

from starlette.datastructures import MutableHeaders


class SecurityHeadersMiddleware:
    """Agrega los headers de seguridad básicos a cada respuesta HTTP."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            # No es HTTP (websocket, etc.): pasamos sin tocar.
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
                headers["X-Content-Type-Options"] = "nosniff"
                headers["X-Frame-Options"] = "DENY"
                headers["Referrer-Policy"] = "no-referrer"
                if scope["path"].startswith("/api/me/"):
                    headers["Cache-Control"] = "no-store"
            await send(message)

        await self.app(scope, receive, send_wrapper)