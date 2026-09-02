/**
 * App.jsx — Componente principal de la aplicación
 * =================================================
 *
 * Toda la UI vive en este componente. Para un taller de
 * 90 minutos, un solo componente es suficiente. En un proyecto
 * real, esto se dividiría en:
 *
 *   <TaskInput onAdd={...} />
 *   <TaskList tasks={...} onToggle={...} onDelete={...} />
 *
 * Conceptos de React que practicamos acá:
 *   - useState: estado local del componente
 *   - useEffect: efectos secundarios (fetch al montar)
 *   - JSX: sintaxis similar a HTML dentro de JavaScript
 *   - Event handling: onSubmit, onChange, onClick
 *   - Conditional rendering: mostrar cosas según condiciones
 *   - Lists: renderizar arrays con .map()
 */

import { useState, useEffect } from "react";
import { fetchTasks, createTask, toggleTask, deleteTask } from "./api";
import "./App.css";

export default function App() {
  // ---- Estado ----
  const [tasks, setTasks] = useState([]); // Lista de tareas
  const [newTitle, setNewTitle] = useState(""); // Input controlado
  const [loading, setLoading] = useState(true); // Estado de carga
  const [error, setError] = useState(null); // Mensaje de error

  // ---- Cargar tareas al montar el componente ----
  // useEffect con [] vacío = se ejecuta UNA sola vez,
  // cuando el componente se "monta" (aparece en pantalla).
  useEffect(() => {
    loadTasks();
  }, []);

  async function loadTasks() {
    try {
      setLoading(true);
      const data = await fetchTasks();
      setTasks(data);
      setError(null);
    } catch (err) {
      setError("No se pudo conectar con el backend. ¿Está corriendo en :8000?");
    } finally {
      setLoading(false);
    }
  }

  // ---- Crear tarea ----
  async function handleAdd(e) {
    e.preventDefault(); // Evita que el form recargue la página

    const title = newTitle.trim();
    if (!title) return; // No crear tareas vacías

    try {
      const task = await createTask(title);
      setTasks([...tasks, task]); // Agrego al final (inmutabilidad)
      setNewTitle(""); // Limpio el input
      setError(null);
    } catch (err) {
      setError("Error al crear la tarea");
    }
  }

  // ---- Toggle completada ----
  async function handleToggle(id) {
    try {
      const updated = await toggleTask(id);
      setTasks(
        tasks.map((t) => (t.id === id ? updated : t)) // Reemplazo solo la que cambió
      );
    } catch (err) {
      setError("Error al actualizar la tarea");
    }
  }

  // ---- Eliminar tarea ----
  async function handleDelete(id) {
    try {
      await deleteTask(id);
      setTasks(tasks.filter((t) => t.id !== id)); // Filtro la eliminada
    } catch (err) {
      setError("Error al eliminar la tarea");
    }
  }

  // ---- Render ----
  return (
    <div className="app">
      <header className="header">
        <h1>Mis Tareas</h1>
        <p className="subtitle">Mi Primera APP — FastAPI + React</p>
      </header>

      {/* Formulario para agregar tareas */}
      <form className="add-form" onSubmit={handleAdd}>
        <input
          type="text"
          className="add-input"
          placeholder="¿Qué necesitás hacer?"
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
          autoFocus
        />
        <button type="submit" className="add-button" disabled={!newTitle.trim()}>
          Agregar
        </button>
      </form>

      {/* Mensaje de error */}
      {error && (
        <div className="error">
          <span>⚠️ {error}</span>
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {/* Lista de tareas */}
      {loading ? (
        <p className="empty">Cargando tareas...</p>
      ) : tasks.length === 0 ? (
        <p className="empty">
          No hay tareas todavía. ¡Agregá una arriba!
        </p>
      ) : (
        <ul className="task-list">
          {tasks.map((task) => (
            <li key={task.id} className={`task-item ${task.completed ? "completed" : ""}`}>
              <label className="task-label">
                <input
                  type="checkbox"
                  checked={task.completed}
                  onChange={() => handleToggle(task.id)}
                />
                <span className="task-title">{task.title}</span>
                <span className="task-title">- Prioridad: {task.priority}</span>
              </label>
              <button
                className="delete-button"
                onClick={() => handleDelete(task.id)}
                title="Eliminar tarea"
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}

      {/* Contador */}
      {tasks.length > 0 && (
        <footer className="footer">
          <span>
            {tasks.filter((t) => t.completed).length} de {tasks.length} completadas
          </span>
        </footer>
      )}
    </div>
  );
}
