import { useEffect, useRef } from "react";
import type { LogEntry } from "../types";

/**
 * RequestLog — la consola didáctica del laboratorio.
 *
 * Cada request que hace el frontend queda anotada acá con su status.
 * Es como la pestaña Network del DevTools, pero con la lección al lado.
 * Probalo: hacé 5 logins fallidos seguidos y mirá aparecer el 429.
 */

const STATUS_CLASS: Record<number, string> = {
  200: "ok",
  401: "unauthorized",
  422: "unauthorized",
  429: "rate-limited",
  0: "network-error",
};

function StatusBadge({ status }: { status: number | null }) {
  if (status === null) return <span className="badge pending">…</span>;
  const cls = STATUS_CLASS[status] ?? "other";
  return <span className={`badge ${cls}`}>{status === 0 ? "RED" : status}</span>;
}

export default function RequestLog({ entries }: { entries: LogEntry[] }) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Scrollear SOLO dentro de la consola (scrollTop), nunca la página
    // entera: scrollIntoView movería todo el viewport y molestaría al
    // alumno mientras mira un panel.
    const el = containerRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [entries.length]);

  if (entries.length === 0) {
    return (
      <aside className="request-log empty">
        <h2>Consola de requests</h2>
        <p>
          Cada request que hagas desde los paneles aparece acá, con su status.
          👉 Probá hacer 5 logins fallidos seguidos para ver el <strong>429</strong>.
        </p>
      </aside>
    );
  }

  return (
    <aside className="request-log" ref={containerRef}>
      <h2>Consola de requests</h2>
      <ul className="log-entries">
        {entries.map((entry) => (
          <li key={entry.id} className="log-entry">
            <StatusBadge status={entry.status} />
            <span className="log-method">{entry.method}</span>
            <code className="log-url">{entry.url}</code>
            <span className="log-label">{entry.label}</span>
            {entry.status === 429 && <em className="log-extra">(Retry-After: 900s)</em>}
          </li>
        ))}
      </ul>
    </aside>
  );
}