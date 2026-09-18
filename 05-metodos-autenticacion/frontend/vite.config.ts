import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // En desarrollo, /api/* va al backend FastAPI del módulo 05
    // (http://127.0.0.1:8000). El PROXY es LA pieza didáctica:
    //
    //   El navegador cree que todo es mismo-origen (localhost:5173).
    //   → Las cookies httpOnly (session, jwt-cookie) funcionan SIN CORS.
    //   → No hay problemas de cross-origin ni credentials.
    //
    // En producción esto sería el GATEWAY / mismo dominio. Esa es la
    // lección: el frontend y el backend comparten origen (o un
    // proxy/API gateway los une) para que las cookies jueguen.
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});