import { useEffect, useState } from "react";
import { health } from "../api";
import type { Health } from "../types";

/**
 * HealthBar — la LECCIÓN VIVA del módulo.
 *
 * Polling de /api/health cada 2.5s. Mirá qué contadores cambian con cada
 * método:
 *
 *   - sessions_count   → sube SOLO con Session Based (estado en server)
 *   - api_tokens_count → sube SOLO con Token opaco (estado en server)
 *   - login_failures_count → sube con cada 401 (rate limiter contando)
 *   - users_count      → crece al entrar por SSO con un email nuevo (JIT)
 *
 * Logueate con JWT o SSO y NO cambia nada: son stateless. Ver el número
 * quieto con tus ojos es entender la diferencia stateful vs stateless.
 */

const INTERVAL_MS = 2500;

function Counter({
  label,
  value,
  title,
}: {
  label: string;
  value: number;
  title?: string;
}) {
  return (
    <span className="counter" title={title}>
      <span className="counter-label">{label}</span>
      <span className="counter-value">{value}</span>
    </span>
  );
}

export default function HealthBar() {
  const [data, setData] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function tick() {
      const res = await health();
      if (cancelled) return;
      if (res.ok && res.data) {
        setData(res.data);
        setError(null);
      } else {
        setError(res.detail ?? "server caído");
      }
    }

    tick();
    const id = setInterval(tick, INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  if (error) {
    return (
      <div className="healthbar">
        <strong>¿Está el server vivo?</strong>
        <span className="health-error">{error}</span>
        <em className="health-note">
          Arrancalo: <code>uvicorn app.main:app --port 8000</code> en{" "}
          <code>05-metodos-autenticacion/backend/</code>
        </em>
      </div>
    );
  }

  if (!data) {
    return <div className="healthbar loading">Cargando health…</div>;
  }

  return (
    <div className="healthbar">
      <Counter label="usuarios" value={data.users_count} title="Crece al registrarte o entrar por SSO con un email nuevo (JIT provisioning)" />
      <Counter label="sesiones" value={data.sessions_count} title="SOLO Session Based guarda sesiones en el server (método 2)" />
      <Counter label="tokens opacos" value={data.api_tokens_count} title="SOLO Token Auth guarda tokens en el server (método 3)" />
      <Counter label="fallos de login" value={data.login_failures_count} title="Intentos fallidos vivos en la ventana del rate limiter (5 fallos/15min → 429)" />
      <em className="health-note">{data.note}</em>
    </div>
  );
}