# Guía Video B — BekBrace · OAuth 2.0 con FastAPI (con nota)

| | |
|---|---|
| **Título** | OAuth 2.0 with FastAPI in 5 minutes |
| **Autor** | BekBrace |
| **Duración** | ~5 min |
| **Link** | https://www.youtube.com/watch?v=U8v2RsAcXoM |

---

## ⚠️ LEÉ ESTO ANTES DE MIRAR

Este video es **excelente para entender el flujo OAuth2** pero usa dos
librerías que hoy están **obsoletas y no debés copiar**:

| Librería | Problema | Reemplazo 2026 |
|----------|----------|----------------|
| `passlib` | Sin mantenimiento desde 2020, bugs de compatibilidad abiertos | `pwdlib[argon2]` |
| `python-jose` | CVEs abiertos, mantenimiento errático | `pyjwt` |

**Nuestro ejemplo de la materia** usa el stack correcto:
`pwdlib[argon2]` (hash de passwords) + `pyjwt` (tokens). Miralo con esa
lente: **la librería es lo de menos, el flujo es lo importante**.

---

## Por qué este video

El Video A (Nasser) cubre los 5 esquemas clásicos. Lo que NO cubre es la
**delegación** — y ahí entra OAuth2. BekBrace muestra el flujo de
consentimiento en la práctica, que es la pieza que el módulo 05 agrega como
métodos 6 y 7.

## Qué mirar

| Qué pasa | Dónde poner atención |
|----------|----------------------|
| El formulario de login | ¿Quién recibe realmente la password? (pista: el IdP, no la app) |
| El "consentimiento" | ¿La app le pide permiso al usuario PARA QUÉ? (scopes) |
| El token que devuelve | ¿Es un JWT? ¿qué claims tiene? Notá el formato |
| El endpoint protegido | ¿Cómo se valida el token del lado del server? |

## Preguntas de comprensión

1. **¿Qué es el "consentimiento"** en OAuth2 y por qué es la clave de la
   delegación?
2. **¿La password del usuario viaja a la app** o al servidor de autorización?
3. **¿Qué rol** cumplen `client_id` y el `scope`?
4. **¿Qué diferencia ves** entre el token de BekBrace y el JWT de nuestro
   `jwt_header.py`? (pista: ambos son JWT — pero uno nació en un *flujo de
   delegación*)

---

## Conexión con el módulo

| Lo que muestra el video | Lo que tenés en el módulo |
|-------------------------|---------------------------|
| Flujo OAuth2 password | `oauth2.py` — `POST /api/auth/oauth2/token` con form OAuth2 |
| Token que se valida en el server | `GET /api/me/oauth2` con bearer |
| Delegación a un IdP | `sso_simulado.py` — el IdP emite `id_token`, la app valida `iss`/`aud` |

> 💡 **Experimento**: probá el método 6 (OAuth2) y el 7 (SSO) en el backend
> del módulo. Después volvé al video: vas a ver que el *flujo* es el mismo,
> solo cambia quién emite el token.

---

## Después de mirar

- Logueate con OAuth2 (`bash scripts/verificar_metodos.sh`, bloque 6) y con SSO
  (bloque 7). Mirá qué contadores cambian en `/api/health`.
- Leé [CASOS_DE_USO.md](CASOS_DE_USO.md), casos 4, 5 y 6: son los escenarios
  donde OAuth2 y SSO son la decisión correcta.