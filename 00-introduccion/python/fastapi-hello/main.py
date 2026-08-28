"""
Módulo principal de la API Hola Mundo con FastAPI.

FastAPI es un framework web moderno y rápido (de alto rendimiento)
para construir APIs con Python 3.8+ basado en type hints estándar.

Características clave que se demuestran aquí:
  - Type hints como ciudadanos de primera clase
  - Documentación automática e interactiva (OpenAPI / Swagger)
  - Validación automática de parámetros con Pydantic
  - Async nativo
  - Inyección de dependencias

Para ejecutar:
    $ uvicorn main:app --reload --port 8000

Documentación interactiva (una vez ejecutando):
    - Swagger UI: http://localhost:8000/docs
    - ReDoc:     http://localhost:8000/redoc
"""

from fastapi import FastAPI
import logging

VERSION = "0.1.0"


# ---------------------------------------------------------------------------
# Configuración del logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Instancia de la aplicación
# ---------------------------------------------------------------------------
# FastAPI() recibe parámetros de configuración que se reflejan en la
# documentación automática. El tipo `app` se infiere como `FastAPI`.
app = FastAPI(
    title="Hola Mundo - FastAPI",
    description="API de ejemplo para el curso de Desarrollo Web - Backend",
    version=VERSION,
    # Los docs se sirven en /docs por defecto, se puede personalizar:
    # docs_url="/api/docs",
)


# ---------------------------------------------------------------------------
# Endpoint raíz
# ---------------------------------------------------------------------------
# El decorador `@app.get("/")` asocia esta función a una petición GET en "/".
# FastAPI infiere automáticamente:
#   - El método HTTP del decorador
#   - El tipo de retorno (dict → JSON)
#   - El schema OpenAPI a partir del type hint de retorno
@app.get("/")
def read_root(name: str = "default"):
    """
    Endpoint raíz.
    Retorna un mensaje de bienvenida.

    Demuestra:
    - Decorador de ruta más simple posible
    - Inferencia automática de tipo de respuesta (dict → JSON)
    - Documentación automática generada desde el docstring y los tipos
    """
    logger.info(f"Petición recibida en / con name={name}")
    if name != "default":
        return {"message": f"¡Hola, {name}!"}
    else:
        return {"message": "¡Hola, mundo desde FastAPI!"}


# ---------------------------------------------------------------------------
# Endpoint de salud
# ---------------------------------------------------------------------------
# Los endpoints de health check son un estándar en APIs productivas.
# Permiten a balanceadores de carga, orquestadores y monitores
# verificar que la aplicación está viva y respondiendo.
@app.get("/health")
def health_check():
    """
    Health check de la API.
    Retorna el estado del servicio.

    Es una buena práctica separar los endpoints de monitoreo
    de los endpoints de negocio.
    """
    logger.info("Petición recibida en /health")
    return {"status": "ok", "service": "fastapi-hello"}



# ---------------------------------------------------------------------------
# Endpoint de version
# ---------------------------------------------------------------------------
@app.get("/version")
def version_check():
    return {"message": VERSION}