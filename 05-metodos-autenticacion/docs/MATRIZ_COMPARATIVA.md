# Matriz Comparativa — Los 7 métodos de autenticación

> **La pregunta correcta no es "¿cuál método uso?", sino "¿qué combinación de
> dimensiones uso?"**. Los 7 no compiten entre sí: cada uno ocupa un lugar en
> un espacio de diseño. Esta matriz te da ese espacio.

---

## Las dimensiones (leé esto primero)

Antes de comparar métodos, separá los ejes. Son **dimensiones independientes**:

| Eje | Pregunta que responde | Valores típicos |
|-----|----------------------|-----------------|
| **Estado** | ¿Quién guarda "que estás logueado"? | Stateless vs Stateful (server) |
| **Transporte** | ¿Cómo viaja la credencial? | Header vs Cookie vs Body |
| **Delegación** | ¿Quién verifica tu password? | La app vs Un tercero (IdP) |
| **Duración** | ¿Cuánto vale la credencial? | Request, Sesión, Token largo plazo |
| **Revocación** | ¿Podés cortar el acceso ya mismo? | Sí / No (hasta expirar) |

> 💡 **Insight central**: JWT y Session NO son competidores. "JWT" responde al
> eje *estado* (stateless); "cookie" responde al eje *transporte*. Podés tener
> JWT en cookie (ωω método 5) o JWT en header (método 4). Son combinaciones.

---

## La matriz completa

| # | Método | Estado | Transporte | Quién valida | Revocación | Complejidad | Uso típico |
|---|--------|--------|-----------|--------------|-----------|-------------|-----------|
| 1 | **Basic Auth** | Stateless | Header `Authorization: Basic` | La app (cada request) | N/A (no hay token) | ★ | APIs internas, monitoreo, primeros pasos |
| 2 | **Session Based** | Stateful (server) | Cookie `session_id` | La app (lookup en server) | ✅ Inmediata | ★★ | Web apps clásicas (form login) |
| 3 | **Token Auth** (opaco) | Stateful (server) | Header `Bearer <token>` | La app (lookup en server) | ✅ Inmediata | ★★ | APIs móviles, SPAs |
| 4 | **JWT** (header) | Stateless | Header `Bearer <JWT>` | La app (verifica firma) | ❌ Hasta expirar | ★★★ | APIs distribuidas, microservicios |
| 5 | **Cookie Based** (JWT en cookie) | Stateless | Cookie `httpOnly` | La app (verifica firma) | ❌ Hasta expirar | ★★★ | SPAs, web apps con CSRF mitigado |
| 6 | **OAuth2** (password flow) | Stateless (JWT) o stateful | Header / form | IdP + app (token) | Depende | ★★★★ | Delegación de acceso a recursos |
| 7 | **SSO** (OIDC) | Stateless (id_token) | Header / cookie | IdP (externo) | ❌ (sesión en IdP) | ★★★★★ | Login único entre apps, "Login with Google" |

---

## Las 5 preguntas que deciden tu diseño

Cuando estés diseñando autenticación, hacete estas preguntas EN ORDEN:

### 1. ¿Quién es el cliente?

| Cliente | Lo que implica |
|---------|---------------|
| **Browser (SPA/MVC)** | Cookie httpOnly es natural: el JS no guarda secretos |
| **App móvil** | Header Bearer: no hay cookies. Token opaco o JWT |
| **API ↔ API (servidor)** | Header Bearer o mTLS. Token corto, rotación |
| **CLI / scripts** | Basic (con HTTPS) o token de integración revocable |

### 2. ¿Podés permitirte estado en el server?

| Necesidad | Elegí |
|-----------|-------|
| Múltiples instancias / microservicios sin sesión compartida | **JWT** (stateless) |
| Revocación inmediata ante robo (banear al instante) | **Sessions / Token opaco** |
| Sesiones largas con "recordame" sin re-login | Session con sliding expiration |
| Cero infraestructura de sesión, escala horizontal simple | JWT |

### 3. ¿Quién debe saber tu password?

| Escenario | Elegí |
|-----------|-------|
| Solo tu app (credenciales propias) | Basic / Sessions / Tokens / JWT |
| Acceso delegado a un tercero SIN darle tu password | **OAuth2** |
| Un solo login para todas las apps de la empresa | **SSO / OIDC** |

### 4. ¿Cuánta seguridad de transporte necesitás?

| Transporte | Riesgo | Mitigación |
|------------|--------|-----------|
| Header `Authorization` | Robo de token en logs/proxies | HTTPS siempre, no loguear headers |
| Cookie `httpOnly` | CSRF, XSS (cookie robada) | SameSite=Strict, CSRF token, HTTPS |
| Body (form OAuth2) | Menos común en APIs | HTTPS, client_id/secret, PKCE |

### 5. ¿Qué pasa si te roban el token?

| Método | Respuesta ante robo |
|--------|---------------------|
| Sessions / Token opaco | **Revocás en 1 segundo** (borrás del server). Preferible si el riesgo es alto |
| JWT | No podés revocar hasta expirar. Reducí `exp`, rotá a corto plazo |
| Basic | Cambiás la password del usuario (afecta todo) |

---

## Costos / tradeoffs por método

### Basic Auth
- ✅ Mínimo código, funciona en todo
- ✅ Perfecto para monitoreo (`/health`), internal tools, dev local
- ❌ Credenciales viajan en cada request (base64 ≠ cifrado)
- ❌ Sin logout ni revocación granular
- ❌ Nada de "expiró la sesión"
- **Regla de oro**: SIEMPRE con HTTPS; NUNCA en producción expuesto, NUNCA con password de usuario real — usá token de integración.

### Session Based
- ✅ Revocación inmediata, control total del server
- ✅ Simple de entender (un dict / tabla de sesiones)
- ❌ Estado en el server: memoria o caché compartida (Redis)
- ❌ Escalar = escalar el storage de sesiones
- ❌ Vulnerable a session fixation / CSRF si no cuidás las cookies

### Token Auth (opaco)
- ✅ Misma revocación que sessions, pero viaja en header → ideal para móviles
- ✅ No depende de cookies (sin CSRF)
- ❌ Misma necesidad de storage (lookup por token)
- ❌ El header se puede loguear accidentalmente → cachá logs

### JWT
- ✅ Stateless: validás con la firma, sin lookup
- ✅ Escala horizontal sin compartir sesiones
- ✅ Auto-contenido: claims (roles, exp) viajan adentro
- ❌ No revocable hasta expirar (a menos que agregues deny-list)
- ❌ Payload legible (base64) → nunca metas datos sensibles
- ❌ Necesitás librería segura: `algorithms` explícito, validar `iss`/`aud`/`exp`

### Cookie Based (JWT en cookie)
- ✅ Browser-friendly: el JS no ve el token (`httpOnly`)
- ✅ Combine lo stateless con la ergonomía de cookies
- ❌ Misma limitación de revocación del JWT
- ❌ CSRF: la cookie viaja sola → SameSite=Strict/Lax + CSRF token

### OAuth2
- ✅ Delegación: el usuario NO le da la password a tu app
- ✅ Estandarizado (RFC 6749), soportado por todos los gigantes
- ❌ Complejidad de flujos (authorization code, password, client credentials...)
- ❌ Múltiples tokens (access + refresh) que rotar
- ❌ Mala praxis catastrófica: "password flow" con tercera parte

### SSO (OIDC)
- ✅ Un login, muchas apps (CAS, Google, GitHub, Azure AD, Okta...)
- ✅ El IdP maneja password, MFA, recovery — vos no guardás nada
- ✅ JIT provisioning: el usuario se crea al primer login
- ❌ Dependés de un tercero (¿si cae Google?)
- ❌ Validación estricta obligatoria: `iss`, `aud`, `exp`, `nonce`
- ❌ Complejidad de integración (well-known, JWKS, refresh del IdP)

---

## Recomendaciones por stack (resumen ejecutivo)

| Contexto | Combinación recomendada |
|----------|------------------------|
| **SPA + API propia, equipo chico** | JWT en cookie `httpOnly` + CSRF token, o JWT en header si la SPA guarda el token en memoria |
| **App móvil + API propia** | OAuth2 password flow + JWT short-lived + refresh token rotado |
| **Web app clásica (form server-rendered)** | Session cookie + SameSite + CSRF token |
| **Microservicios internos** | JWT firmado por gateway, validado en cada servicio (con `iss`/`aud`) |
| **Empresa grande, varias apps** | SSO/OIDC con IdP central (Keycloak, Okta, Entra ID) + JWT en cada app |
| **Integraciones / bots / scripts** | Token de integración opaco revocable (nunca Basic con password real) |

> **Recordá**: son combinaciones, no elecciones únicas. Tu app puede usar SSO
> para humanos y token opaco para integraciones y Basic (internal) para
> monitoreo. Todo al mismo tiempo. Eso es diseño guiado por seguridad.