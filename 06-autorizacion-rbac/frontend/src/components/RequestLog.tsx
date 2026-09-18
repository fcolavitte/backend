import type { LogEntry } from "../types";

interface Props {
  entries: LogEntry[];
}

/**
 * Consola didáctica — cada request con su status.
 *
 * Mirá los colores:
 *   🟢 2xx → el server te dejó pasar
 *   🟠 4xx → rechazado (401 no autenticado, 403 sin permiso, 404 no existe)
 *
 * Acá es donde se hace VISIBLE la autorización: si un request que
 * debería fallar con 403 aparece en verde (200), tu backend tiene un
 * bug de access control. Los mismos colores que la terminal del script
 * de verificación.
 */

function methodClass(method: string): string {
  switch (method) {
    case "GET":
      return "m-get";
    case "POST":
      return "m-post";
    case "PATCH":
      return "m-patch";
    case "DELETE":
      return "m-delete";
    default:
      return "";
  }
}

function statusClass(status: number | null): string {
  if (status === null) return "s-pending";
  if (status < 300) return "s-ok";
  if (status < 500) return "s-client";
  return "s-server";
}

export default function RequestLog({ entries }: Props) {
  return (
    <div className="request-log">
      <h3>Consola de requests</h3>
      {entries.length === 0 ? (
        <p className="empty">Aún no hay requests — hacé un login o una acción para que aparezcan.</p>
      ) : (
        <div className="log-scroll">
          {entries.map((e) => (
            <div key={e.id} className="log-line">
              <span className={`log-method ${methodClass(e.method)}`}>{e.method}</span>
              <span className="log-url">{e.url}</span>
              <span className={`log-status ${statusClass(e.status)}`}>
                {e.status ?? "..."}
              </span>
              <span className="log-label">{e.label}</span>
              {e.detail && <span className="log-detail">{e.detail}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}