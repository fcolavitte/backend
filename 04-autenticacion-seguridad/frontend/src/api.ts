/**
 * Capa de comunicación con la API (el "cliente HTTP").
 *
 * Acá viven las llamadas al backend. La novedad de ESTE módulo respecto al
 * 03 es el TOKEN: después de loguearte, guardás el JWT y lo reenviás en el
 * header `Authorization: Bearer <token>` en cada request autenticado.
 *
 * Fijate la LECCIÓN DE SEGURIDAD:
 *   - `getMe()` recibe el token como parámetro y lo manda en el header.
 *   - El frontend NO decide si el token es válido: el backend lo verifica
 *     (get_current_user). Si es inválido, recibimos 401 y reaccionamos.
 *   - El token viaja en el header Authorization, NO en la URL (en la URL
 *     queda en los logs del server y en el historial — fugas).
 */

import type { LoginInput, RegisterInput, Token, User } from "./types";

const BASE_URL = "/api";

/** Helper que hace el fetch y devuelve el JSON tipado. */
async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options);
  if (!response.ok) {
    // Leemos el detalle del backend (FastAPI devuelve {"detail": "..."}).
    const body = await response.json().catch(() => null);
    const message =
      body && typeof body.detail === "string" ? body.detail : `Error ${response.status}`;
    throw new Error(message);
  }
  return (await response.json()) as T;
}

export function register(input: RegisterInput): Promise<User> {
  return request<User>(`${BASE_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
}

export function login(input: LoginInput): Promise<Token> {
  return request<Token>(`${BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
}

/** GET /api/users/me — requiere el token válido en el header. */
export function getMe(token: string): Promise<User> {
  return request<User>(`${BASE_URL}/users/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}
