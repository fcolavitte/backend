# Guía del Alumno — Autenticación y Seguridad (taller por grupos)

> **Módulo 04 — Desarrollo de Software 2026**
> **Modalidad**: taller por grupos con descubrimiento. **60 minutos.**
> Ya leíste el `MATERIAL_PREVIO.md`. Ahora a construir.

---

## Cómo funciona este taller

1. Tu **fork** ya trae el **esqueleto** del backend (todo lo demás viene hecho).
2. Tu grupo completa **seis archivos** siguiendo las consignas.
3. Después de cada fase, **verificás** que funcione antes de avanzar.
4. Si te trabás: preguntale al docente. Pero él no te da la respuesta — te
   hace una pregunta que te ayuda a encontrarla vos.

**Roles dentro del grupo** (rotan en cada fase): **Piloto** (escribe),
**Navegante** (lee consignas y anticipa errores), **Investigador** (busca en
la doc o en el código del Módulo 03).

---

## Qué ya viene hecho en tu fork (NO se modifica)

```
04-autenticacion-seguridad/backend/
├── app/
│   ├── main.py                    # entrypoint (dado)
│   ├── config.py                  # SECRET_KEY, ALGORITHM, expiración (dado)
│   ├── database.py                # engine + session (dado)
│   ├── models/user.py             # modelo SQLModel + schemas (dado)
│   ├── security.py                # ⬅️ VOS LO COMPLETÁS (hash + JWT)
│   ├── dependencies.py            # ⬅️ VOS COMPLETÁS get_current_user
│   ├── repositories/
│   │   └── user_repository.py     # ⬅️ VOS LO COMPLETÁS
│   ├── services/
│   │   └── auth_service.py        # ⬅️ VOS LO COMPLETÁS
│   └── controllers/
│       ├── health_controller.py   # EJEMPLO de controller (dado)
│       ├── auth_controller.py     # ⬅️ VOS LO COMPLETÁS
│       └── users_controller.py    # ⬅️ VOS LO COMPLETÁS
└── ...
```

El frontend (`../frontend/`) ya viene **completo y funcionando**. No se
construye en el taller: se conecta al final para cerrar el ciclo.

---

## Fase 0 — Setup (5 min)

```bash
cd 04-autenticacion-seguridad/backend
cp .env.example .env      # completá DATABASE_URL + SECRET_KEY
uv sync                   # instala pwdlib[argon2], pyjwt, email-validator
uv run -m app.main        # levanta el server en :8000
```

Verificá:

```bash
curl http://localhost:8000/api/health
# → {"status":"Funciona","service":"04-...","db":"conectada","users_count":0}
```

> El health **ya funciona** porque usa el `health_controller` (dado) y el
> `count()` del repository (ejemplo resuelto). Fijate: el `count()` ya viene
> escrito. Los otros métodos del repository son los tuyos.

---

## Fase 1 — Security: hash + JWT (15 min)

**Objetivo**: completar `app/security.py`. Es el corazón criptográfico del
módulo. Cuatro funciones:

```python
def hash_password(password: str) -> str: ...
def verify_password(plain_password: str, hashed_password: str) -> bool: ...
def create_access_token(subject: str, expires_minutes: int | None = None) -> str: ...
def decode_token(token: str) -> dict: ...
```

### Consignas (descubrimiento)

1. **`hash_password`**: usás `password_hash.hash(password)`. Ese objeto
   `password_hash` ya viene creado arriba con `PasswordHash.recommended()`.
   ¿Qué algoritmo creés que usa "recommended"? (spoiler: Argon2id).

2. **`verify_password`**: `password_hash.verify(plain, hashed)`. Devuelve
   `True`/`False`. **Nunca** lanza excepción si no coincide.

3. **`create_access_token`**: la parte más delicada.
   - Armás un dict `payload = {"sub": subject}`.
   - Calculás la expiración:
     ```python
     expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES)
     ```
   - Agregás `payload["exp"] = expire`.
   - Devolvés `jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)`.

   > ⚠️ **`timezone.utc`, no `now()` a secas.** Si usás `datetime.now()` sin
   > timezone, la expiración es frágil y rompe en distintos husos. Es un
   > error clásico.

4. **`decode_token`**: `jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])`.
   Devuelve el payload (un dict). **No captures la excepción**: dejala
   propagar. Si el token expiró o la firma es inválida, `jwt.decode` lanza
   `jwt.InvalidTokenError` (o sus subclases). La traducción a 401 la hace
   `get_current_user`, no acá.

   > 🧠 **Pregunta de la fase**: ¿por qué `decode_token` NO devuelve un 401?
   > (misma lógica que el 404 del Módulo 03: la seguridad no sabe de HTTP).

**Verificá** (podés probar las funciones con un REPL):

```bash
uv run python -c "from app.security import hash_password, verify_password; h = hash_password('hola12345'); print(h[:20]); print(verify_password('hola12345', h), verify_password('mal', h))"
# → $argon2id$v=19$...  y  True False
```

---

## Fase 2 — Repository: la capa de datos (10 min)

**Objetivo**: completar `app/repositories/user_repository.py`.

```python
def get_by_email(self, email: str) -> User | None: ...
def get_by_id(self, user_id: int) -> User | None: ...
def create(self, email: str, hashed_password: str) -> User: ...
```

### Consignas

1. **`get_by_email`**: `select(User).where(User.email == email)`, ejecutás con
   `self.session.exec(...)`, y usás `.first()` (querés UNO o `None`, no una lista).
2. **`get_by_id`**: atajo del ORM → `self.session.get(User, user_id)`.
3. **`create`**: `User(email=email, hashed_password=hashed_password)`, luego
   `add()`, `commit()`, y `refresh()` para traer `id` + `created_at`.

> 🔎 **Pregunta de la fase**: el repository recibe `hashed_password` (ya
> hasheado). ¿Por qué el repository NO hashea? (porque hashear no es "datos",
> es "seguridad/negocio" — pasa por el service antes de llegar acá).

---

## Fase 3 — Service: la capa de negocio (10 min)

**Objetivo**: completar `app/services/auth_service.py`.

```python
def register_user(self, body: UserCreate) -> User | None: ...
def authenticate_user(self, email: str, password: str) -> User | None: ...
```

### Consignas

1. **`register_user`**:
   1. Normalizá el email: `email = body.email.lower().strip()`.
   2. Si `self.repository.get_by_email(email)` devuelve algo → devolvé `None`
      (el email ya existe).
   3. `hashed = hash_password(body.password)`.
   4. `return self.repository.create(email, hashed)`.

2. **`authenticate_user`**:
   1. Normalizá el email igual.
   2. `user = self.repository.get_by_email(email)`.
   3. Si `user is None` → `return None`.
   4. Si `not verify_password(password, user.hashed_password)` → `return None`.
   5. `return user`.

> 🧠 **LA PREGUNTA DEL MILLÓN**: cuando el login falla, ¿el service devuelve
> `None` o lanza un `401`? → `None`. El `401` es HTTP y el service no sabe de
> HTTP. El controller lo traduce. Es exactamente el `404` del Módulo 03.

> 🎯 **Bonus (timing attack)**: ¿notás que si el user no existe, el paso de
> `verify_password` (que es lento, Argon2) no corre? Eso hace que "email
> inexistente" sea más rápido que "contraseña mal". Un atacante lo puede medir.
> ¿Cómo lo arreglarías? (discutílo con el grupo; la respuesta está en la
> puesta en común).

---

## Fase 4 — Controller + get_current_user: la capa HTTP (15 min)

**Objetivo**: completar `app/controllers/auth_controller.py`,
`app/controllers/users_controller.py` y `app/dependencies.py`.

### 4.1 `auth_controller.py`

**`register`**:
```python
user = service.register_user(body)
if user is None:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El email ya está registrado")
return user
```
(El `response_model=UserRead` se encarga de NO exponer el hash.)

**`login`**:
```python
user = service.authenticate_user(body.email, body.password)
if user is None:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Email o contraseña incorrectos",
        headers={"WWW-Authenticate": "Bearer"},
    )
access_token = create_access_token(str(user.id))
return Token(access_token=access_token, token_type="bearer")
```

> 🧠 **Fijate el mensaje de error del login**: "Email o contraseña
> incorrectos" para AMBOS casos (email inexistente Y contraseña mal). Si
> dijeras "email no existe" vs "contraseña mal", estarías permitiendo user
> enumeration. Un solo mensaje genérico lo evita.

### 4.2 `users_controller.py`

**`read_me`**:
```python
@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user
```

> 🧠 **La lección se cierra**: este endpoint NO recibe un id por URL. El
> "quién" viene del TOKEN, resuelto por `get_current_user`. Acá no hay SQL,
> no hay hash, no hay verificación: solo devolver al usuario que la
> dependencia ya autenticó.

### 4.3 `dependencies.py` — `get_current_user` (la joya)

```python
def get_current_user(
    token: str = Depends(oauth2_scheme),
    repository: UserRepository = Depends(get_user_repository),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
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

> 🧠 **Esto es lo que protege las rutas.** Cualquier endpoint que pida
> `Depends(get_current_user)` queda bloqueado: si el token no está, está
> mal firmado, expiró, o el usuario no existe → `401` y el endpoint ni corre.

---

## Fase 5 — Frontend: cerrar el ciclo (5 min)

El frontend ya viene **completo**. Tu trabajo es conectarlo y verificar el
ciclo de autenticación de punta a punta.

```bash
cd ../frontend
pnpm install
pnpm dev        # levanta en :5173
```

Abrí `http://localhost:5173` y hacé el ciclo completo desde la UI:

1. **Registrate** (pestaña "Registrarse") con un email y contraseña.
2. Se **loguea automáticamente** y te muestra tu perfil.
3. **Cerrá sesión** y volvé a entrar con "Iniciar sesión".

**Descubrí cómo viaja el token**: abrí `src/api.ts`. Fijate que `getMe(token)`
manda el JWT en el header `Authorization: Bearer <token>`. Y en `src/types.ts`
el `interface User` refleja el `UserRead` del backend — **sin** `hashed_password`.

> 🧠 **Pregunta de cierre**: ¿dónde se guarda el token y por qué? (en esta
> demo, `localStorage`). ¿Qué riesgo de seguridad introduce guardar un JWT en
> `localStorage`? (pista: XSS — investigá en la puesta en común).

---

## Fase 6 — Verificación final (5 min)

Registrate, logueate y accedé a tu perfil:

```bash
# 1. Registrate
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"juan@ejemplo.com","password":"supersecreto123"}'
# → 201, con id, email y created_at (SIN hashed_password)

# 2. Logueate (guardá el token)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"juan@ejemplo.com","password":"supersecreto123"}'
# → {"access_token":"eyJ...","token_type":"bearer"}

# 3. Usá el token para acceder a /me (reemplazá TOKEN)
curl http://localhost:8000/api/users/me -H "Authorization: Bearer TOKEN"
# → tu usuario

# 4. Probá SIN token
curl http://localhost:8000/api/users/me
# → 401 {"detail":"Not authenticated"}

# 5. Probá login con contraseña MAL
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"juan@ejemplo.com","password":"incorrecta"}'
# → 401 "Email o contraseña incorrectos"  (¡mismo mensaje genérico!)
```

Y abrí el Swagger (`http://localhost:8000/docs`): usá el botón **Authorize**
para pegar el token y ver cómo las rutas protegidas se desbloquean.

---

## 🔐 La solución

> La solución completa **NO está en este repo**. El docente la libera al
> final de la clase en la rama `solucion`. Cuando se anuncie, hacé:
>
> ```bash
> git fetch origin
> git diff main..origin/solucion
> ```
>
> Y compará tu código con la solución.
>
> **La gracia del taller está en descubrirlo vos.** Si la solución estuviera
> acá desde el principio, no aprenderías nada.
