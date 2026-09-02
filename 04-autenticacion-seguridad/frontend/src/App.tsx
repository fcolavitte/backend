import { useEffect, useState } from "react";
import "./App.css";
import type { User } from "./types";
import { getMe, login, register } from "./api";

/**
 * Frontend del Módulo 04 — ciclo de autenticación completo.
 *
 * Flujo:
 *   1. Sin token → pantalla de login/register.
 *   2. Al loguearte (o registrarte) → guardás el JWT y lo usás para `getMe()`.
 *   3. Con token válido → pantalla de perfil (email + fecha).
 *   4. Logout → borrás el token y volvés a la pantalla de login.
 *
 * El token se guarda en `localStorage` (solo para esta demo académica). En
 * producción, JWT en localStorage tiene tradeoffs de seguridad (XSS) que
 * vale la pena discutir — ver la puesta en común.
 */

const TOKEN_KEY = "token";

export default function App() {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY));
  const [user, setUser] = useState<User | null>(null);
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Si hay token al montar, intentamos recuperar el perfil.
  useEffect(() => {
    if (!token) return;
    let cancelled = false;
    getMe(token)
      .then((u) => {
        if (!cancelled) setUser(u);
      })
      .catch(() => {
        // Token inválido o expirado → lo descartamos.
        if (!cancelled) logout();
      });
    return () => {
      cancelled = true;
    };
  }, [token]);

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
    setError(null);
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      if (mode === "register") {
        await register({ email, password });
        // Registro OK → logueamos automáticamente.
        const { access_token } = await login({ email, password });
        localStorage.setItem(TOKEN_KEY, access_token);
        setToken(access_token);
      } else {
        const { access_token } = await login({ email, password });
        localStorage.setItem(TOKEN_KEY, access_token);
        setToken(access_token);
      }
      setPassword("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error inesperado");
    } finally {
      setLoading(false);
    }
  }

  // ── Vista autenticada ──────────────────────────────────────────
  if (user) {
    return (
      <main className="app">
        <h1>Mi Cuenta</h1>
        <div className="profile">
          <p className="label">Email</p>
          <p className="value">{user.email}</p>
          <p className="label">Registrado el</p>
          <p className="value">{new Date(user.created_at).toLocaleString("es-AR")}</p>
        </div>
        <button className="logout" onClick={logout}>
          Cerrar sesión
        </button>
        <p className="hint">
          Este perfil se cargó con <code>GET /api/users/me</code> usando el
          token en el header <code>Authorization: Bearer</code>.
        </p>
      </main>
    );
  }

  // ── Vista de login/register ────────────────────────────────────
  return (
    <main className="app">
      <h1>Mi Cuenta</h1>

      <div className="tabs">
        <button
          className={mode === "login" ? "active" : ""}
          onClick={() => {
            setMode("login");
            setError(null);
          }}
        >
          Iniciar sesión
        </button>
        <button
          className={mode === "register" ? "active" : ""}
          onClick={() => {
            setMode("register");
            setError(null);
          }}
        >
          Registrarse
        </button>
      </div>

      <form onSubmit={handleSubmit} className="auth-form">
        <input
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="email@ejemplo.com"
          required
        />
        <input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Contraseña (mín. 8 caracteres)"
          minLength={8}
          required
        />
        <button type="submit" disabled={loading || !email.trim() || password.length < 8}>
          {loading ? "Procesando…" : mode === "login" ? "Entrar" : "Crear cuenta"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      <p className="hint">
        {mode === "register"
          ? "El backend hashea tu contraseña con Argon2 antes de guardarla."
          : "El backend verifica tus credenciales y te devuelve un JWT."}
      </p>
    </main>
  );
}
