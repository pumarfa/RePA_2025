import os
import logging
from dotenv import load_dotenv
from logging.handlers import TimedRotatingFileHandler

load_dotenv()

LOGS_PATH = os.getenv("LOGS_PATH")

# Crear el directorio de logs si no existe
log_directory = "src/logs" # reemplazar por LOGS_PATH
os.makedirs(log_directory, exist_ok=True)

# Configurar el archivo de log
log_file_path = os.path.join(log_directory, "app.log")

# Configurar handler rotativo
file_handler = TimedRotatingFileHandler(
    filename=log_file_path,
    when="midnight",    # Rotación diaria a medianoche
    interval=1,         # Intervalo diario (valor por defecto)
    backupCount=5,      # Mantener 5 archivos de backup
    encoding="utf-8",   # Codificación explícita
    delay=False         # Crear archivo inmediatamente
)

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
