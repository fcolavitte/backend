import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// ¿A dónde apunta el proxy /api?
//  - Sin docker (dev local): VITE_PROXY_TARGET sin definir → 127.0.0.1:8000.
//  - Con docker compose: la env var la define docker-compose.yml →
//    http://backend:8000 (el nombre del service en la red de Compose).
const PROXY_TARGET = process.env.VITE_PROXY_TARGET ?? "http://127.0.0.1:8000";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // En desarrollo, /api/* va al backend FastAPI del módulo 06. Mismo
    // patrón del módulo 05: el proxy de Vite une front y backend en el
    // MISMO origen → no hace falta CORS y el header `Authorization:
    // Bearer <jwt>` viaja sin fricción.
    //
    // En producción esto sería el gateway / mismo dominio. El punto: el
    // navegador siempre cree que habla con localhost:5173.
    proxy: {
      "/api": {
        target: PROXY_TARGET,
        changeOrigin: true,
      },
    },
  },
});