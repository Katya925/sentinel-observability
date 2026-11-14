# ============================================================
# SENTINEL OBSERVABILITY
# CONFIGURACIÓN DE LOGS ESTRUCTURADOS
# ============================================================

import json
import logging
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """
    Convierte los registros de Python al formato JSON.
    """

    def format(self, record):

        # Estructura principal del registro
        log_data = {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),

            "level": record.levelname,

            "service": "sentinel-backend",

            "event": record.getMessage()
        }

        # Incorporar información adicional si existe
        campos = [
            "request_id",
            "method",
            "endpoint",
            "status_code",
            "duration_ms"
        ]

        for campo in campos:

            if hasattr(record, campo):
                log_data[campo] = getattr(
                    record,
                    campo
                )

        return json.dumps(
            log_data,
            ensure_ascii=False
        )


def configurar_logging():

    logger = logging.getLogger(
        "sentinel.observability"
    )

    logger.setLevel(logging.INFO)

    # Evitar duplicar registros
    logger.propagate = False

    if not logger.handlers:

        handler = logging.StreamHandler()

        handler.setFormatter(
            JSONFormatter()
        )

        logger.addHandler(handler)

    return logger