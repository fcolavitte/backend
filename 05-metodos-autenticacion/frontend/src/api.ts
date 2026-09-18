/**
 * api.ts — UN mecanismo distinto por método. Esta es la lección del módulo.
 *
 * Mirá cómo cambia la request entre métodos:
 *
 *   - Basic  → header `Authorization: Basic base64(email:pass)` en CADA request
 *   - Session→ POST JSON + cookie httpOnly (la guarda el browser, no el JS)
 *   - Token  → POST form-urlencoded + header `Authorization: Bearer <opaco>`
 *   - JWT    → POST JSON + header `Authorization: Bearer <jwt>`
 *   - JWT cookie → POST JSON + cookie httpOnly con el JWT adentro
 *   - OAuth2 → POST form-urlencoded (grant_type=password, estándar del protocolo)
 *   - SSO    → POST JSON a "el IdP" simulando la emisión de un id_token
 *
 * El parámetro `credentials: "include"` en los métodos de cookie es CLAVE:
 * sin él, el browser no envía/recibe cookies entre orígenes. Como igual
 * vamos por el proxy de Vite (mismo-origen), la cookie viaja sola.
 */

import type { ApiResult, Health, LogEntry, Message, SSOExplain, Token, UserRead } from "./types";

// ── Consola didáctica ──────────────────────────────────────────────────────
// El frontend registra acá cada request; App.tsx lo muestra en la consola.
let logSink: ((entry: LogEntry) => void) | null = null;
let seq = 0;

export function setLogSink(sink: (entry: LogEntry) => void): void {
  logSink = sink;
}

function pushLog(entry: LogEntry): void {
  logSink?.(entry);
}

/** fetch con manejo de errores normalizado: siempre devolvemos status+cuerpo. */
async function http<T>(
  method: string,
  url: string,
  label: string,
  init: RequestInit = {},
  silent = false,
): Promise<ApiResult<T>> {
  const entry: LogEntry = { id: ++seq, method, url, status: null, label };
  try {
    const res = await fetch(url, { method, credentials: "same-origin", ...init });
    entry.status = res.status;
    if (!silent) pushLog(entry);
    const text = await res.text();
    const retryAfter = res.headers.get("Retry-After") ?? undefined;
    let data: unknown = null;
    try {
      data = text ? JSON.parse(text) : null;
    } catch {
      data = text;
    }
    if (!res.ok) {
      const detail =
        data && typeof data === "object" && "detail" in data
          ? String((data as { detail: unknown }).detail)
          : `HTTP ${res.status}`;
      const result: ApiResult<T> = { ok: false, status: res.status, data: null, detail, retryAfter };
      return result;
    }
    return { ok: true, status: res.status, data: data as T, retryAfter };
  } catch (err) {
    entry.status = 0;
    if (!silent) pushLog(entry);
    return {
      ok: false,
      status: 0,
      data: null,
      detail: err instanceof Error ? err.message : "Error de red",
    };
  }
}

const JSON_HEADERS = { "Content-Type": "application/json" };
const FORM_HEADERS = { "Content-Type": "application/x-www-form-urlencoded" };

// ── 1 · BASIC AUTH ─────────────────────────────────────────────────────────
// LECCIÓN: no hay login. Las credenciales viajan en CADA request, en base64.
// base64 NO es cifrado: cualquiera puede decodificarlo. Esto solo tiene
// sentido sobre HTTPS (que cifra el canal).

export function basicMe(email: string, password: string): Promise<ApiResult<UserRead>> {
  const token = btoa(`${email}:${password}`);
  return http<UserRead>(
    "GET",
    "/api/me/basic",
    `Authorization: Basic ${token}`,
    { headers: { Authorization: `Basic ${token}` } },
  );
}

// ── 2 · SESSION BASED ──────────────────────────────────────────────────────
// LECCIÓN: el login crea una sesión EN EL SERVER y la guarda en una cookie
// httpOnly. El browser guarda y reenvía la cookie SOLO (el JS no la ve).
// Logout = borrar la sesión en el server → revocación INMEDIATA.

export function sessionLogin(email: string, password: string): Promise<ApiResult<Token>> {
  return http<Token>("POST", "/api/auth/session/login", "Login → cookie session_id (httpOnly)", {
    headers: JSON_HEADERS,
    body: JSON.stringify({ email, password }),
  });
}

export function sessionMe(): Promise<ApiResult<UserRead>> {
  return http<UserRead>("GET", "/api/me/session", "La cookie session_id viaja sola (httpOnly)");
}

export function sessionLogout(): Promise<ApiResult<Message>> {
  return http<Message>(
    "POST",
    "/api/auth/session/logout",
    "Logout → borra la sesión del SERVER (revocación inmediata)",
  );
}

// ── 3 · TOKEN AUTH (opaco) ─────────────────────────────────────────────────
// LECCIÓN: token OPACO (aleatorio, sin significado) guardado en el server,
// que viaja en `Authorization: Bearer`. Form-urlencoded (el contrato clásico
// de las APIs, OAuth2PasswordRequestForm). Logout revoca en el server.

export function tokenLogin(email: string, password: string): Promise<ApiResult<Token>> {
  return http<Token>("POST", "/api/auth/token/login", "Login (form) → token opaco en server", {
    headers: FORM_HEADERS,
    body: new URLSearchParams({ username: email, password }).toString(),
  });
}

export function tokenMe(token: string): Promise<ApiResult<UserRead>> {
  return http<UserRead>("GET", "/api/me/token", "Authorization: Bearer <token opaco>", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function tokenLogout(token: string): Promise<ApiResult<Message>> {
  return http<Message>(
    "POST",
    "/api/auth/token/logout",
    "Logout → revoca el token en el SERVER",
    { headers: { Authorization: `Bearer ${token}` } },
  );
}

// ── 4 · JWT EN HEADER ──────────────────────────────────────────────────────
// LECCIÓN: el token lleva la info ADENTRO (header.payload.signature) firmada.
// NO hay estado en el server → no aparece en el health, escala horizontal.
// El payload es LEGIBLE sin secreto (base64url) — decodificalo en el front.

export function jwtLogin(email: string, password: string): Promise<ApiResult<Token>> {
  return http<Token>("POST", "/api/auth/jwt/login", "Login → JWT firmado (stateless)", {
    headers: JSON_HEADERS,
    body: JSON.stringify({ email, password }),
  });
}

export function jwtMe(token: string): Promise<ApiResult<UserRead>> {
  return http<UserRead>("GET", "/api/me/jwt", "Authorization: Bearer <jwt>", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

// ── 5 · JWT EN COOKIE (httpOnly) ───────────────────────────────────────────
// LECCIÓN: el MISMO JWT del método 4, pero el vehículo es una cookie httpOnly
// (mitiga XSS, abre CSRF → se mitiga con SameSite). Logout = borrar la cookie,
// pero el JWT SIGUE VÁLIDO hasta expirar (no hay estado en el server).

export function jwtCookieLogin(email: string, password: string): Promise<ApiResult<Token>> {
  return http<Token>("POST", "/api/auth/jwt-cookie/login", "Login → JWT en cookie httpOnly", {
    headers: JSON_HEADERS,
    body: JSON.stringify({ email, password }),
  });
}

export function jwtCookieMe(): Promise<ApiResult<UserRead>> {
  return http<UserRead>("GET", "/api/me/jwt-cookie", "La cookie access_token viaja sola (httpOnly)");
}

export function jwtCookieLogout(): Promise<ApiResult<Message>> {
  return http<Message>(
    "POST",
    "/api/auth/jwt-cookie/logout",
    "Logout → borra cookie (el JWT sigue válido hasta expirar)",
  );
}

// ── 6 · OAUTH 2.0 (password flow) ──────────────────────────────────────────
// LECCIÓN: OAuth2 es el PROTOCOLO (flujo + endpoints + grant types), JWT es
// el FORMATO del token. El contrato es estándar: POST form-urlencoded con
// grant_type + username + password. Acá el password flow es el grant_type.

export function oauth2Token(email: string, password: string): Promise<ApiResult<Token>> {
  return http<Token>(
    "POST",
    "/api/auth/oauth2/token",
    "OAuth2 password flow: POST /token (grant_type=password)",
    {
      headers: FORM_HEADERS,
      body: new URLSearchParams({
        grant_type: "password",
        username: email,
        password,
      }).toString(),
    },
  );
}

export function oauth2Me(token: string): Promise<ApiResult<UserRead>> {
  return http<UserRead>("GET", "/api/me/oauth2", "Authorization: Bearer <jwt de OAuth2>", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

// ── 7 · SSO (OIDC simulado) ────────────────────────────────────────────────
// LECCIÓN: SSO es la EXPERIENCIA — el token lo emite un IdP (tercero) con
// claims OIDC (iss, aud, sub, email). Nuestra app valida firma + iss + aud
// y hace JIT provisioning si el email no existe todavía.

export function ssoExplain(): Promise<ApiResult<SSOExplain>> {
  return http<SSOExplain>("GET", "/api/sso/explain", "¿Qué es SSO? (flujo OIDC en 7 pasos)");
}

export function ssoSimulate(email: string, name: string): Promise<ApiResult<Token>> {
  return http<Token>(
    "POST",
    "/api/sso/simulate",
    "IdP (simulado) emite id_token con claims OIDC (iss/aud/sub/email)",
    { headers: JSON_HEADERS, body: JSON.stringify({ email, name }) },
  );
}

export function ssoMe(token: string): Promise<ApiResult<UserRead>> {
  return http<UserRead>(
    "GET",
    "/api/me/sso",
    "Validamos el id_token del IdP: firma + iss + aud → JIT provisioning",
    { headers: { Authorization: `Bearer ${token}` } },
  );
}

// ── HEALTH ─────────────────────────────────────────────────────────────────
// El contador vivo del lab: sessions_count solo crece con Session cookie,
// api_tokens_count solo con Token opaco. JWT/SSO no tocan nada (stateless).
//
// silent=true: este endpoint hace POLLING cada 2.5s desde el HealthBar.
// No debe llenar la consola de requests — la consola es para las acciones
// del alumno, no para el ruido de fondo del health.

export function health(): Promise<ApiResult<Health>> {
  return http<Health>("GET", "/api/health", "Health: contadores del server", {}, true);
}