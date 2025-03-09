from fastapi import FastAPI
from src.routes.user_routes import user_router
from src.routes.seed_routers import seed_router
from src.db.database import Base, engine, init_db
from fastapi.middleware.cors import CORSMiddleware

# Inicializar la base de datos
init_db()

app = FastAPI()
app.title = "RePA IAViM - 2025"
app.version = "0.1.0"

origin = ['*'] # URL permitidas para consumir la API

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
    )

# Incluir rutas a módulos
app.include_router(user_router, prefix="/users", tags=["Users"])

# Datos iniciales
app.include_router(seed_router, prefix="/seed", tags=["Seed Data"]) # Carga inicial de datos

@app.get("/")
def root():
    return {"message": "API de Gestión de Usuarios funcionando correctamente"}
