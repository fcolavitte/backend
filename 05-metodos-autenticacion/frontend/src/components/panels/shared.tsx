import { useState } from "react";
import type { ApiResult, UserRead } from "../../types";

/**
 * Piezas compartidas por los 8 paneles del laboratorio.
 *
 * Un solo componente por pieza, reutilizado por todos los métodos: el panel
 * de cada método define SU flujo, y estas piezas solo le dan la forma.
 */

// ── AuthForm: inputs de email/password con submit ─────────────────────────

const DEMO_EMAIL = "demo@ejemplo.com";
const DEMO_PASSWORD = "demo12345";

export function AuthForm({
  onSubmit,
  submitLabel,
  busy,
}: {
  onSubmit: (email: string, password: string) => Promise<void>;
  submitLabel: string;
  busy: boolean;
}) {
  const [email, setEmail] = useState(DEMO_EMAIL);
  const [password, setPassword] = useState(DEMO_PASSWORD);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    await onSubmit(email, password);
  }

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
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
        placeholder="Contraseña"
        required
      />
      <button type="submit" disabled={busy || !email.trim() || !password}>
        {busy ? "…" : submitLabel}
      </button>
    </form>
  );
}

// ── ResultBox: muestra el resultado de la última request ──────────────────

export function ResultBox({ result }: { result: ApiResult<unknown> | null }) {
  if (!result) return null;
  if (!result.ok) {
    return (
      <div className="result error">
        <strong>{result.status > 0 ? `HTTP ${result.status}` : "Error de red"}</strong>
        <span>{result.detail}</span>
        {result.retryAfter && <em>Retry-After: {result.retryAfter}s</em>}
      </div>
    );
  }
  return (
    <details className="result ok" open={false}>
      <summary>{result.status > 0 ? `HTTP ${result.status}` : "OK"}</summary>
      <pre>{JSON.stringify(result.data, null, 2)}</pre>
    </details>
  );
}

// ── ProfileCard: muestra "quién sos" para un método ────────────────────────

export function ProfileCard({ user }: { user: UserRead | null }) {
  if (!user) {
    return (
      <div className="profile empty">
        <p>Sin perfil cargado.</p>
      </div>
    );
  }
  return (
    <div className="profile">
      <p className="label">Email</p>
      <p className="value">{user.email}</p>
      <p className="label">Nombre</p>
      <p className="value">{user.name}</p>
      <p className="label">Registrado el</p>
      <p className="value">{new Date(user.created_at).toLocaleString("es-AR")}</p>
    </div>
  );
}

// ── PanelShell: encabezado uniforme (título + lección) ─────────────────────

export function PanelShell({
  numero,
  titulo,
  leccion,
  children,
}: {
  numero: string;
  titulo: string;
  leccion: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <section className="panel">
      <header className="panel-header">
        <span className="panel-num">{numero}</span>
        <h2>{titulo}</h2>
      </header>
      <p className="lesson">{leccion}</p>
      {children}
    </section>
  );
}