from fastapi import FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient
from mongodb.routes import router as consultas_router
from backend.routes import router as agente_router

config = dotenv_values(".env")

app = FastAPI()

@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(config["URL"])
    app.database = app.mongodb_client[config["DB_NAME"]]

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()

app.include_router(consultas_router, tags=["consultas"], prefix="/consulta")
app.include_router(agente_router, tags=["agente"], prefix="/agente")