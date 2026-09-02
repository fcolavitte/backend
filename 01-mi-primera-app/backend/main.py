"""
Mi Primera APP — Backend API de Tareas
======================================

API REST completa para gestionar tareas (To-Do List).
Desarrollada con FastAPI como parte del taller "Mi Primera APP".

Ejecutar:
    uv run main.py

Endpoints:
    GET    /api/tasks         → Listar todas las tareas
    POST   /api/tasks         → Crear una tarea nueva
    PATCH  /api/tasks/{id}    → Toggle completada / no completada
    DELETE /api/tasks/{id}    → Eliminar una tarea
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ============================================================
# 1. MODELOS DE DATOS (Pydantic)
# ============================================================
# Pydantic valida automáticamente que los datos que llegan
# sean del tipo correcto. Si mandás un string donde va un int,
# FastAPI devuelve un error 422 claro y descriptivo.

def str_prioridad(num: int):
    if num == 1:
        return 'media'
    if num == 2:
        return 'alta'
    return 'baja'

class TaskCreate(BaseModel):
    """Modelo para CREAR una tarea. Solo pedimos el título."""

    title: str = Field(..., min_length=1, max_length=200, examples=["Comprar leche"])
    priority: int = 0


class Task(BaseModel):
    """Modelo completo de una tarea (lo que devolvemos al frontend)."""

    id: int
    title: str
    completed: bool
    created_at: str
    priority: int = 0


# ============================================================
# 2. ALMACENAMIENTO EN MEMORIA
# ============================================================
# Para este taller NO usamos base de datos.
# Los datos viven en una lista de Python mientras el servidor
# está corriendo. Si reiniciás el servidor, se pierden.
# Esto es INTENCIONAL — el foco está en el ciclo HTTP,
# no en la persistencia.

tasks: list[dict] = []
next_id: int = 1


def find_task(task_id: int) -> Optional[dict]:
    """Busca una tarea por ID. Devuelve None si no existe."""
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


# ============================================================
# 3. APLICACIÓN FASTAPI
# ============================================================

app = FastAPI(
    title="Mi Primera APP — API de Tareas",
    description="API REST para gestionar tareas. Taller de Desarrollo de Software 2026.",
    version="0.1.0",
)

# ============================================================
# 4. CORS (Cross-Origin Resource Sharing)
# ============================================================
# CORS es un mecanismo de seguridad del navegador.
# Por defecto, un frontend en localhost:5173 NO puede hacer
# fetch a localhost:8000 — el navegador lo bloquea.
#
# En desarrollo usamos el proxy de Vite para evitar esto,
# pero configuramos CORS de todas formas porque:
#   1. Es un concepto fundamental que todo dev debe entender
#   2. Lo necesitás cuando deployás el frontend por separado
#
# En producción, acá irían solo los dominios reales.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: listar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 5. ENDPOINTS
# ============================================================


@app.get("/api/tasks", response_model=list[Task])
def list_tasks():
    """Devuelve la lista completa de tareas."""
    return tasks


@app.post("/api/tasks", response_model=Task, status_code=201)
def create_task(body: TaskCreate):
    """
    Crea una tarea nueva.

    El body debe tener:
      - "title": string no vacío (máximo 200 caracteres)

    FastAPI valida automáticamente con Pydantic.
    Si falta el title o está vacío, devuelve error 422.
    """
    global next_id

    task = {
        "id": next_id,
        "title": body.title.strip(),
        "priority": body.priority,
        "completed": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    next_id += 1
    tasks.append(task)
    return task


@app.patch("/api/tasks/{task_id}", response_model=Task)
def toggle_task(task_id: int):
    """
    Cambia el estado de una tarea (completada ↔ no completada).

    PATCH = actualización parcial. Solo modificamos el campo
    'completed', no necesitamos enviar toda la tarea.
    """
    task = find_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Tarea {task_id} no encontrada")

    task["completed"] = not task["completed"]
    return task


@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    """
    Elimina una tarea por su ID.

    Devuelve { "ok": true } si se eliminó,
    o error 404 si la tarea no existe.
    """
    task = find_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Tarea {task_id} no encontrada")

    tasks.remove(task)
    return {"ok": True}


# ============================================================
# 6. HEALTH CHECK
# ============================================================
# Un health check es un endpoint que verifica que el servicio
# está funcionando. Es estándar en cualquier API moderna.
# Los load balancers y monitores lo llaman periódicamente.


@app.get("/api/health")
def health_check():
    return {"status": "Funciona", "service": "mi-primera-app-backend", "tasks_count": len(tasks)}


# ============================================================
# 7. MAIN — Ejecutar el servidor
# ============================================================
# uvicorn es el servidor ASGI que ejecuta FastAPI.
# --reload: reinicia automáticamente al guardar cambios
# --port 8000: puerto del servidor
#
# NOTA: En producción se usa:
#   uvicorn main:app --host 0.0.0.0 --port 8000
# Sin --reload y con host 0.0.0.0 para aceptar conexiones externas.

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
