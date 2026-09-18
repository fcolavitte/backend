# Material de Aula — Módulo 05: Métodos de Autenticación

> **Clase asincrónica** — Modalidad: aula invertida
> Duración estimada: **2.5 a 3 horas**

## Cómo usar este material

La clase sigue la ruta **LEÉ → MIRÁ → HACÉ**. No saltees pasos: cada uno
construye sobre el anterior, y el código del backend de ejemplo está diseñado
para que lo entiendas **después** de ver los videos, no antes.

---

## 🟢 Paso 1 · Leé (30 min)

- **[README](../README.md)** — qué vas a aprender y cómo está organizado el módulo.
- **[Matriz comparativa](MATRIZ_COMPARATIVA.md)** — los 7 métodos lado a lado.
- **[Casos de uso](CASOS_DE_USO.md)** — cuándo usar cada método (diseño guiado por seguridad).
- **[OWASP Top 10 — mapeo honesto](OWASP.md)** — qué cubre este módulo y qué NO,
  y cómo se hace en un proyecto real. **Obligatorio**: te va a ahorrar el mal
  trago de creer que un módulo de auth es sinónimo de "API segura".

**Objetivo**: al terminar de leer debés poder responder:

1. ¿Cuál es la diferencia entre *método* y *transporte* de autenticación?
2. ¿JWT y sesiones son competidores? ¿Por qué sí o por qué no?
3. ¿Qué significa que un token sea "opaco"? ¿Y "auto-contenido"?
4. ¿Qué guarda el server en sesiones, y qué guarda en JWT?
5. ¿Por qué OAuth2 y SSO son "delegación"?
6. ¿Qué categoría del OWASP cubre este módulo y cuál NO? (autenticación vs autorización)

---

## 🟡 Paso 2 · Mirá (45 min)

### Video A — Hussein Nasser: Cinco autenticaciones de menos a más seguras

| | |
|---|---|
| **Título** | Five Password Authentications From Least to Most Secure |
| **Autor** | Hussein Nasser (487K suscriptores) |
| **Duración** | 17:38 |
| **Link** | https://www.youtube.com/watch?v=_t8EPImx9LI |

**Guía de visionado** → [GUIA_VIDEO_A.md](GUIAS/GUIA_VIDEO_A.md)

**Qué buscar**: el autor ordena 5 esquemas de MENOS a MÁS seguro. Mientras mirás,
anotá en qué posición queda cada uno y **por qué** es más/menos seguro que el anterior.

### Video B — BekBrace: consentimiento OAuth (con nota)

| | |
|---|---|
| **Título** | OAuth 2.0 with FastAPI in 5 minutes |
| **Autor** | BekBrace (105K views) |
| **Duración** | ~5 min |
| **Link** | https://www.youtube.com/watch?v=U8v2RsAcXoM |

**Guía de visionado** → [GUIA_VIDEO_B.md](GUIAS/GUIA_VIDEO_B.md)

> ⚠️ **NOTA IMPORTANTE**: este video usa `passlib` y `python-jose`, librerías que
> hoy están **obsoletas** (passlib no se mantiene desde 2020; python-jose tiene
> CVEs abiertos). Miralo para entender el *flujo OAuth2*, NO copies las librerías.
> En nuestro backend de ejemplo usamos `pwdlib[argon2]` y `pyjwt`, que es lo
> correcto en 2026. La guía del video te marca qué mirar.

**Objetivo**: al terminar de mirar, conectá la teoría con lo que viste:

- En el video de Nasser, ¿cuáles de los 5 esquemas viste en el módulo 04?
- ¿Qué es el "consentimiento" en OAuth que muestra BekBrace?
- ¿Cuándo conviene Basic Auth en producción? (¡casi nunca!, pero ¿por qué?)

---

## 🔵 Paso 3 · Hacé (90 min)

### Parte A · Corré el backend de ejemplo (10 min)

```bash
cd backend
uv sync                # instala dependencias
uv run uvicorn app.main:app --reload --port 8000
```

Verificá que ande: `curl http://127.0.0.1:8000/api/health`
Debería devolver `{"status": "Funciona", ...}`.

> El usuario demo ya está cargado en memoria:
> **email**: `demo@ejemplo.com` · **password**: `demo12345`

### Parte B · Probá los 7 métodos (20 min)

**Opción 1 (recomendada): la battery de tests ya lista**

```bash
bash scripts/verificar_metodos.sh   # → 16 de 16 checkpoints OK
```

**Opción 2: Postman**

Importá `postman/05-metodos-autenticacion.postman_collection.json` y corré el
Collection Runner. Los tokens se guardan solos en variables.

**Opción 3: a mano con curl** — para los curiosos, el script
`verificar_metodos.sh` tiene TODOS los comandos curl comentados. Leelo, es el
mejor material de estudio del módulo.

> **💡 Experimento clave 1 — stateful vs stateless**: abrí
> `http://127.0.0.1:8000/api/health` en el browser mientras hacés login con
> cada método. Mirá qué contador cambia:
> - Session → `sessions_count` sube (la sesión vive en el server)
> - Token opaco → `api_tokens_count` sube (el token vive en el server)
> - JWT → NINGÚN contador cambia (¡es stateless! el server no guarda nada)
>
> Esta es LA diferencia que tenés que entender de este módulo.

> **💡 Experimento clave 2 — rate limiting (Nivel 02)**: probá loguearte con
> un email inventado y contraseña incorrecta 6 veces seguidas. Las primeras 5
> dan `401`, la sexta da `429 Too Many Requests` con header `Retry-After`.
> En `/api/health` vas a ver `login_failures_count` acumular los fallos.
> Eso es lo que frena el brute-force en producción.

### Parte C · Leé el código con lupa (30 min)

Ahora sí, con el backend corriendo y los métodos probados, leé el código.
Orden sugerido:

1. `app/config.py` — SECRET_KEY fail-loud, COOKIE_SECURE, expiraciones
2. `app/security.py` — Argon2id, DUMMY_HASH anti-timing, firma/validación JWT
3. `app/storage.py` — dónde vive el estado (sesiones, tokens opacos)
4. `app/methods/` — empezá por `basic.py` (el más simple), después
   `session_cookie.py`, `token_bearer.py`, y por último `jwt_header.py`.
   Después los dos OAuth (`oauth2.py`) y SSO (`sso_simulado.py`).
5. `app/auth_common.py` — `verify_login`: rate limit + timing attack + 401/429
6. `app/rate_limit.py` — el anti brute-force (Nivel 02)
7. `app/middleware.py` — los security headers (Nivel 02)

**Preguntas para guiar la lectura**:

- ¿Por qué `basic.py` no tiene login ni logout? (pista: no guarda estado)
- ¿Qué pasa con la sesión si reiniciás el server? (pista: memoria)
- ¿Qué diferencia hay entre el JWT del header y el JWT de la cookie?
- ¿Cómo se valida que el token de `/me/sso` vino *realmente* del IdP?
- ¿Por qué `/me/sso` rechaza un JWT local? (pista: iss/aud)
- ¿Por qué el rate limit vive en `verify_login` y no replicado en cada router?
- ¿Por qué en producción el rate limit tiene que vivir en un almacén compartido
  (Redis/gateway) y no en un dict de memoria? (pista: múltiples instancias)

### Parte D · Desafío de seguridad (30 min)

Elegí UNA de estas tres modificaciones y hacela:

1. **Agregá un 8º método**: "App Password" (token largo de un solo uso para
   integraciones, como el de Gmail). Reusá la estructura de `token_bearer.py`.
2. **Endurecé el JWT**: agregá `jti` (identificador único) al token y mantené
   una *deny-list* en memoria para poder revocar un JWT antes de que expire.
3. **Rate limit por IP**: hoy el bloqueo es por email (un atacante que prueba
   contra muchos emails no se frena). Investigá cómo agregar el límite por
   dirección IP — y pensá dónde viviría eso en producción (¿la app? ¿el
   gateway? ¿ambos?).

> Subí tu solución a la rama `solucion` de tu fork con un commit convencional,
> y dejá comentado en el PR qué decidiste y por qué (tradeoffs).

---

## 🧠 Cierre: el mapa mental del módulo

```
AUTENTICACIÓN  (¿quién sos?)
   ├── Quién guarda el estado:
   │    ├── Nadie (stateless)      → JWT, Basic
   │    └── El server              → Sessions, Token opaco
   ├── Cómo viaja la credencial:
   │    ├── Header                 → Basic, Bearer token, Bearer JWT
   │    └── Cookie (httpOnly)      → Session cookie, JWT cookie
   ├── Quién verifica la password:
   │    ├── La propia app          → Basic, Sessions, Tokens, JWT
   │    └── Un tercero (IdP)       → OAuth2, SSO
   ├── Qué se guarda al hashear    → Argon2id (nunca MD5/SHA1/plano)
   └── Cómo se protege el login    → Rate limit (5 fallos → 429) + timing attack

AUTORIZACIÓN  (¿qué podés hacer?)   ← PRÓXIMA CLASE (Nivel 03)
   └── RBAC, scopes, tenancy, deny-by-default (OWASP A01)
```

Si pudiste llenar este mapa con tus palabras — y además sabés decir qué
cubre y qué NO cubre el módulo en el OWASP Top 10 (→ [OWASP.md](OWASP.md)) —
**aprobaste el módulo**.

## Qué sigue

En la próxima clase (presencial) construimos el **Nivel 03 — Autorización**
(RBAC, scopes reales, multi-tenancy) como **proyecto práctico** aplicando
estas decisiones con diseño guiado por seguridad. Traé las dudas que te
hayan quedado del desafío.