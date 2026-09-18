/**
 * Tipos del contrato de la API (módulo 06) — espejo de app/models.py del backend.
 *
 * La lección del módulo 03 sigue valiendo: si el backend cambia un campo,
 * TypeScript te avisa ACÁ antes de ejecutar. Compará campo por campo:
 *
 *   UserRead      → id, email, name, role, tenant_id, created_at (SIN hash)
 *   DocumentRead  → id, owner_id, tenant_id, title, content,
 *                   visibility ("public"|"private"), published, created_at
 *   Token         → access_token, token_type
 *   Health        → status, users_count, documents_count, tenants_count, note
 *
 * JwtPayload es CLAVE para este módulo: es el contenido del token decodificado.
 * Es legible SIN el secreto (base64url). El rol y el scope que ves acá son
 * "lo que dice el token" — el server relee el ROL del storage en cada request
 * (security.py lo explica). El SCOPE, en cambio, ES del token.
 */

export type Role = "admin" | "editor" | "viewer";
export type Visibility = "public" | "private";

export interface UserRead {
  id: number;
  email: string;
  name: string;
  role: Role;
  tenant_id: number;
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface DocumentRead {
  id: number;
  owner_id: number;
  tenant_id: number;
  title: string;
  content: string;
  visibility: Visibility;
  published: boolean;
  created_at: string;
}

export interface Health {
  status: string;
  users_count: number;
  documents_count: number;
  tenants_count: number;
  note: string;
}

/** El payload del JWT, ya decodificado (base64url, sin verificar la firma). */
export interface JwtPayload {
  sub: string; // id del usuario
  role: Role; // rol al MOMENTO del login
  tenant_id: number;
  scope: string; // "read" | "read write" — lo que ESTE token puede hacer
  iat: number;
  exp: number;
}

/** Resultado normalizado de una request: siempre tenés status + cuerpo. */
export interface ApiResult<T> {
  ok: boolean;
  status: number;
  data: T | null;
  detail?: string;
}

/** Una línea de la consola didáctica del laboratorio. */
export interface LogEntry {
  id: number;
  method: string;
  url: string;
  status: number | null;
  label: string;
  detail?: string;
}

/** El body del PATCH /api/documents/{id} (todo opcional, al menos uno). */
export interface DocumentPatch {
  title?: string;
  content?: string;
  visibility?: Visibility;
}