from fastapi import FastAPI, Request
from jose import JWTError, jwt
from dotenv import load_dotenv
from src.logger import logger
from src.utils import decode_access_token

import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY") # Cambia esto a un valor seguro
ALGORITHM = os.getenv("ALGORITHM")

async def log_requests(request: Request, call_next):
    log_dict = {
        "method": request.method,
        "url": request.url,
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
        "body": await request.body(),
    }
    # Agregar condicional, si hay usuario logueado y get_current_user(request) != None
    authorization: str = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        try:
            # Decodificar el token para obtener la información del usuario
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            log_dict["user"] = f"User ID: {payload.get('id')}, Email: {payload.get('email')}"
        except jwt.ExpiredSignatureError:
            # Si el token ha expirado, se registra y se marca el usuario como desconocido
            logger.warning("Token expirado")
            log_dict["user"] = "Expired token"
        except JWTError as e:
            # Si ocurre un error al decodificar, se registra y se marca el usuario como desconocido
            logger.warning(f"Error decodificando token: {e}")
            log_dict["user"] = "Invalid token"
    else:
        # Si no hay token, se asume que es una solicitud de un usuario anónimo
        log_dict["user"] = "Anonymous"
    
    logger.info(log_dict, extra=log_dict)
    response = await call_next(request)
    return response
