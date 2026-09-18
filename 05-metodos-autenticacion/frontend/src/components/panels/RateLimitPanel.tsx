import { useState } from "react";
import { sessionLogin } from "../../api";
import type { ApiResult, Token } from "../../types";
import { PanelShell, ResultBox } from "./shared";

/**
 * Panel extra — RATE LIMITING (el 429).
 *
 * El backend cuenta intentos fallidos POR EMAIL: 5 fallos en 15 minutos →
 * HTTP 429 Too Many Requests + header Retry-After. Cualquier método con
 * login lo usa (passa por verify_login en el backend).
 *
 * Acá lo forzamos a propósito: un email "basura" (distinto en cada corrida
 * para no contaminar el contador del usuario demo), y le erramos 6 veces
 * seguidas. El 6to intento debería devolver 429.
 *
 * Mirá también login_failures_count en el HealthBar: el contador VIVO.
 */

const FALLOS = 6;
const DELAY_BETWEEN_MS = 700;

export default function RateLimitPanel() {
  const [results, setResults] = useState<(ApiResult<Token> & { intento: number })[]>([]);
  const [running, setRunning] = useState(false);
  const [email] = useState(() => `spam-${Date.now()}@ejemplo.com`);

  async function run() {
    setRunning(true);
    setResults([]);
    // 11 carácteres: password inválido seguro (mínimo 8 ok, pero el email
    // no existe → authenticate_user devuelve None → 401).
    for (let intento = 1; intento <= FALLOS; intento++) {
      const res = await sessionLogin(email, "password-invalida");
      setResults((prev) => [...prev, { ...res, intento }]);
      if (intento < FALLOS) {
        await new Promise((resolve) => setTimeout(resolve, DELAY_BETWEEN_MS));
      }
    }
    setRunning(false);
  }

  return (
    <PanelShell
      numero="8"
      titulo="Rate limiting (el 429)"
      leccion={
        <>
          El backend permite <strong>5 fallos por email en 15 minutos</strong>.
          Este panel fuerza 6 fallos seguidos con un email basura (nuevo en
          cada corrida, para no pisar al usuario demo). El intento 6 debería
          devolver <strong>429</strong> con <code>Retry-After</code>. Fijate
          también el contador <strong>fallos de login</strong> en el HealthBar.
        </>
      }
    >
      <p className="rate-email">
        Probando contra email basura: <code>{email}</code>
      </p>

      <button onClick={run} disabled={running}>
        {running ? "Disparando fallos…" : `Disparar ${FALLOS} logins fallidos seguidos`}
      </button>

      {results.length > 0 && (
        <ul className="rate-results">
          {results.map((res) => (
            <li key={res.intento} className={`rate-intent ${res.status === 429 ? "blocked" : ""}`}>
              <span className="rate-num">Intento #{res.intento}</span>
              <span className="rate-status">
                {res.status === 429 ? "🚫 429 Too Many Requests" : `HTTP ${res.status}`}
              </span>
              <span className="rate-detail">
                {res.status === 429
                  ? `Bloqueado — ${res.detail} (Retry-After: ${res.retryAfter}s)`
                  : res.detail ?? "OK"}
              </span>
            </li>
          ))}
        </ul>
      )}

      {results.some((res) => res.status === 429) && (
        <ResultBox
          result={{
            ok: false,
            status: 429,
            data: null,
            detail:
              "El email quedó bloqueado 15 minutos. El login exitoso resetea el contador (en un email REAL). Esto es lo que frena el brute force.",
          }}
        />
      )}
    </PanelShell>
  );
}