# Frontend — Laboratorio de Métodos de Autenticación (Módulo 05)

Paneles interactivos para **probar los 7 métodos** con solo hacer click, ver
las **cookies httpOnly**, el **payload del JWT sin el secreto**, el **429 de
rate limiting** y los **contadores del server en vivo**.

## Cómo arrancar

Requisito: el backend corriendo en `http://127.0.0.1:8000`:

```bash
# (en 05-metodos-autenticacion/backend/)
uv sync
uv run -m app.main
```

Luego, en esta carpeta:

```bash
pnpm install
pnpm dev
```

Abrí `http://localhost:5173`. **No hace falta CORS**: el front va por el
proxy de Vite (`/api` → `127.0.0.1:8000`), mismo-origen. Esa es una lección
en sí misma: las cookies httpOnly juegan porque tanto front como backend
comparten origen (o un API gateway los une en producción).

> **⚠️ Usamos pnpm, NO npm.** El registro/CLI de npm está bloqueado en la
> facultad; pnpm es la herramienta oficial del curso para proyectos Node.
> Nunca generes `package-lock.json` (npm) en este repo. El lockfile de
> pnpm es `pnpm-lock.yaml`.

> Por qué proxy en vez de CORS: el módulo 04 usó el mismo patrón. Con CORS
> cross-origin habría que configurar `credentials`, y las cookies httpOnly
> se volverían más frágiles. El proxy es lo que hace que la demo funcione
> "así de fácil".

## Qué probar (los paneles)

| Panel | Qué hace | Lección clave |
|-------|----------|---------------|
| 1 · Basic | pone `Authorization: Basic base64(email:pass)` en cada request | base64 ≠ cifrado. Solo sobre HTTPS |
| 2 · Session | login → cookie `session_id` httpOnly | el server guarda estado; revocación inmediata |
| 3 · Token opaco | login → token aleatorio en `Bearer` | igual que session pero sin cookie; para APIs |
| 4 · JWT header | login → JWT firmado en `Bearer` | **stateless**: no aparece en el server |
| 5 · JWT cookie | el mismo JWT pero en cookie httpOnly | tradeoff XSS vs CSRF según el vehículo |
| 6 · OAuth2 | `POST /token` con `grant_type=password` | OAuth2 es el PROTOCOLO, JWT el FORMATO |
| 7 · SSO | el IdP (simulado) emite id_token OIDC | validar firma + `iss` + `aud`; JIT provisioning |
| 8 · Rate limit | dispara 6 logins fallidos | el 6to da **429** + `Retry-After` |

El **HealthBar** de arriba es la lección viva: `sesiones` y `tokens opacos`
suben SOLO con Session/Token (estado en server). JWT y SSO no cambian nada
(stateless).

La **consola de requests** de abajo anota cada request con su status.

## Cómo probar en 5 minutos (ruta guiada)

1. **Health**: mirá los contadores en el HealthBar. Anotá el número de
   `sesiones` y `tokens opacos`. (Vas a verlos cambiar en los próximos pasos.)
2. **Tab 1 · Basic**: clickeá *GET /api/me/basic* con el usuario demo
   (`demo@ejemplo.com` / `demo12345`). Después clickeá **"Decodificar"**: base64
   NO es cifrado, la password viaja en texto visible.
3. **Tab 2 · Session**: login → *¿Quién soy?* → logout. Fijate en el HealthBar:
   `sesiones` subió con el login y bajó con el logout (**revocación inmediata**, a
   diferencia del JWT). Abrí DevTools → Application → Cookies: la cookie
   `session_id` está ahí pero el JS no la puede leer (httpOnly).
4. **Tab 3 · Token opaco**: login → *¿Quién soy?* → logout. Acá el contador que
   sube es `tokens opacos`. Mismo concepto que Session, pero sin cookie (para APIs).
5. **Tab 4 · JWT header**: login → clickeá **"Decodificar payload"**: podés leer
   `sub`/`exp` SIN el secreto. Fijate que el HealthBar **NO cambia** — es stateless.
6. **Tab 8 · Rate limit**: clickeá *disparar 6 logins fallidos* → los 5 primeros dan
   401, el 6to **429 con Retry-After**. Mirá `fallos de login` en el HealthBar.
7. **Tab 6 · OAuth2** y **Tab 7 · SSO**: probá el flujo estándar. En SSO usá un
   email inventado (`alumnoX@facultad.edu`): mirá `usuarios` subir (JIT
   provisioning — el usuario se creó al vuelo).

Para verificar de una: `pnpm build` (typecheck + bundle).

## Estructura

```
src/
  api.ts            # UN mecanismo por método, documentado línea por línea
  types.ts          # espejo de app/models.py del backend
  App.tsx           # tabs + HealthBar + consola
  components/
    HealthBar.tsx   # polling de /api/health (contadores en vivo)
    RequestLog.tsx  # consola didáctica
    panels/
      BasicPanel.tsx / SessionPanel.tsx / TokenPanel.tsx /
      JwtHeaderPanel.tsx / JwtCookiePanel.tsx / OAuth2Panel.tsx /
      SsoPanel.tsx / RateLimitPanel.tsx / shared.tsx
```

## Verificación

```bash
pnpm build   # tsc --noEmit && vite build
```

> Nota didáctica: en producción el token de Basic/JWT/OAuth2 viviría en
> memoria + refresh (SPA), NO en `localStorage`, por el riesgo de XSS. Lo
> discutimos en clase.