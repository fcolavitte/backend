import { useEffect, useState } from "react";
import { health } from "../api";
import type { Health } from "../types";

/**
 * Contadores del server en vivo (polling cada 3s). El seed vive en
 * memoria (app/storage.py) y vuelve a cero al reiniciar el backend.
 */
export default function HealthBar() {
  const [healthState, setHealthState] = useState<Health | null>(null);

  useEffect(() => {
    const tick = () => {
      void health().then((res) => {
        if (res.ok && res.data) setHealthState(res.data);
      });
    };
    tick();
    const id = setInterval(tick, 3000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="healthbar">
      <span className={healthState ? "health-dot ok" : "health-dot"} />
      <span>
        {healthState ? healthState.status : "Conectando al backend en :8000…"}
      </span>
      {healthState && (
        <span className="health-stats">
          <span className="pill">{healthState.users_count} usuarios</span>
          <span className="pill">{healthState.documents_count} documentos</span>
          <span className="pill">{healthState.tenants_count} empresas</span>
        </span>
      )}
    </div>
  );
}