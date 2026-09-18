/**
 * Tipos del contrato de la API (módulo 05).
 *
 * Espejo de app/models.py del backend. La lección del Módulo 03 sigue
 * valiendo: si el backend cambia un campo, TypeScript te avisa ACÁ antes
 * de ejecutar. Compará campo por campo:
 *
 *   UserRead   → id, email, name, created_at (SIN password_hash)
 *   Token      → access_token, token_type
 *   Message    → message
 *   SSOExplain → flow, steps
 *   Health     → status, users_count, sessions_count, api_tokens_count,
 *                login_failures_count, note
 */

export interface UserRead {
  id: number;
  email: string;
  name: string;
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface Message {
  message: string;
}

export interface SSOExplain {
  flow: string;
  steps: string[];
}

export interface Health {
  status: string;
  users_count: number;
  sessions_count: number;
  api_tokens_count: number;
  login_failures_count: number;
  note: string;
}

/** Resultado normalizado de una request: siempre tenés status + cuerpo. */
export interface ApiResult<T> {
  ok: boolean;
  status: number;
  data: T | null;
  detail?: string;
  /** Header Retry-After del 429 (segundos), si vino. */
  retryAfter?: string;
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