from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.logsapp import LoggingMiddleware
from src.database import init_db

from src.routes.user_routes import user_router
from src.routes.admin_routes import admin_router
from src.seed import seed_data

# Inicializar la base de datos
init_db()

app = FastAPI()
app.title = "Backend Frame - 2025"
app.version = "0.0.1"

origin = ['*'] # URL permitidas para consumir la API

# Agregar el middleware a la aplicación
app.middleware("http")(LoggingMiddleware(app))

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar la base de datos y ejecutar seeding
@app.on_event("startup")
def on_startup():
    init_db()  # Crear tablas si no existen
    seed_data()  # Ejecutar seeding

# Incluir rutas a módulos
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(admin_router, prefix="/admin", tags=["Administrator"])

@app.get("/")
def root():
    return {"message": "FastAPI funcionando correctamente..."}
