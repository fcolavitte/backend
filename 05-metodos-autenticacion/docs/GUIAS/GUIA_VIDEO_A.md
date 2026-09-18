# Guía Video A — Hussein Nasser · Cinco autenticaciones de menos a más seguras

| | |
|---|---|
| **Título** | Five Password Authentications From Least to Most Secure |
| **Autor** | Hussein Nasser (487K suscriptores) |
| **Duración** | 17:38 |
| **Link** | https://www.youtube.com/watch?v=_t8EPImx9LI |

---

## Por qué este video

Hussein Nasser es referente mundial en arquitectura de bases de datos y
sistemas. En este video hace exactamente lo que nosotros vamos a hacer:
**ordenar los métodos de autenticación por su nivel de seguridad** y explicar
por qué cada uno supera al anterior. Es la base conceptual perfecta para el
módulo, y los 7 métodos del backend de ejemplo son una implementación práctica
de lo que él explica.

> ⚠️ **Nota de contexto**: el video cubre 5 esquemas. Nosotros vemos 7. Los 2
> que agrega el módulo son **OAuth2 y SSO**, que entran en la categoría de
> *delegación* (el IdP valida por vos). Son los que él no trata en detalle —
> por eso además mirás el Video B.

---

## Qué mirar (timeline con foco)

| Minuto | Qué pasa | Dónde poner atención |
|--------|----------|----------------------|
| 0:00–2:00 | Intro y planteo | ¿Cómo define "secure"? ¿qué métrica usa? |
| 2:00–6:00 | Los esquemas más básicos | ¿Por qué son los MENOS seguros? ¿qué les falta? |
| 6:00–11:00 | El salto de seguridad | Notá CUÁL es el cambio que más sube la seguridad — y por qué |
| 11:00–15:00 | Los más seguros | ¿Qué tradeoff traen? (costo, complejidad, UX) |
| 15:00–17:38 | Cierre y ranking | Armate el ranking final vos mismo antes de que él lo diga |

---

## Preguntas de comprensión (respondelas mientras mirás)

1. **¿Cuál es la métrica** que usa para ordenar "de menos a más seguro"?
2. **¿En qué posición** queda nuestro método 1 (Basic Auth)? ¿Coincide con lo
   que dice la matriz del módulo?
3. **¿Cuál es el eslabón intermedio** que la mayoría de las apps debería estar
   usando y no usa?
4. **¿Por qué el más seguro del ranking** no es el más usado en la práctica?
5. **¿Dónde encajan JWT y OAuth** en ese ranking? (pista: no son "más
   seguros", son *otra dimensión* — la delegación)

---

## Conexión con los 7 métodos del módulo

| Lo que él dice | El método del módulo que lo implementa |
|----------------|----------------------------------------|
| El esquema más débil | `basic.py` — Basic Auth |
| El que guarda estado en el server | `session_cookie.py` — Session Based |
| El salto de seguridad | `token_bearer.py` y `jwt_header.py` — Token opaco y JWT |
| La fascinación por token auto-contenido | `jwt_header.py` + `jwt_cookie.py` |
| *(no lo cubre)* | `oauth2.py` + `sso_simulado.py` — delegación |

## Después de mirar

- Completá el **mapa mental** del [Material de Aula](MATERIAL_AULA.md) con lo
  que viste.
- Leé la [Matriz Comparativa](MATRIZ_COMPARATIVA.md) de nuevo: ahora las
  filas de Basic, Sessions, Tokens y JWT te van a sonar familiares.