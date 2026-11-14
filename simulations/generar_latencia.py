# ============================================================
# SENTINEL OBSERVABILITY
# INC-002 - GENERADOR DE TRÁFICO CONTROLADO
# ============================================================

import json
import time
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

EJEMPLO = BASE_DIR / "tests" / "ejemplo_reclamacion.json"

URL = "http://127.0.0.1:8000/predict"

with open(EJEMPLO, encoding="utf-8") as archivo:
    reclamacion = json.load(archivo)

print("Iniciando simulación INC-002")

# 180 solicitudes, una cada 2 segundos aproximadamente.
# El tiempo total incluye la latencia de cada solicitud.
for numero in range(1, 181):

    datos = json.dumps(reclamacion).encode("utf-8")

    solicitud = urllib.request.Request(
        URL,
        data=datos,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    inicio = time.perf_counter()

    try:
        with urllib.request.urlopen(
            solicitud,
            timeout=15
        ) as respuesta:

            codigo = respuesta.status

    except Exception as error:
        codigo = f"ERROR: {error}"

    duracion = time.perf_counter() - inicio

    print(
        f"Solicitud {numero}/180 | "
        f"Estado: {codigo} | "
        f"Latencia: {duracion:.2f}s",
        flush=True
    )

    time.sleep(2)

print("Simulación INC-002 finalizada")