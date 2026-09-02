# 📖 Material Previo — Autenticación y Seguridad (aula invertida)

> **Módulo 04 — Desarrollo de Software 2026**
> **Leé esto ANTES de la clase.** La clase es un taller: si no venís con esto
> leído, no vas a poder construir. El aula es para HACER, no para enterarte.

---

## La promesa

Hasta ahora, tu API de tareas era **de puertas abiertas**: cualquiera que
conociera la URL podía listar, crear, editar y borrar tareas. No había forma
de distinguir *quién* hacía cada cosa.

Hoy vas a cerrar la puerta. Vas a aprender a:

1. **Registrar usuarios** (guardando la contraseña protegida, jamás en texto plano)
2. **Loguearlos** (verificar que son quienes dicen ser)
3. **Mantener sesiones** (que el server recuerde quién sos entre request y request)
4. **Distinguir SSO de JWT** (y por qué compararlos es un error conceptual)
5. **Defenderte de las amenazas más comunes** (OWASP Top 10)

---

## 1. Las tres preguntas que la gente confunde (la lección de fondo)

Cuando hablamos de "login" en realidad hay **tres preguntas distintas** que
conviene no mezclar:

| Pregunta | Nombre | Ejemplo |
|----------|--------|---------|
| ¿Quién sos? | **Autenticación** | Ingresás email + contraseña |
| ¿Qué podés hacer? | **Autorización** | "Solo el dueño puede borrar SU tarea" |
| ¿Cómo lo demuestro en cada request? | **Sesión / token** | Cookie de sesión o JWT en cada request |

Hoy nos enfocamos en la primera y la tercera. La autorización (roles,
permisos) es la base de los próximos módulos (RBAC). Pero es imposible
hablar de "qué podés hacer" si antes no resolvimos "quién sos".

> 🧠 **El principio**: la autenticación responde "¿sos quien decís ser?".
> Es distinta de la autorización, que responde "¿te dejo hacer esto?". Un
> sistema puede saber perfectamente quién sos y aun así negarte el acceso a
> algo. Y al revés: un bug de autorización no arregla una mala autenticación.

---

## 2. El problema: contraseñas en texto plano

La tentación de todo principiante es guardar la contraseña tal cual:

```
users
├── id
├── email
└── password   ← "supersecreto123" (¡ERROR GRAVÍSIMO!)
```

¿Por qué está mal? Porque si la base se filtra (y las bases se filtran todo
el tiempo), **todas las contraseñas quedan expuestas**. Y como la gente
reutiliza contraseñas, el atacante no solo entra a TU app: entra a su banco,
su mail, su Netflix.

### La solución: hash (con sal)

Guardamos un **hash**, no la contraseña. Un hash es una función **unidireccional**:

```
contraseña ──► hash(password) ──► "una cadena larga e ilegible"
                          │
                          └──► NO se puede revertir
```

Para loguear, en lugar de "comparar contraseñas", hacemos:

```
hash(contraseña ingresada) == hash guardado ?
```

Si coinciden, era la misma contraseña. Si no, no. En ningún momento
recuperamos la contraseña original.

**Y no alcanza con cualquier hash.** `MD5` o `SHA1` son **rápidos**: un
atacante con una GPU puede probar miles de millones de contraseñas por
segundo (brute-force). Necesitamos un hash **diseñado para contraseñas**:
lento, costoso, con "sal" (un valor aleatorio único por usuario).

**Argon2** es el ganador del Password Hashing Competition (2015). Es el
estándar actual. Lo vas a usar hoy.

> 🧠 **El principio**: nunca guardes contraseñas. Guardá su hash con un
> algoritmo diseñado para ser lento (Argon2, bcrypt, scrypt). "Lento" es
> una FEATURE acá: hace inviable el brute-force.

### 📚 Para profundizar en este tema

- 🔗 **[OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)** — la guía oficial de cómo guardar contraseñas (Argon2, bcrypt, scrypt, sal, pepper). **Léela sí o sí.**
- 🔗 **[Argon2 — Password Hashing Competition](https://www.password-hashing.net/)** — el sitio oficial del concurso que Argon2 ganó. Explica por qué ganó.
- 🔗 **[Argon2 — Paper (PDF)](https://github.com/P-H-C/phc-winner-argon2)** — el paper técnico, para quien quiera entender los parámetros (memoria, tiempo, paralelismo).
- 🎬 **Computerphile — [Password Cracking](https://www.youtube.com/@Computerphile)** — buscá *"password cracking"*: muestran cómo se rompen hashes débiles y por qué los lentos importan.
- 🔗 **[Have I Been Pwned?](https://haveibeenpwned.com/)** — el sitio de Troy Hunt: verificá si tu email estuvo en alguna filtración. Te va a dejar pensando.

---

## 3. Sesiones: ¿cómo "recuerdo" quién sos entre requests?

HTTP es **stateless** (sin estado): cada request es independiente. El server
no recuerda nada entre uno y otro. Entonces, ¿cómo sabe que "este request es
de Juan, que ya se logueó"?

Hay dos estrategias grandes. **Entender el tradeoff entre ambas es LA
lección conceptual de hoy.**

### 3.1 Sesión server-side (el "viejo y confiable")

1. Logueás. El server genera un **id de sesión** aleatorio.
2. El server **guarda** ese id (en memoria, base, o Redis) asociado a tu usuario.
3. Te devuelve el id en una **cookie** (`Set-Cookie: session_id=...`).
4. En cada request, tu navegador reenvía la cookie. El server busca el id
   en su almacén y recupera "ah, sos Juan".

**Ventaja**: revocación inmediata. Si querés desloguear a Juan, **borrás la
fila** del almacén. Listo, ya no vale.

**Desventaja**: el server guarda estado. Si tenés 10 servidores (escala
horizontal), todos necesitan acceder al MISMO almacén de sesiones (Redis
compartido), o el usuario se "desloguea" al cambiar de servidor.

### 3.2 Token (JWT) — stateless

1. Logueás. El server **firma** un token (JWT) con tu identidad.
2. **No guarda nada.** Te devuelve el token.
3. En cada request reenviás el token. El server **verifica la firma** (sin
   consultar base) y confía en lo que dice el token.

**Ventaja**: el server no guarda estado. Cualquier servidor con la misma
clave puede verificar el token → escala horizontal fácil.

**Desventaja**: revocación difícil. El token es válido hasta que **expira**
(`exp`). Si se lo roban, no podés "anularlo" fácilmente (a menos que armes
una blacklist, lo cual reintroduce el estado que querías evitar).

### El tradeoff, en una tabla

| | Sesión server-side | JWT |
|---|---|---|
| Estado | En el server | En el token (cliente) |
| Revocación | Fácil (borrás la sesión) | Difícil (esperar `exp` o blacklist) |
| Escala horizontal | Necesita almacén compartido (Redis) | Fácil (solo la clave) |
| Dónde vive la sesión | DB/Redis | En el cliente |

**Ninguno es "mejor" en abstracto.** Es una decisión de arquitectura:
¿priorizás poder echar a alguien al instante, o escalar sin estado?

> 🧠 **El principio**: HTTP no tiene estado. La sesión es una capa que
> construimos ENCIMA. Podés mantenerla en el server (stateful) o firmarla en
> un token y dársela al cliente (stateless). Es un tradeoff, no una guerra.

### 📚 Para profundizar en este tema

- 🔗 **[jwt.io — Introduction to JSON Web Tokens](https://jwt.io/introduction)** — la intro canónica. Tiene el debugger interactivo para ver el payload de un JWT.
- 🔗 **[RFC 7519 — JSON Web Token](https://datatracker.ietf.org/doc/html/rfc7519)** — la especificación formal del JWT.
- 🔗 **[MDN — HTTP Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies)** — cómo funcionan las cookies (el vehículo de la sesión server-side).
- 🎬 **Hussein Nasser — [Session vs JWT](https://www.youtube.com/@hnasr)** — explica el tradeoff con diagramas. Buscá *"session vs jwt"*.
- 📖 **Auth0 Docs — [Token Based Authentication](https://auth0.com/docs/secure/tokens)** — Auth0 explica los fundamentos de tokens y sesiones muy claro.

---

## 4. ¿Qué es un JWT, exactamente?

Un JWT (**JSON Web Token**) es un **formato** de token. No es un protocolo de
login, no es un mecanismo de sesión completo: es una forma estándar de
codificar y **firmar** información.

Tiene tres partes, separadas por puntos:

```
header.payload.signature
```

- **Header** — qué algoritmo de firma se usa (`{"alg": "HS256", "typ": "JWT"}`)
- **Payload** — los "claims" (afirmaciones): quién sos (`sub`), cuándo expira (`exp`), etc.
- **Signature** — la firma criptográfica que garantiza que **nadie alteró** las dos primeras partes

El punto clave: el payload está **codificado (base64), NO encriptado**. Cualquiera
puede leerlo. Por eso **jamás pongas secretos ni datos sensibles** en el JWT.
La firma solo garantiza *integridad y autenticidad* ("no fue alterado y lo firmó
el server"), no *confidencialidad*.

> 🧠 **El principio**: el JWT se firma, no se encripta. La firma responde
> "¿puedo confiar en que esto salió del server?". No responde "¿lo puede
> leer alguien más?" — sí, cualquiera puede leerlo. Nada de contraseñas ni
> datos sensibles en el payload.

> 🔐 **¿Y dónde guardo el token en el frontend?** Es una decisión con
> tradeoff. Dos opciones comunes:
> - **`localStorage`**: fácil, pero vulnerable a **XSS** (cualquier script
>   que se ejecute en tu página puede leerlo).
> - **Cookie `httpOnly`**: el JS no puede leerla (mitiga XSS), pero abre la
>   puerta a **CSRF**, que hay que mitigar aparte (token anti-CSRF, SameSite).
> En este taller usamos `localStorage` por simplicidad académica, pero es un
> tema que vas a discutir en la puesta en común.

### 📚 Para profundizar en este tema

- 🔗 **[jwt.io — JSON Web Tokens](https://jwt.io/)** — el debugger interactivo: pegá un token y ves header/payload/signature.
- 🔗 **[RFC 7519 — JWT](https://datatracker.ietf.org/doc/html/rfc7519)** — la spec completa.
- 🔗 **[RFC 7515 — JWS (firma)](https://datatracker.ietf.org/doc/html/rfc7515)** — cómo se firma el token (la parte de la firma).
- 🎬 **Computerphile — [JWT](https://www.youtube.com/@Computerphile)** — video corto que explica JWT sin humo.

---

## 5. SSO vs JWT: el error conceptual más común

**SSO (Single Sign-On)** y **JWT** se comparan todo el tiempo... y está mal.
Son cosas de **categorías distintas**.

- **SSO** es un **flujo / protocolo de autenticación delegada**. La idea:
  te logueás UNA vez en un proveedor (Google, tu empresa) y accedés a MUCHOS
  servicios sin volver a loguearte. Ejemplos de protocolos: **SAML**, **OIDC**
  (que está construido sobre **OAuth 2.0**).

- **JWT** es un **formato de token**. Es CÓMO se codifica y firma la
  información, no QUÉ flujo estás usando.

**La clave**: son ortogonales. Un SSO casi siempre **emite un JWT** como token
de acceso (en OIDC, el "ID token" es un JWT). SAML, en cambio, usa
assertions XML, no JWT.

La analogía: SSO es "el sistema de riego" (el flujo: abrir la canilla central
y que riegue todo el jardín). JWT es "el tipo de caño" (el material con el que
se fabrica el agua que viaja). Compararlos es como comparar el sistema de
riego con el caño de PVC: no compiten, **se combinan**.

> 🧠 **El principio**: SSO es un *flujo*; JWT es un *formato*. Un SSO
> (vía OIDC) normalmente emite un JWT. No es "SSO vs JWT": es "SSO con JWT".

### 📚 Para profundizar en este tema

- 🔗 **[Auth0 — What is SSO?](https://auth0.com/docs/authenticate/single-sign-on)** — explicación clara de Single Sign-On.
- 🔗 **[Auth0 — SAML vs OIDC](https://auth0.com/docs/authenticate/protocols/saml/saml-sso-concepts/saml-vs-oidc)** — las dos familias de SSO comparadas.
- 🔗 **[OpenID Connect — Spec](https://openid.net/developers/how-connect-works/)** — el protocolo OIDC (SSO moderno sobre OAuth 2.0).
- 🔗 **[OAuth 2.0 Simplified](https://aaronparecki.com/oauth-2-simplified/)** — el libro online gratuito de Aaron Parecki, la mejor intro a OAuth/OIDC.
- 🎬 **OktaDev — [OAuth and OpenID Connect in Plain English](https://www.youtube.com/@OktaDev)** — video que desenreda OAuth vs OIDC vs SAML.

---

## 6. Seguridad OWASP: las amenazas de las que te defendés

**OWASP** (Open Worldwide Application Security Project) publica el **Top 10**:
las 10 categorías de riesgo más críticas en aplicaciones web. Hoy te
concentrás en las que tocan de lleno a la autenticación:

| Posición OWASP (2021) | Nombre | Qué significa en NUESTRO contexto |
|---|---|---|
| **A01** | Broken Access Control | Endpoints sin proteger (cualquiera borra) → `get_current_user` |
| **A02** | Cryptographic Failures | Contraseñas en texto plano o hashes débiles → Argon2 |
| **A03** | Injection | SQLi, etc. → el ORM parametriza (ya lo sabías del 03) |
| **A07** | Identification & Authentication Failures | Sesiones rotas, tokens débiles, sin expiración → JWT bien firmado + `exp` |

Y dos amenazas que tocan de lleno al login y que **vamos a discutir**:

- **User enumeration**: si el login dice "el email no existe" vs "contraseña
  incorrecta", un atacante puede averiguar qué emails están registrados. La
  solución: **mensaje genérico** ("credenciales incorrectas") para ambos casos.

- **Timing attack**: si "usuario inexistente" responde más rápido que
  "contraseña mal" (porque en un caso se saltea el hash lento), un atacante
  mide el tiempo y adivina igual. La solución: **siempre** verificar contra un
  hash, incluso cuando el usuario no existe.

> 🧠 **El principio**: la seguridad no es un feature que "agregás al final".
> Es una propiedad transversal. El Top 10 de OWASP es tu checklist: repasalo
> cada vez que toques autenticación.

### 📚 Para profundizar en este tema

- 🔗 **[OWASP Top 10 (2021)](https://owasp.org/Top10/)** — la referencia obligada. Leé A01, A02, A03 y A07.
- 🔗 **[OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/index.html)** — una mina de oro: *Authentication*, *Password Storage*, *JWT*, *Session Management*.
- 🔗 **[OWASP — Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)** — todo lo que deberías hacer al autenticar.
- 🔗 **[OWASP — JSON Web Token Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)** — los errores clásicos con JWT (aunque diga "Java", los conceptos aplican).
- 🎬 **LiveOverflow — [canal](https://www.youtube.com/@LiveOverflow)** — seguridad real explicada en profundidad. Buscá *"JWT attack"*.

---

## Autoevaluación (hacela antes de venir)

Respondé mentalmente. Si dudás, releé la sección:

1. ¿Cuál es la diferencia entre **autenticación** y **autorización**?
2. ¿Por qué NUNCA guardamos la contraseña en texto plano? ¿Qué guardamos en su lugar?
3. ¿Por qué MD5 o SHA1 son malos para contraseñas? ¿Qué tiene Argon2 que no tienen ellos?
4. ¿Cuál es el **tradeoff** entre sesión server-side y JWT?
5. ¿El JWT se **encripta** o se **firma**? ¿Qué implica eso para su payload?
6. ¿Por qué está mal comparar "SSO vs JWT"? ¿Qué es cada uno?
7. ¿Qué es el **user enumeration** y cómo lo evita un mensaje de login genérico?
8. ¿Qué categorías del OWASP Top 10 tocan de lleno a la autenticación?

---

## Qué vas a necesitar en clase

- El proyecto del Módulo 03 (la arquitectura en capas, que extendemos)
- Tu `DATABASE_URL` (Docker o Supabase, la misma de siempre)
- `uv` instalado (ya lo usás) y `pnpm` para el frontend
- **Actitud de taller**: vas a construir en grupo, no a copiar.

> *"La Universidad te da el mapa. El recorrido lo hacés vos."*
