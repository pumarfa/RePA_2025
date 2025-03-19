import os
import logging
from dotenv import load_dotenv

token = 'oX6sAtRF63a5CY9XUqySWPVw'

load_dotenv()

LOGS_PATH = os.getenv("LOGS_PATH")
BETTER_STACKTRACE = os.getenv("BETTER_STACKTRACE")

# Crear el directorio de logs si no existe
log_directory = "src/logs" # reemplazar por LOGS_PATH
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
        logging.StreamHandler(),  # Opcional: para imprimir logs en la consola
    ]
)

# Obtener el logger
logger = logging.getLogger(__name__)
