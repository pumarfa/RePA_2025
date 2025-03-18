import os
import logging
from fastapi import FastAPI, Request, HTTPException, status
from typing import Callable
from jose import JWTError
from src.utils import decode_access_token  # Asegúrate de importar la función de decodificación

# Crear el directorio de logs si no existe
log_directory = "src/logs"
os.makedirs(log_directory, exist_ok=True)

# Configurar el archivo de log
log_file_path = os.path.join(log_directory, "app.log")

# Configurar el formato del log
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Configurar el nivel de log y el manejador de archivo
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()  # Opcional: para imprimir logs en la consola
    ]
)

# Obtener el logger
logger = logging.getLogger(__name__)

class LoggingMiddleware:
    def __init__(self, app: FastAPI):
        self.app = app

    async def __call__(self, request: Request, call_next: Callable):
        # Extraer el token del encabezado "Authorization"
        authorization: str = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            try:
                # Decodificar el token para obtener la información del usuario
                payload = decode_access_token(token)
                user_info = f"User ID: {payload.get('id')}, Email: {payload.get('email')}"
            except JWTError as e:
                # Si ocurre un error al decodificar, se registra y se marca el usuario como desconocido
                logger.warning(f"Error decodificando token: {e}")
                user_info = "Invalid token"
        else:
            # Si no hay token, se asume que es una solicitud de un usuario anónimo
            user_info = "Anonymous"

        # Registrar la información antes de procesar la solicitud
        logger.info(f"Request: {request.method} {request.url.path} - {user_info}")

        # Procesar la solicitud y obtener la respuesta
        response = await call_next(request)

        # Registrar la información después de procesar la solicitud
        logger.info(f"Response: {response.status_code} - {user_info}")

        return response
