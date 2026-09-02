/**
 * Tipos del contrato de la API (autenticación).
 *
 * Refleja, como tipos TypeScript, el JSON que recibe/devuelve el backend
 * FastAPI (models/user.py). La lección del Módulo 03 sigue valiendo: si el
 * backend cambia un campo, el compilador te avisa ACÁ antes de ejecutar.
 *
 * Compará campo por campo con el backend:
 *   User      → UserRead (id, email, created_at) — SIN hashed_password
 *   Token     → Token (access_token, token_type)
 *   Register  → UserCreate (email, password)
 *   Login     → UserLogin (email, password)
 */

export interface User {
  id: number;
  email: string;
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface RegisterInput {
  email: string;
  password: string;
}

export interface LoginInput {
  email: string;
  password: string;
}
