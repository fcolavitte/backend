/**
 * Módulo principal de la API Hola Mundo con Fastify + Swagger.
 *
 * Fastify es un framework web para Node.js enfocado en:
 *   - Rendimiento (hasta 2x más rápido que Express)
 *   - Baja sobrecarga (overhead mínimo)
 *   - Sistema de plugins (herencia de contexto)
 *   - Validación basada en esquemas JSON (JSON Schema)
 *   - Serialización optimizada con schemas
 *   - Logger nativo (Pino)
 *
 * Para ejecutar:
 *   $ pnpm run dev       # Desarrollo con hot-reload (node --watch + tsx)
 *   $ pnpm start         # Producción
 *
 * Swagger UI:
 *   Abrir http://localhost:3000/docs en el navegador.
 */

import Fastify from "fastify";
import fastifySwagger from "@fastify/swagger";
import fastifySwaggerUi from "@fastify/swagger-ui";

// ---------------------------------------------------------------------------
// Instancia de la aplicación
// ---------------------------------------------------------------------------
// Fastify() recibe un objeto de configuración.
// El logger está habilitado: usa Pino por debajo, produce logs JSON
// estructurados ideales para producción.
const app = Fastify({
  logger: true,
});

// ===========================================================================
// Plugins (registrados ANTES que las rutas — requisito de @fastify/swagger)
// ===========================================================================

// ---------------------------------------------------------------------------
// Plugin: @fastify/swagger — Genera la especificación OpenAPI
// ---------------------------------------------------------------------------
// Escanea las rutas registradas y construye la documentación OpenAPI 3.0
// automáticamente. Si las rutas tienen definido un schema JSON, Swagger
// lo usa para documentar parámetros, bodies, responses, etc.
//
// El await es necesario para que Fastify procese el plugin antes de
// registrar las rutas. Sin await, las rutas pueden no aparecer en el spec.
await app.register(fastifySwagger, {
  openapi: {
    openapi: "3.0.3",
    info: {
      title: "Fastify Hola Mundo",
      description:
        "API de ejemplo para el curso Desarrollo Web — Backend (UTN FRLP)",
      version: "0.1.0",
    },
    servers: [
      { url: "http://localhost:3000", description: "Desarrollo" },
    ],
  },
});

// ---------------------------------------------------------------------------
// Plugin: @fastify/swagger-ui — Sirve la interfaz visual de Swagger
// ---------------------------------------------------------------------------
// Expone la documentación generada en una interfaz web interactiva.
// Swagger UI queda disponible en http://localhost:3000/docs
await app.register(fastifySwaggerUi, {
  routePrefix: "/docs",
});

// ===========================================================================
// Rutas
// ===========================================================================

// ---------------------------------------------------------------------------
// Endpoint raíz
// ---------------------------------------------------------------------------
// .get() registra una ruta GET.
// El segundo parámetro es el objeto de configuración de la ruta (opcional).
// El tercero es el handler.
//
// Acá usamos el parámetro de configuración (objeto con "schema") para
// documentar la respuesta con JSON Schema. Swagger lo va a leer y mostrar
// en la UI.
app.get(
  "/",
  {
    schema: {
      summary: "Mensaje de bienvenida",
      description: "Retorna un saludo de la API",
      response: {
        200: {
          type: "object",
          properties: {
            message: { type: "string", description: "Mensaje de saludo" },
          },
        },
      },
    },
  },
  async () => {
    /**
     * Endpoint raíz.
     * Retorna un mensaje de bienvenida.
     *
     * Demuestra:
     * - Ruta GET más simple posible
     * - Retorno de objeto (Fastify lo serializa a JSON)
     * - Schema de respuesta documentado (Swagger lo refleja)
     */
    return { message: "¡Hola, mundo desde Fastify!" };
  },
);

// ---------------------------------------------------------------------------
// Endpoint de salud
// ---------------------------------------------------------------------------
// Los health checks son un estándar en APIs productivas.
// Herramientas como Kubernetes, Docker y balanceadores de carga
// los usan para verificar disponibilidad del servicio.
app.get(
  "/health",
  {
    schema: {
      summary: "Health check",
      description: "Verifica que el servicio esté operativo",
      response: {
        200: {
          type: "object",
          properties: {
            status: { type: "string", description: "Estado del servicio" },
            service: { type: "string", description: "Nombre del servicio" },
          },
        },
      },
    },
  },
  async () => {
    /**
     * Health check de la API.
     * Retorna el estado del servicio.
     *
     * Separar monitoreo de lógica de negocio es una buena práctica
     * de arquitectura.
     */
    return { status: "ok", service: "fastify-hello" };
  },
);



// ---------------------------------------------------------------------------
// Endpoint version
// ---------------------------------------------------------------------------
app.get(
  "/version",
  {
    schema: {
      summary: "Version check",
      description: "Verifica la version del backend",
      response: {
        200: {
          type: "object",
          properties: {
            version: { type: "string", description: "Version del backend" },
          },
        },
      },
    },
  },
  async () => {
    return { version: "v0.1.0" };
  },
);


// ---------------------------------------------------------------------------
// Endpoint saludo - parámetro de ruta
// ---------------------------------------------------------------------------
app.get(
  "/saludo/:nombre",
  {
    schema: {
      summary: "Saludo",
      description: "Retorna un saludo al nombre",
      params: {
        type: "object",
        properties: {
          nombre: { type: "string", description: "Nombre de la persona" },
        },
        required: ["nombre"],
      },
      response: {
        200: {
          type: "object",
          properties: {
            message: { type: "string", description: "Un saludo" },
          },
        },
      },
    },
    preHandler: async (request, reply) => {
      console.log("Petición recibida");
    },
  },
  async (request) => {
	const { nombre } = request.params as { nombre: string };
    return { message: `¡Hola, ${nombre}!` };
  },
);


// ===========================================================================
// Inicio del servidor
// ===========================================================================
// Envolvemos en una función async porque listen() devuelve una promesa.
// Si usáramos await en el scope global, TypeScript en modo ESM lo permite,
// pero hacerlo en una función async es más explícito y portable.
const start = async (): Promise<void> => {
  try {
    const port = 3000;
    const address = await app.listen({ port });
    app.log.info(`Servidor escuchando en ${address}`);
  } catch (err) {
    // Fastify loguea el error automáticamente y terminamos el proceso
    // con código de error para que el orquestador (Docker, PM2, etc.)
    // pueda reiniciar el servicio.
    app.log.error(err);
    process.exit(1);
  }
};


start();
