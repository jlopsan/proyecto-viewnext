from fastapi import FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient
from mongodb.routes import router as consultas_router
from backend.routes import router as agente_router
from contextlib import asynccontextmanager

# Cargar configuración desde el archivo .env
config = dotenv_values(".env")

# Crear la instancia de la aplicación FastAPI
app = FastAPI()

# Definir el contexto para el ciclo de vida (startup y shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lógica de inicio (startup)
    app.mongodb_client = MongoClient(config["URL"])
    app.database = app.mongodb_client[config["DB_NAME"]]
    yield  # Durante la ejecución de la aplicación
    # Lógica de cierre (shutdown)
    app.mongodb_client.close()

# Asignar el ciclo de vida personalizado a la app
app = FastAPI(lifespan=lifespan)

# Incluir routers de otros módulos
app.include_router(consultas_router, tags=["consultas"], prefix="/consulta")
app.include_router(agente_router, tags=["agente"], prefix="/agente")
