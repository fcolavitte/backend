# 📘 SPEC — Módulo 04: Autenticación y Seguridad

> **Este documento es TU recurso de aprendizaje.**
> No es un contrato frío: es el mapa de lo que vas a construir, **por qué** lo
> construimos así, y **qué vas a descubrir** en el camino. Leelo antes de
> tocar código, y volvé a él cuando te trabes.

---

## 1. Qué vas a construir

Sobre la API en capas del Módulo 03, vas a agregar la **capa de seguridad**:

- **Registro de usuarios** (`register`) → contraseña hasheada con **Argon2**
- **Login** → verificación de credenciales + emisión de un **JWT**
- **Endpoint protegido** (`/api/users/me`) → solo accesible con token válido
- **Frontend React + TypeScript** → cierra el ciclo: register, login y perfil desde la UI

Y lo más importante: **vas a entender por qué cada cosa se hace así**, y qué
pasa si no se hace. Porque la seguridad no se aprende leyendo: se aprende
viendo el código vulnerable y arreglándolo.

> 🤔 **¿Qué descubriste en el Módulo 03?** Que el `404` vive en el controller
> porque es HTTP, y el service no sabe de HTTP. Hoy la lección es gemela: el
> `401` y el `409` también viven en la capa HTTP, y el hash y la firma del
> token viven en capas que NO saben de HTTP.

---

## 2. Por qué lo construimos así (la idea de fondo)

En el Módulo 03 separaste **HTTP, negocio y datos**. Hoy sumamos una
responsabilidad nueva: **seguridad**. ¿Dónde vive cada cosa?

| Responsabilidad | Dónde vive | Por qué |
|-----------------|-----------|---------|
| Hash de contraseña | `security.py` | Es una primitiva criptográfica, reutilizable |
| Verificación de credenciales | `auth_service.py` | Es una regla de negocio |
| Emisión/validación de JWT | `security.py` + `dependencies.py` | La firma es técnica; el 401 es HTTP |
| Traducir `None` → `401/409` | controllers | HTTP es la capa de presentación |

**La regla de oro (idéntica al 03)**: una capa solo conoce a la de **abajo**.
El `security.py` no sabe de HTTP. El service no lanza `401`: devuelve `None`
y el controller lo traduce. El repository no hashea ni valida: solo persiste.

> 💡 **Pista para el taller**: cuando no sepas dónde va algo, preguntate
> *"¿esto es HTTP, es negocio, es datos, o es criptografía?"*.
> - `401`/`409` es HTTP → controller / `get_current_user`
> - "el email ya existe" es negocio → service (devuelve `None`)
> - "hash esta contraseña" es criptografía → `security.py`
> - "buscá el user por email" es datos → repository

---

## 3. Qué tenés que completar (tu misión)

El repo te entrega el backend **casi listo**. Solo tenés que escribir los
archivos que son la lección:

| Archivo | Capa | Qué hacés |
|---------|------|-----------|
| `backend/app/security.py` | Seguridad | Las 4 primitivas: hash, verify, create_token, decode_token |
| `backend/app/repositories/user_repository.py` | Repository | 3 métodos de acceso a datos |
| `backend/app/services/auth_service.py` | Service | register_user + authenticate_user |
| `backend/app/dependencies.py` | HTTP/cableado | `get_current_user` (protege rutas) |
| `backend/app/controllers/auth_controller.py` | Controller | POST register + POST login |
| `backend/app/controllers/users_controller.py` | Controller | GET /api/users/me |

Todo lo demás ya viene **dado** (el modelo `User`, la conexión, el cableado
base, el entrypoint, un controller de ejemplo y el **frontend completo**). La
guía `GUIA_ALUMNO.md` te lleva paso a paso.

> 🎯 **Tu meta**: al final, poder registrarte, loguearte, recibir un JWT, y
> usarlo para acceder a `/api/users/me`. Y explicar POR QUÉ nadie puede
> suplantarte sin la clave.

---

## 4. La arquitectura

### 4.1 Dónde vive cada responsabilidad

| Capa | Carpeta | Sabe de… | NO sabe de… |
|------|---------|----------|-------------|
| Controller | `controllers/` | HTTP (rutas, 401, 409, JSON) | hash, SQL, reglas |
| Service | `services/` | Reglas de negocio (email existe, verificar) | HTTP, hash |
| Repository | `repositories/` | SQL/ORM, la base | HTTP, hash, negocio |
| Security | `security.py` | Hash, JWT (primitivas) | HTTP, negocio, SQL |

### 4.2 El flujo de login (la película completa)

```
POST /api/auth/login {email, password}
        │
        ▼
[Controller]  delega en el service
        │
        ▼
[Service]     get_by_email(email) ──► None? ──► devuelve None
        │        │
        │        └──► User ──► verify_password(password, hash)?
        │                           │
        │                           ├── False ──► devuelve None
        │                           └── True ───► devuelve User
        ▼
[Controller]  User? ──► create_access_token(str(user.id))
        │                    └──► {"access_token": "...", "token_type": "bearer"}
        │              None? ──► 401 "Email o contraseña incorrectos"
```

Y para una ruta protegida:

```
GET /api/users/me  (header: Authorization: Bearer <token>)
        │
        ▼
[get_current_user]  decode_token(token) ──► error? ──► 401
        │                    │
        │                    └──► payload["sub"] ──► get_by_id(int(sub))
        │                              │
        │                              ├── None ──► 401
        │                              └── User ──► devuelve el user
        ▼
[users_controller]  devuelve current_user
```

> 🤔 **¿Qué descubriste acá?** El `401` NO lo lanza el service ni `security.py`.
> `security.py` deja propagar la excepción del JWT; `get_current_user` la
> captura y la traduce a `401`. Es el mismo principio que el `404` del Módulo 03,
> aplicado a la seguridad.

---

## 5. El modelo de datos (User)

Una clase define la tabla (`table=True`):

```python
class User(UserBase, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str          # ← el hash, NO el texto plano
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False))
```

Y heredando, qué entra y qué sale por la API:

| Clase | Rol | Nota |
|-------|-----|------|
| `User` | La TABLA (`table=True`) | Tiene `hashed_password` |
| `UserCreate` | Entrada al registrarse | `email` + `password` (texto plano, solo en el request) |
| `UserLogin` | Entrada al loguearse | `email` + `password` |
| `UserRead` | Salida | **NO incluye el hash** |
| `Token` | Salida del login | `access_token` + `token_type` |

> 🤔 **¿Qué descubriste acá?** Dos cosas críticas:
> 1. En la base NO existe columna `password`: existe `hashed_password`.
> 2. `UserRead` hereda de `UserBase`, NO de `User`, precisamente para no
>    exponer el hash. El hash se usa para verificar, jamás para devolver.

---

## 6. Los endpoints

| Método | Ruta | Qué hace | Autenticado |
|--------|------|----------|-------------|
| `GET` | `/api/health` | Verifica servicio + base | No |
| `POST` | `/api/auth/register` | Crea un usuario (`201`) | No |
| `POST` | `/api/auth/login` | Verifica credenciales, devuelve JWT | No |
| `GET` | `/api/users/me` | Devuelve el usuario autenticado | **Sí** (JWT) |

**Códigos y errores que tenés que respetar:**

| Caso | Código |
|------|--------|
| `email` mal formado / `password` < 8 / faltante | `422` |
| Register con email ya existente | `409` `{"detail": "El email ya está registrado"}` |
| Login con credenciales inválidas | `401` `{"detail": "Email o contraseña incorrectos"}` |
| Ruta protegida sin token / token inválido / expirado | `401` `{"detail": "Credenciales inválidas"}` + header `WWW-Authenticate: Bearer` |

> 💡 **Pista para el taller**: el `POST /register` devuelve `201`, no `200`.
> Y el `POST /login` devuelve `200` con el `Token`.

---

## 7. Cómo verificar tu trabajo

```bash
cd backend
uv sync
cp .env.example .env        # DATABASE_URL + SECRET_KEY
uv run -m app.main          # http://localhost:8000
```

**Checkpoints** (si los pasás, vas bien):

1. `/api/health` responde `db: "conectada"` y `users_count: 0`.
2. `POST /api/auth/register` crea un usuario y devuelve `201` **sin** `hashed_password`.
3. En la base, la columna `hashed_password` **NO** contiene tu contraseña (es un hash Argon2 que empieza con `$argon2id$`).
4. `POST /api/auth/login` con la contraseña correcta devuelve un `access_token`.
5. `GET /api/users/me` con `Authorization: Bearer <token>` devuelve tu usuario; sin token devuelve `401`.
6. Login con contraseña **incorrecta** devuelve `401` con mensaje **genérico** (igual que un email inexistente).

> 🎯 **Tu meta final**: el flujo completo register → login → `/me` funciona,
> y sabés explicar por qué una contraseña filtrada no alcanza para entrar.

---

## 8. Dónde seguir aprendiendo

- `MATERIAL_PREVIO.md` → los conceptos + **bibliografía extensa** (docs, videos, papers).
- `GUIA_ALUMNO.md` → la guía paso a paso con consignas y pistas.
- `README.md` → instalación y estructura del repo.
- La **collection Postman** (`postman/`) → para verificar el flujo feliz y los casos límite.
- El **frontend** (`frontend/`) → cierra el ciclo: register, login y perfil desde la UI.
- `GUIA_DOCENTE.md` → (solo para el docente) el análisis de diseño de la clase.
