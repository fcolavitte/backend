/**
 * api.ts — el CLIENTE HTTP del laboratorio. Está COMPLETO a propósito:
 * la lección del módulo no es el transporte, es la AUTORIZACIÓN.
 *
 * Cada llamada tiene un label didáctico que explica qué autorización se
 * está poniendo a prueba. Mirá la consola abajo en la UI: cada request
 * aparece con método, ruta y status. Ese status ES la lección:
 *
 *   - 200/201 → el server te dejó pasar (¿debería? mirá la matriz)
 *   - 401     → no autenticado (token inválido/ausente)
 *   - 403     → autenticado pero SIN permiso (esto es lo que estás
 *               implementando en el backend)
 *   - 404     → el recurso no existe
 *
 * El token viaja en `Authorization: Bearer <jwt>` — el patrón para APIs
 * del módulo 05. El frontend lo guarda en memoria (y localStorage para
 * no perderlo al refrescar): ojo, en producción un SPA usa cookies
 * httpOnly o memoria + refresh, NUNCA localStorage, por riesgo de XSS.
 * Acá es un laboratorio: la simplicidad es la lección.
 */

import type {
  ApiResult,
  DocumentPatch,
  DocumentRead,
  Health,
  JwtPayload,
  LogEntry,
  Role,
  Token,
  UserRead,
} from "./types";

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
  token?: string,
  init: RequestInit = {},
  silent = false,
): Promise<ApiResult<T>> {
  const headers: Record<string, string> = {
    ...(init.headers as Record<string, string> | undefined),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const entry: LogEntry = { id: ++seq, method, url, label, status: null };
  try {
    const res = await fetch(url, { method, headers, ...init });
    entry.status = res.status;
    if (!silent) pushLog(entry);

    const text = await res.text();
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
      entry.detail = detail;
      return { ok: false, status: res.status, data: null, detail };
    }
    return { ok: true, status: res.status, data: data as T };
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

// ── Decodificación del JWT (lección: el payload es LEGIBLE sin secreto) ────

function decodeBase64Url(part: string): string {
  const b64 = part.replace(/-/g, "+").replace(/_/g, "/");
  const padded = b64 + "=".repeat((4 - (b64.length % 4)) % 4);
  return atob(padded);
}

/**
 * Decodifica el payload de un JWT SIN verificar la firma (eso lo hace el
 * server). Por eso la UI lo muestra: un JWT no escripta nada, solo firma.
 * Si el token fue alterado, el server lo rechaza con 401 — probalo.
 */
export function decodeToken(token: string): JwtPayload | null {
  try {
    const payload = token.split(".")[1];
    if (!payload) return null;
    return JSON.parse(decodeBase64Url(payload)) as JwtPayload;
  } catch {
    return null;
  }
}

// ── Auth ───────────────────────────────────────────────────────────────────

/**
 * Login → JWT con claims de autorización (role, tenant_id, scope).
 * El scope es OPCIONAL y limita lo que ESTE token puede hacer:
 *
 *   scope = null        → el default del rol (viewer→"read", editor/admin→"read write")
 *   scope = "read"      → token de SOLO LECTURA aunque seas admin
 *   scope = "read write"→ lectura + escritura (si tu rol lo permite)
 *
 * Si un viewer pide "read write" el server responde 400: no se puede
 * auto-elevar (lección del Pilar 3).
 */
export function login(
  email: string,
  password: string,
  scope: string | null,
): Promise<ApiResult<Token>> {
  const scopeLabel = scope ? ` (scope ${JSON.stringify(scope)})` : " (scope default del rol)";
  return http<Token>("POST", "/api/auth/login", `Login → JWT con claims${scopeLabel}`, undefined, {
    headers: JSON_HEADERS,
    body: JSON.stringify({ email, password, scope }),
  });
}

/** Register: el nuevo usuario SIEMPRE nace como viewer (el rol lo asigna un admin). */
export function register(
  email: string,
  name: string,
  password: string,
): Promise<ApiResult<UserRead>> {
  return http<UserRead>(
    "POST",
    "/api/auth/register",
    "Register → nace como viewer (el rol lo asigna un admin)",
    undefined,
    { headers: JSON_HEADERS, body: JSON.stringify({ email, name, password }) },
  );
}

// ── Usuarios (solo admin de tu empresa — matriz) ───────────────────────────

export function listUsers(token: string): Promise<ApiResult<UserRead[]>> {
  return http<UserRead[]>(
    "GET",
    "/api/users",
    "GET /api/users → solo admin de tu empresa (403 si no lo sos)",
    token,
  );
}

export function changeRole(
  token: string,
  userId: number,
  role: Role,
): Promise<ApiResult<UserRead>> {
  return http<UserRead>(
    "PATCH",
    `/api/users/${userId}/role`,
    `PATCH /api/users/${userId}/role → cambia el rol a ${role} (la operación MÁS sensible)`,
    token,
    { headers: JSON_HEADERS, body: JSON.stringify({ role }) },
  );
}

// ── Documentos (el recurso protegido) ──────────────────────────────────────

export function listDocuments(token: string): Promise<ApiResult<DocumentRead[]>> {
  return http<DocumentRead[]>(
    "GET",
    "/api/documents",
    "GET /api/documents → públicos de tu empresa + los tuyos",
    token,
  );
}

export function getDocument(token: string, docId: number): Promise<ApiResult<DocumentRead>> {
  return http<DocumentRead>(
    "GET",
    `/api/documents/${docId}`,
    `GET /api/documents/${docId} → dueño / admin / público (¿IDOR?)`,
    token,
  );
}

export function createDocument(
  token: string,
  title: string,
  content: string,
): Promise<ApiResult<DocumentRead>> {
  return http<DocumentRead>(
    "POST",
    "/api/documents",
    "POST /api/documents → requiere scope write (nace draft privado)",
    token,
    { headers: JSON_HEADERS, body: JSON.stringify({ title, content }) },
  );
}

export function updateDocument(
  token: string,
  docId: number,
  patch: DocumentPatch,
): Promise<ApiResult<DocumentRead>> {
  return http<DocumentRead>(
    "PATCH",
    `/api/documents/${docId}`,
    `PATCH /api/documents/${docId} → dueño o admin + scope write`,
    token,
    { headers: JSON_HEADERS, body: JSON.stringify(patch) },
  );
}

export function deleteDocument(token: string, docId: number): Promise<ApiResult<DocumentRead>> {
  return http<DocumentRead>(
    "DELETE",
    `/api/documents/${docId}`,
    `DELETE /api/documents/${docId} → SOLO admin + scope write`,
    token,
  );
}

export function publishDocument(token: string, docId: number): Promise<ApiResult<DocumentRead>> {
  return http<DocumentRead>(
    "POST",
    `/api/documents/${docId}/publish`,
    `POST /api/documents/${docId}/publish → dueño o admin + scope write`,
    token,
  );
}

// ── Health (polling del HealthBar; silent para no llenar la consola) ───────

export function health(): Promise<ApiResult<Health>> {
  return http<Health>("GET", "/api/health", "Health: contadores del server", undefined, {}, true);
}