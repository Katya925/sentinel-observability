# ============================================================
# PROYECTO SENTINEL
# FASE II - BACKEND CON FASTAPI
# Detección de fraude en reclamaciones de seguros
# ============================================================

import json
import joblib
import pandas as pd
import time
import uuid
import os
import asyncio

from tracing_config import configurar_tracing

from logging_config import configurar_logging

from fastapi import Request
from fastapi.responses import Response

from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST
)


from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


# ============================================================
# 1. CONFIGURACIÓN DE RUTAS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "sentinel_pipeline.joblib"
METADATA_PATH = BASE_DIR / "sentinel_metadata.json"


# ============================================================
# 2. CARGA DEL MODELO Y METADATOS
# ============================================================

modelo = None
metadata = None


@asynccontextmanager
async def lifespan(app: FastAPI):

    global modelo, metadata

    # Cargar metadatos
    with open(
        METADATA_PATH,
        "r",
        encoding="utf-8"
    ) as archivo:

        metadata = json.load(archivo)

    # Cargar modelo entrenado
    # Solo cargar archivos generados por fuentes confiables
    modelo = joblib.load(MODEL_PATH)

    print("Modelo Sentinel cargado correctamente.")

    yield


# ============================================================
# 3. CREACIÓN DE LA API
# ============================================================

app = FastAPI(
    title="Sentinel API",
    description=(
        "API educativa para detección de posibles "
        "fraudes en reclamaciones de seguros."
    ),
    version="1.0.0",
    lifespan=lifespan
)


# ============================================================
# SENTINEL OBSERVABILITY - INICIALIZACIÓN DE TRAZAS
# ============================================================
tracer = configurar_tracing(app)



# ============================================================
# SENTINEL OBSERVABILITY - LOGGER
# ============================================================

logger = configurar_logging()



# ============================================================
# SENTINEL OBSERVABILITY - MÉTRICAS PROMETHEUS
# ============================================================

HTTP_REQUESTS = Counter(
    "sentinel_http_requests_total",
    "Total de solicitudes HTTP",
    ["method", "endpoint", "status"]
)

HTTP_LATENCY = Histogram(
    "sentinel_http_request_duration_seconds",
    "Duración de solicitudes HTTP en segundos",
    ["method", "endpoint"],
    buckets=(
        0.01, 0.025, 0.05, 0.1, 0.25,
        0.5, 1, 2.5, 5, 10
    )
)

PREDICTIONS = Counter(
    "sentinel_predictions_total",
    "Total de predicciones realizadas"
)

FRAUD_ALERTS = Counter(
    "sentinel_fraud_alerts_total",
    "Total de alertas de fraude generadas"
)

PREDICTION_ERRORS = Counter(
    "sentinel_prediction_errors_total",
    "Total de errores de inferencia"
)


# ============================================================
# MÉTRICAS PROMETHEUS + LOGS ESTRUCTURADOS
# ============================================================

@app.middleware("http")
async def monitorizar_http(request: Request, call_next):

    inicio = time.perf_counter()

    # ========================================================
    # SIMULACIÓN INC-002 - LATENCIA CONTROLADA
    # ========================================================
    if request.url.path == "/predict":

        retraso = float (
            os.getenv("SENTINEL_SIMULATE_LATENCY_SECONDS", "0")            
        )

        if retraso > 0:
            await asyncio.sleep(retraso)

    
    # Identificador único para correlacionar solicitudes
    request_id = str(uuid.uuid4())

    # Valor inicial para errores no controlados
    status_code = 500

    # Obtener ruta sin generar etiquetas dinámicas
    ruta = request.scope.get("route")

    endpoint = (
        ruta.path
        if ruta is not None
        else request.url.path
    )

    try:

        response = await call_next(request)

        status_code = response.status_code

        # Devolver identificador al cliente
        response.headers["X-Request-ID"] = request_id

        return response

    except Exception:

        # Registrar el error sin exponer datos personales
        logger.exception(
            "http_request_exception",
            extra={
                "request_id": request_id,
                "method": request.method,
                "endpoint": endpoint,
                "status_code": 500
            }
        )

        raise

    finally:

        duracion = time.perf_counter() - inicio

        # Registrar métricas Prometheus
        HTTP_LATENCY.labels(
            method=request.method,
            endpoint=endpoint
        ).observe(duracion)

        HTTP_REQUESTS.labels(
            method=request.method,
            endpoint=endpoint,
            status=str(status_code)
        ).inc()

        # Registrar evento estructurado
        logger.info(
            "http_request_completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "endpoint": endpoint,
                "status_code": status_code,
                "duration_ms": round(
                    duracion * 1000,
                    2
                )
            }
        )


# ============================================================
# 4. MODELO DE DATOS DE ENTRADA
# ============================================================

class Reclamacion(BaseModel):

    datos: dict[str, str | int | float | bool] = Field(
        description="Variables de la reclamación"
    )


# ============================================================
# 5. ENDPOINT DE SALUD
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "ok",
        "modelo_cargado": modelo is not None,
        "proyecto": "Sentinel"
    }


# ============================================================
# 6. CONSULTAR VARIABLES DEL MODELO
# ============================================================

@app.get("/features")
def features():

    return {
        "modelo": metadata["modelo"],
        "variables": metadata["variables_entrada"],
        "total_variables": len(
            metadata["variables_entrada"]
        )
    }


# ============================================================
# 7. ENDPOINT DE PREDICCIÓN
# ============================================================

@app.post("/predict")
def predict(reclamacion: Reclamacion):

    try:

        # Obtener las variables requeridas
        variables = metadata["variables_entrada"]

        # Verificar que no falten variables
        faltantes = [
            variable
            for variable in variables
            if variable not in reclamacion.datos
        ]

        if faltantes:

            raise HTTPException(
                status_code=422,
                detail={
                    "mensaje": "Faltan variables requeridas",
                    "variables_faltantes": faltantes
                }
            )

        # Construir DataFrame con el orden correcto
        datos = pd.DataFrame(
            [reclamacion.datos]
        )

        datos = datos[variables]

        # Obtener probabilidad de fraude
        probabilidad = float(
            modelo.predict_proba(datos)[0, 1]
        )

        # Recuperar umbral
        umbral = float(
            metadata["umbral_alerta"]
        )

        # Determinar si corresponde generar alerta
        alerta = probabilidad >= umbral

        # Registrar inferencia exitosa
        PREDICTIONS.inc()

        # Registrar alerta de fraude
        if alerta:
            FRAUD_ALERTS.inc()

        # Devolver resultado
        return {
            "probabilidad_fraude": round(
                probabilidad, 4
            ),
            "umbral_alerta": umbral,
            "alerta": bool(alerta),
            "clasificacion": (
                "Revision requerida"
                if alerta
                else "Sin alerta de alto riesgo"
            ),
            "requiere_revision_humana": True,
            "apto_para_produccion": False
        }

    except HTTPException:
        raise

    except (ValueError, TypeError, KeyError) as error:
        PREDICTION_ERRORS.inc()
        raise HTTPException(
            status_code=422,
            detail="Los datos de la reclamación no son válidos."
        ) from error


# ============================================================
# ENDPOINT DE MÉTRICAS PROMETHEUS
# ============================================================

@app.get("/metrics", include_in_schema=False)
def metrics():

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )