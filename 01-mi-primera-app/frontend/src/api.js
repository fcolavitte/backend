/**
 * api.js — Servicio de comunicación con el Backend
 * ==================================================
 *
 * Este archivo encapsula TODA la comunicación con la API.
 * El componente App.jsx NUNCA hace fetch directamente —
 * siempre pasa por acá.
 *
 * POR QUÉ separar esto:
 *   1. Si cambia la URL base, se cambia en UN solo lugar
 *   2. Si necesitás agregar headers (auth), se agrega acá
 *   3. El componente se queda limpio, solo con lógica de UI
 *
 * Nota: Usamos rutas relativas (/api/tasks) porque el proxy
 * de Vite las redirige al backend. En producción, acá iría
 * la URL completa (https://api.miserver.com/api/tasks).
 */

const API_BASE = "/api";

/**
 * Helper genérico para hacer fetch con manejo de errores.
 * Si el servidor responde con error (4xx, 5xx), lanza una
 * excepción con el mensaje del backend.
 */
async function request(url, options = {}) {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `Error ${response.status}`);
  }

  // DELETE devuelve { ok: true } — no intentamos parsear como JSON
  // si el status es 204 No Content
  if (response.status === 204) return null;

  return response.json();
}

/**
 * GET /api/tasks → Devuelve la lista de tareas
 */
export async function fetchTasks() {
  return request("/tasks");
}

/**
 * POST /api/tasks → Crea una tarea nueva
 * @param {string} title - Título de la tarea
 */
export async function createTask(title) {
  return request("/tasks", {
    method: "POST",
    body: JSON.stringify({ "title": title, "priority": 0 }),
  });
}

/**
 * PATCH /api/tasks/{id} → Cambia completed ↔ !completed
 * @param {number} id - ID de la tarea
 */
export async function toggleTask(id) {
  return request(`/tasks/${id}`, {
    method: "PATCH",
  });
}

/**
 * DELETE /api/tasks/{id} → Elimina una tarea
 * @param {number} id - ID de la tarea
 */
export async function deleteTask(id) {
  return request(`/tasks/${id}`, {
    method: "DELETE",
  });
}
