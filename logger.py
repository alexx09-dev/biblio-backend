# logger.py
# Configuración centralizada del sistema de logging para toda la aplicación
# Importar la instancia 'logger' en cualquier módulo que necesite registrar eventos

import logging
import sys


def configurar_logger(nombre: str = "biblioteca_api") -> logging.Logger:
    """
    Crea y configura un logger con formato estructurado.
    Se llama una sola vez al iniciar la aplicación.

    El formato incluye:
    - asctime:    fecha y hora del evento
    - levelname:  nivel de severidad (INFO, ERROR, etc.)
    - name:       nombre del logger (módulo de origen)
    - message:    mensaje del evento
    """

    logger = logging.getLogger(nombre)

    # Evitar agregar handlers duplicados si el logger ya fue configurado
    if logger.handlers:
        return logger

    # ------------------------------------------------------------------
    # Nivel de logging
    # DEBUG muestra todo — ideal para desarrollo
    # En producción cambiar a logging.INFO para reducir el ruido
    # ------------------------------------------------------------------
    logger.setLevel(logging.DEBUG)

    # ------------------------------------------------------------------
    # Formato del mensaje de log
    # Ejemplo de salida:
    # 2025-01-15 10:23:45,123 | INFO     | biblioteca_api | Libro creado: id=5
    # ------------------------------------------------------------------
    formato = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ------------------------------------------------------------------
    # Handler de consola — muestra los logs en la terminal
    # StreamHandler(sys.stdout) evita mezclar logs con errores de stderr
    # ------------------------------------------------------------------
    handler_consola = logging.StreamHandler(sys.stdout)
    handler_consola.setLevel(logging.DEBUG)
    handler_consola.setFormatter(formato)

    logger.addHandler(handler_consola)

    return logger


# ---------------------------------------------------------------------------
# Instancia única del logger — lista para importar en cualquier módulo
# Uso: from logger import logger
#      logger.info("Operación completada")
#      logger.error("Algo falló")
# ---------------------------------------------------------------------------
logger = configurar_logger()