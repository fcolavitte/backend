---
marp: true
theme: default
paginate: true
backgroundColor: #0f172a
color: #e2e8f0
style: |
  /* ---- Base ---- */
  section {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    padding: 36px 56px;
    background-color: #0f172a;
    color: #e2e8f0;
  }
  h1 { color: #f8fafc; font-size: 1.55em; }
  h2 { color: #f1f5f9; font-size: 1.25em; }
  h3 { color: #94a3b8; font-size: 1em; }
  h4 { color: #93c5fd; }
  strong { color: #f1f5f9; }
  em { color: #cbd5e1; }
  a { color: #93c5fd; }

  /* ---- Slides densas: reducimos todo un escalón ---- */
  section.smaller { font-size: 0.92em; }
  section.smaller h1 { font-size: 1.4em; }
  section.smaller h2 { font-size: 1.15em; }

  /* ---- Código ---- */
  code {
    color: #93c5fd;
    background: #1e293b;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.85em;
  }
  pre {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 0.82em;
    line-height: 1.35;
    color: #e2e8f0;
  }
  pre code {
    background: none;
    padding: 0;
    color: #e2e8f0;
  }

  /* ---- Resaltado sintáctico ---- */
  pre code :is(.hljs-keyword, .hljs-doctag, .hljs-template-tag, .hljs-template-variable, .hljs-variable.language_, .hljs-selector-tag) { color: #f472b6 !important; }
  pre code :is(.hljs-string, .hljs-regexp, .hljs-meta .hljs-string) { color: #86efac !important; }
  pre code :is(.hljs-title, .hljs-title.function_, .hljs-title.class_, .hljs-name, .hljs-quote, .hljs-selector-pseudo) { color: #7dd3fc !important; }
  pre code :is(.hljs-attr, .hljs-attribute, .hljs-literal, .hljs-meta, .hljs-selector-attr, .hljs-selector-class, .hljs-selector-id, .hljs-variable) { color: #93c5fd !important; }
  pre code :is(.hljs-number, .hljs-symbol) { color: #fcd34d !important; }
  pre code :is(.hljs-operator, .hljs-params, .hljs-subst, .hljs-type) { color: #cbd5e1 !important; }
  pre code :is(.hljs-comment, .hljs-code, .hljs-formula) { color: #94a3b8 !important; font-style: italic; }
  pre code :is(.hljs-section, .hljs-bullet) { color: #f0abfc !important; font-weight: 700; }
  pre code .hljs-built_in { color: #fca5a5 !important; }

  /* ---- Tablas ---- */
  table {
    font-size: 0.8em;
    background: #1e293b;
    border-radius: 8px;
    overflow: hidden;
    border-collapse: collapse;
    width: 100%;
  }
  thead { background: #334155; }
  th {
    color: #93c5fd;
    padding: 5px 10px;
    text-align: left;
    border-bottom: 2px solid #3b82f6;
    background: #334155;
  }
  td {
    color: #cbd5e1;
    padding: 5px 10px;
    border-bottom: 1px solid #334155;
    background: #1e293b;
  }
  tr:hover td { background: #263348; }

  /* ---- Blockquote ---- */
  blockquote {
    border-left: 4px solid #3b82f6;
    background: #1e293b;
    padding: 8px 14px;
    border-radius: 0 8px 8px 0;
    margin: 8px 0;
  }
  blockquote p {
    color: #94a3b8;
    font-style: italic;
  }

  /* ---- Listas ---- */
  ul { list-style-type: none; padding-left: 0; }
  ul li::before { content: "▸ "; color: #93c5fd; font-weight: bold; }
  ul li { color: #cbd5e1; line-height: 1.5; }
  ol li { color: #cbd5e1; line-height: 1.5; }

  /* ---- Lead slides ---- */
  section.lead h1 { font-size: 2.2em; }
  section.lead p { color: #94a3b8; }

  /* ---- Checkpoint ---- */
  section.checkpoint {
    background-color: #052e16;
  }
  section.checkpoint h1 {
    color: #34d399;
    font-size: 1.7em;
  }
  section.checkpoint p, section.checkpoint li {
    color: #a7f3d0;
  }

  /* ---- Fase ---- */
  section.fase {
    background-color: #1e1b4b;
  }
  section.fase h1 { color: #c4b5fd; font-size: 1.7em; }
  section.fase h2 { color: #ddd6fe; }

  /* ---- Desbloqueo (errores comunes) ---- */
  section.desbloqueo {
    background-color: #2a1a1a;
  }
  section.desbloqueo h1 { color: #fca5a5; font-size: 1.6em; }

  /* ---- Bibliografía ---- */
  section.biblio {
    background-color: #0b1220;
  }
  section.biblio h1 { color: #93c5fd; font-size: 1.6em; }
  section.biblio h2 { color: #c4b5fd; font-size: 1.05em; }
  section.biblio li { font-size: 0.82em; line-height: 1.45; }

  /* ---- Footer ---- */
  footer { color: #64748b; font-size: 0.6em; }
---

<!-- _class: lead -->
<!-- note: |
  Bienvenida a la clase 04. Hoy NO agregamos una API: le ponemos IDENTIDAD
  a cada request. En el 03 reorganizaron en capas; hoy cierran la puerta.
  Recordar: la lectura previa ya la hicieron en casa. La apertura (quiz +
  repaso) es corta, y después arrancan los 60 min de ACTIVIDAD.
  Timing: apertura 0-1 min
-->

# Autenticación y Seguridad

### Clase 04 — Desarrollo de Software 2026

Hoy no escriben una API nueva. **Le ponen una identidad a cada request, y una puerta a la API.**

---

<!-- note: |
  Objetivos medibles. Decirlos en voz alta y dejar la slide visible.
  Son la promesa: al final, cada alumno tilda los 4.
  Timing: apertura 1-2 min
-->

## Objetivos de la clase

Al terminar, vas a poder:

1. **Registrar y loguear** usuarios, guardando la contraseña como **hash Argon2** (jamás texto plano).

2. **Emitir y validar un JWT**, y proteger un endpoint con `get_current_user`.

3. **Distinguir** sesión server-side de JWT, y explicar el tradeoff.

4. **Nombrar** las amenazas OWASP que tocan la autenticación y cómo evitarlas.

> Cuatro objetivos, 60 minutos de actividad, y los construís vos en grupo.

---

<!-- note: |
  Quiz de 3 preguntas para activar.
  RESPUESTAS:
  1. Autenticación responde "quién sos"; autorización, "qué podés hacer".
  2. Porque las bases se filtran y la gente reutiliza contraseñas. Guardamos
     un hash (Argon2), irreversible y lento.
  3. Se FIRMA, no se encripta: el payload es legible (base64), la firma
     garantiza integridad. Nada de secretos en el payload.
  Timing: apertura 2-5 min
-->

## Quiz de apertura (aula invertida)

1. ¿Cuál es la diferencia entre **autenticación** y **autorización**?

2. ¿Por qué NUNCA guardamos la contraseña en texto plano? ¿Qué guardamos?

3. ¿El JWT se **encripta** o se **firma**? ¿Qué implica para su payload?

> El quiz sale del `MATERIAL_PREVIO.md` (con su bibliografía). Si no lo leíste,
> hoy vas a ver pasar la clase por la ventana.

---

<!-- note: |
  Las 3 preguntas que se confunden. Esta es la lección de fondo.
  Enfatizar: son preguntas distintas; no mezclar.
  Timing: apertura 5-8 min
-->

## Las tres preguntas que la gente confunde

| Pregunta | Nombre | Ejemplo |
|----------|--------|---------|
| ¿Quién sos? | **Autenticación** | email + contraseña |
| ¿Qué podés hacer? | **Autorización** | "solo el dueño borra SU tarea" |
| ¿Cómo lo demuestro en cada request? | **Sesión / token** | cookie o JWT |

> Hoy nos enfocamos en la 1ª y la 3ª. La autorización (RBAC) es el próximo
> módulo. Pero sin "quién sos", no podés decidir "qué podés hacer".

---

<!-- note: |
  El problema del texto plano. Mostrar la tabla users con password.
  Preguntar: "¿qué pasa si se filtra esta base?".
  Timing: apertura 8-11 min
-->

## El problema: contraseñas en texto plano

```sql
users
├── id
├── email
└── password   ← "supersecreto123"   -- ERROR GRAVÍSIMO
```

¿Qué pasa si la base se filtra? **Todas las contraseñas, expuestas.**
Y como la gente reutiliza contraseñas, no entran solo a TU app:
entran a su banco, su mail, su Netflix.

> La solución: guardar un **hash** — una función **irreversible**. Para
> loguear comparamos `hash(ingresada) == hash(guardado)`. Nunca recuperamos
> la original.

---

<!-- note: |
  Hash con sal. Y no cualquier hash: MD5/SHA1 son rápidos → brute-force con GPU.
  Necesitamos lento: Argon2. "Lento" es feature.
  Timing: apertura 11-14 min
-->

## La solución: hash lento (Argon2)

```python
hash("supersecreto123")
# → "$argon2id$v=19$m=65536,t=3,p=4$..."  (irreversible)

verify_password("supersecreto123", hash)   # → True
verify_password("incorrecta", hash)        # → False
```

| Algoritmo | Velocidad | ¿Sirve para contraseñas? |
|-----------|-----------|--------------------------|
| MD5 / SHA1 | rápida | ❌ (brute-force con GPU) |
| **Argon2** | **lenta, costosa** | ✅ (diseñado para contraseñas) |

> **"Lento" es una FEATURE.** Hace inviable el brute-force. Argon2 ganó el
> Password Hashing Competition 2015.

---

<!-- note: |
  Sesión vs JWT. LA lección conceptual de hoy. HTTP es stateless.
  Dos estrategias para mantener sesión: server-side (estado) o token (stateless).
  Timing: apertura 14-18 min
-->

## Sesión vs JWT: el tradeoff

HTTP es **stateless**. ¿Cómo "recuerdo" quién sos entre requests?

| | Sesión server-side | JWT (token) |
|---|---|---|
| Estado | En el server (DB/Redis) | En el token (cliente) |
| Revocación | **Fácil** (borrás la sesión) | Difícil (esperar `exp` o blacklist) |
| Escala horizontal | Necesita almacén compartido | **Fácil** (solo la clave) |

> **Ninguno es mejor en abstracto.** Es una decisión de arquitectura:
> ¿priorizás echar a alguien al instante, o escalar sin estado?

---

<!-- note: |
  SSO vs JWT: la trampa conceptual. NO se comparan. SSO = flujo; JWT = formato.
  Un SSO (OIDC) emite un JWT. SAML usa XML.
  Timing: apertura 18-21 min
-->

## SSO vs JWT: el error conceptual más común

- **SSO** → un **flujo** de autenticación delegada. Te logueás UNA vez y accedés
  a muchos servicios. Protocolos: **SAML**, **OIDC** (sobre OAuth 2.0).

- **JWT** → un **formato** de token. Es CÓMO se codifica y firma la info.

> Son **ortogonales**, no competidores. Un SSO casi siempre **emite un JWT**
> (el "ID token" de OIDC es un JWT). Comparar SSO con JWT es como comparar
> **el sistema de riego** con **el tipo de caño**.

---

<!-- note: |
  El JWT por dentro. 3 partes separadas por puntos. Payload legible.
  Enfatizar: se firma, no se encripta. No meter secretos.
  Timing: apertura 21-23 min
-->

## El JWT por dentro

```
header.payload.signature
```

- **header** — algoritmo (`{"alg": "HS256", "typ": "JWT"}`)
- **payload** — claims: `sub` (quién), `exp` (expiración)…
- **signature** — la firma que garantiza que **nadie lo alteró**

```python
payload = {"sub": "42", "exp": 1735689600}
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
jwt.decode(token, SECRET_KEY, algorithms=["HS256"])   # ← algorithms SIEMPRE explícito
```

> ⚠️ El payload está **codificado (base64), NO encriptado**. Cualquiera puede
> leerlo. **Jamás secretos adentro.** Y `algorithms` explícito evita el
> "algorithm confusion attack".

---

<!-- note: |
  OWASP Top 10 (2021). Las categorías que tocan auth: A01, A02, A03, A07.
  Y dos amenazas del login: user enumeration y timing attack.
  Timing: apertura 23-25 min (fin de la apertura)
-->

## Seguridad OWASP: tu checklist

| OWASP 2021 | Nombre | Nuestro contexto |
|---|---|---|
| **A01** | Broken Access Control | endpoints sin proteger → `get_current_user` |
| **A02** | Cryptographic Failures | texto plano / hash débil → Argon2 |
| **A03** | Injection | SQLi → el ORM parametriza |
| **A07** | Identification & Authentication Failures | tokens débiles, sin `exp` → JWT firmado + expiración |

Y dos amenazas del login que vamos a discutir:

- **User enumeration** → un mensaje de error genérico ("credenciales incorrectas").
- **Timing attack** → verificar siempre contra un hash, incluso si el user no existe.

---

<!-- note: |
  El plan de la actividad. 60 min de sprint.
  Recordar roles (piloto/navegante/investigador) rotando.
  Timing: apertura 25-26 min (fin de la apertura)
-->

## El plan — 60 min de actividad

> La lectura previa ya la hiciste en casa. Acá van **60 minutos de construcción**.

| Min | Fase | Qué construyen |
|-----|------|----------------|
| 0-5 | **Setup** | Levantar el scaffold |
| 5-20 | **Security** | hash + verify + JWT (4 funciones) |
| 20-30 | **Repository** | get_by_email, get_by_id, create |
| 30-40 | **Service** | register + authenticate (el `None`) |
| 40-55 | **Controller + get_current_user** | endpoints + la ruta protegida |
| 55-60 | **Frontend** | conectar y cerrar el ciclo |

> **Regla del taller**: el docente NO da respuestas. Hace preguntas.
> *"¿Eso es HTTP, negocio, datos, o criptografía?"* destraba el 90%.

---

<!-- _class: fase -->
<!-- note: |
  Fase 1: security.py. Las 4 primitivas. El corazón del módulo.
  Timing: actividad 5-20 min
-->

## Fase 1 — Security: hash + JWT (15 min)

Completá `app/security.py`:

```python
password_hash = PasswordHash.recommended()   # Argon2id

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return password_hash.verify(plain, hashed)

def create_access_token(subject: str) -> str:
    payload = {"sub": subject}
    payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
```

> `timezone.utc` sí o sí. Y `algorithms=[...]` explícito. `decode_token` NO
> captura la excepción: la deja propagar (el 401 lo hace `get_current_user`).

---

<!-- _class: fase -->
<!-- note: |
  Fase 2: repository. 3 métodos. Igual que el 03.
  Pregunta: ¿el repository hashea? No: hashear es seguridad/negocio.
  Timing: actividad 20-30 min
-->

## Fase 2 — Repository (10 min)

Completá `app/repositories/user_repository.py`:

```python
def get_by_email(self, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return self.session.exec(statement).first()

def get_by_id(self, user_id: int) -> User | None:
    return self.session.get(User, user_id)

def create(self, email: str, hashed_password: str) -> User:
    user = User(email=email, hashed_password=hashed_password)
    self.session.add(user)
    self.session.commit()
    self.session.refresh(user)
    return user
```

> El repository recibe `hashed_password` YA hasheado. Hashear no es "datos":
> es seguridad/negocio, y pasa por el service antes.

---

<!-- _class: fase -->
<!-- note: |
  Fase 3: service. La lógica. El momento clave: None vs 401.
  Timing: actividad 30-40 min
-->

## Fase 3 — Service (10 min)

Completá `app/services/auth_service.py`:

```python
def register_user(self, body: UserCreate) -> User | None:
    email = body.email.lower().strip()
    if self.repository.get_by_email(email) is not None:
        return None                      # email ya existe
    hashed = hash_password(body.password)
    return self.repository.create(email, hashed)

def authenticate_user(self, email: str, password: str) -> User | None:
    email = email.lower().strip()
    user = self.repository.get_by_email(email)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
```

> **La pregunta del millón**: ¿el service devuelve `None` o lanza un `401`?
> `None`. El 401 es HTTP y el service no sabe de HTTP. Igual que el 404 del 03.

---

<!-- _class: fase -->
<!-- note: |
  Fase 4: controller + get_current_user. Traducir None -> 401/409.
  Enfatizar mensaje genérico en login.
  Timing: actividad 40-55 min
-->

## Fase 4 — Controller + get_current_user (15 min)

```python
@router.post("/register", response_model=UserRead, status_code=201)
def register(body: UserCreate, service = Depends(get_auth_service)):
    user = service.register_user(body)
    if user is None:
        raise HTTPException(status_code=409, detail="El email ya está registrado")
    return user

@router.post("/login", response_model=Token)
def login(body: UserLogin, service = Depends(get_auth_service)):
    user = service.authenticate_user(body.email, body.password)
    if user is None:
        raise HTTPException(status_code=401,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"})
    return Token(access_token=create_access_token(str(user.id)), token_type="bearer")
```

> **Mensaje genérico** para ambos fallos: evita user enumeration.
> `UserRead` no expone `hashed_password`: el hash no sale por la API.

---

<!-- _class: fase -->
<!-- note: |
  get_current_user: la dependencia que protege. La joya del módulo.
  Timing: actividad 40-55 min (junto con la anterior)
-->

## get_current_user — la ruta protegida

```python
def get_current_user(
    token: str = Depends(oauth2_scheme),
    repository: UserRepository = Depends(get_user_repository),
) -> User:
    credentials_exception = HTTPException(
        status_code=401, detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id = int(payload["sub"])
    except InvalidTokenError:
        raise credentials_exception
    user = repository.get_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user
```

> Cualquier endpoint con `Depends(get_current_user)` queda bloqueado. Si el
> token falta, está mal firmado, expiró o el user no existe → `401`.

---

<!-- _class: checkpoint -->
<!-- note: |
  Checkpoint 2: flujo completo. register -> login -> /me.
  Timing: actividad ~55 min
-->

## ✅ Checkpoint — Flujo completo

```bash
# registrarse
curl -X POST :8000/api/auth/register -H "Content-Type: application/json" \
  -d '{"email":"juan@ejemplo.com","password":"supersecreto123"}'
# → 201, SIN hashed_password

# loguearse
curl -X POST :8000/api/auth/login -H "Content-Type: application/json" \
  -d '{"email":"juan@ejemplo.com","password":"supersecreto123"}'
# → {"access_token":"eyJ...","token_type":"bearer"}

# acceder con token
curl :8000/api/users/me -H "Authorization: Bearer <TOKEN>"   # → tu usuario
curl :8000/api/users/me                                      # → 401
```

- [ ] Register devuelve `201` sin hash
- [ ] Login devuelve token; `/me` con token responde, sin token `401`
- [ ] Login con contraseña mal → `401` con **mensaje genérico**

---

<!-- _class: fase -->
<!-- note: |
  Fase 5: frontend. Ya viene completo. Levantar y verificar el ciclo.
  Mostrar api.ts (header Authorization) y types.ts (User sin hash).
  Timing: actividad 55-60 min
-->

## Fase 5 — Frontend: cerrar el ciclo (5 min)

Ya viene **completo**. Levantalo y verificá:

```bash
cd ../frontend
pnpm install
pnpm dev          # :5173
```

Registrate → se loguea solo → ves tu perfil → cerrá sesión → entrá de nuevo.

```typescript
// src/api.ts — el token viaja en el header Authorization
export function getMe(token: string): Promise<User> {
  return request<User>(`${BASE_URL}/users/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}
```

> El `interface User` de `types.ts` refleja el `UserRead` del backend: **sin**
> `hashed_password`. Y el token se manda en el header, no en la URL.

---

<!-- _class: desbloqueo -->
<!-- note: |
  Slide de desbloqueo. Cheat sheet para responder con pistas.
  Timing: cuando haga falta.
-->

## 🔧 Errores comunes (desbloqueo rápido)

| Síntoma | Pista |
|---------|-------|
| `ImportError: jwt` / `pwdlib` | `uv sync` |
| `422` al registrar | email mal formado (`EmailStr` valida) |
| `409` al registrar dos veces | email ya existe (unique) — esperado |
| `401` en `/me` con token | ¿header exacto `Bearer <token>`? ¿expirado? |
| Firma inválida | modificaste un char del token — la firma lo detecta |
| `datetime.now()` sin timezone | usá `timezone.utc` |
| `jwt.decode` sin `algorithms` | siempre explícito (algorithm confusion) |
| ¿dónde va el hash? | *"¿hashear es HTTP, datos, negocio o criptografía?"* |
| ¿el service lanza 401? | *"¿el service sabe qué es un status code?"* |

> **Regla**: no des la respuesta. Hacé la pregunta que la destraba.

---

<!-- _class: lead -->
<!-- note: |
  Reflexión final. Preguntas al aire (5 min). Cerrar con la frase.
  Timing: actividad 55-60 min
-->

## Hoy no agregaron un login

### Le pusieron una **identidad a cada request**, y una **puerta a la API**

> *"La Universidad te da el mapa. El recorrido lo hacés vos."*

---

<!-- _class: biblio -->
<!-- note: |
  Slide de PUESTA EN COMÚN + bibliografía. Es la que queda proyectada
  mientras los grupos comparten sus descubrimientos. Los alumnos pueden
  escanearla/abrirla para seguir profundizando en casa.
  No leerla entera: es material de referencia.
-->

## 📚 Para seguir aprendiendo (bibliografía)

### Autenticación y sesiones

- **[jwt.io — Introduction](https://jwt.io/introduction)** · debugger interactivo de JWT
- **[RFC 7519 — JSON Web Token](https://datatracker.ietf.org/doc/html/rfc7519)** · la spec
- **[MDN — HTTP Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies)** · el vehículo de la sesión
- **[Auth0 — Token Based Authentication](https://auth0.com/docs/secure/tokens)** · fundamentos de tokens
- 🎬 **Hussein Nasser** — [Session vs JWT](https://www.youtube.com/@hnasr)

### SSO, OAuth 2.0 y OIDC

- **[OAuth 2.0 Simplified](https://aaronparecki.com/oauth-2-simplified/)** · libro online gratis (Aaron Parecki)
- **[Auth0 — What is SSO?](https://auth0.com/docs/authenticate/single-sign-on)** · y [SAML vs OIDC](https://auth0.com/docs/authenticate/protocols/saml/saml-sso-concepts/saml-vs-oidc)
- **[OpenID Connect — How it works](https://openid.net/developers/how-connect-works/)** · el protocolo OIDC
- 🎬 **OktaDev** — [OAuth & OIDC in Plain English](https://www.youtube.com/@OktaDev)

### Seguridad OWASP

- **[OWASP Top 10 (2021)](https://owasp.org/Top10/)** · leé A01, A02, A03 y A07
- **[OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/index.html)** · Authentication, Password Storage, JWT, Session Management
- **[OWASP — Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)** · cómo guardar contraseñas (Argon2, sal, pepper)
- **[Argon2 — Password Hashing Competition](https://www.password-hashing.net/)** · por qué ganó
- 🎬 **LiveOverflow** — [JWT attacks](https://www.youtube.com/@LiveOverflow)

### FastAPI (implementación)

- **[FastAPI — OAuth2 + JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)** · el tutorial oficial con `pwdlib` + Argon2
- **[PyJWT — docs](https://pyjwt.readthedocs.io/)** · la librería de JWT
- **[pwdlib — docs](https://github.com/frankie567/pwdlib)** · hashing con Argon2/bcrypt

> **La seguridad no se aprende leyendo: se aprende rompiendo.**
> Leé, probá, y volvé a romper tu propio código.
