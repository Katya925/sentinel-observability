
# ============================================================
# SENTINEL OBSERVABILITY
# FASE 6 - PREPARACIÓN DE DATOS DE REFERENCIA
# ============================================================

from pathlib import Path

import kagglehub
import pandas as pd


# ============================================================
# CONFIGURACIÓN
# ============================================================

DATASET = "shivamb/vehicle-claim-fraud-detection"

BASE_DIR = Path(__file__).resolve().parents[1]

REFERENCE_DIR = BASE_DIR / "data" / "reference"

REFERENCE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# DESCARGA DEL DATASET
# ============================================================

print("Descargando dataset de Sentinel...")

dataset_path = Path(
    kagglehub.dataset_download(DATASET)
)

print(f"Ruta del dataset: {dataset_path}")


# ============================================================
# LOCALIZACIÓN DEL ARCHIVO
# ============================================================

archivos = list(
    dataset_path.rglob("*.csv")
)

if not archivos:
    raise FileNotFoundError(
        "No se encontraron archivos CSV en el dataset."
    )

print("\nArchivos CSV encontrados:")

for archivo in archivos:
    print(f" - {archivo.name}")

if len(archivos) != 1:
    raise RuntimeError(
        "Se encontraron varios CSV. "
        "Es necesario seleccionar el archivo correcto."
    )

csv_path = archivos[0]


# ============================================================
# CARGA DE DATOS
# ============================================================

df = pd.read_csv(csv_path)

print("\nDimensiones del dataset:")
print(df.shape)

print("\nColumnas disponibles:")
print(df.columns.tolist())


# ============================================================
# VERIFICACIÓN DE VARIABLE OBJETIVO
# ============================================================

TARGET = "FraudFound_P"

if TARGET not in df.columns:
    raise ValueError(
        f"No se encontró la variable objetivo {TARGET}"
    )


# ============================================================
# PREPARACIÓN DE VARIABLES
# ============================================================

# Eliminar únicamente la variable objetivo.
# La selección definitiva de variables deberá coincidir
# con las 32 utilizadas por el pipeline Sentinel.

X = df.drop(columns=[TARGET])

print("\nNúmero de variables disponibles:")
print(X.shape[1])


# ============================================================
# EXPORTACIÓN DE REFERENCIA PRELIMINAR
# ============================================================

output_path = (
    REFERENCE_DIR / "sentinel_reference_preliminar.csv"
)

X.to_csv(
    output_path,
    index=False
)

print("\nArchivo de referencia preliminar creado:")
print(output_path)

print("\nPreparación inicial completada.")
