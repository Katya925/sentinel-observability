
# ============================================================
# SENTINEL OBSERVABILITY
# FASE 6 - CREACIÓN DE REFERENCIA PARA DATA DRIFT
# ============================================================

from pathlib import Path
import json

import kagglehub
import pandas as pd

from sklearn.model_selection import train_test_split


# ============================================================
# CONFIGURACIÓN
# ============================================================

SEED = 42
TARGET = "FraudFound_P"

BASE_DIR = Path(__file__).resolve().parents[2]

REFERENCE_DIR = BASE_DIR / "drift" / "data" / "reference"

METADATA_PATH = (
    BASE_DIR / "backend" / "sentinel_metadata.json"
)

REFERENCE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CARGAR METADATOS DEL MODELO
# ============================================================

with open(
    METADATA_PATH,
    encoding="utf-8"
) as archivo:

    metadata = json.load(archivo)

variables = metadata["variables_entrada"]

print("Variables del modelo:", len(variables))


# ============================================================
# DESCARGAR DATASET
# ============================================================

print("\nDescargando dataset original...")

dataset_path = Path(
    kagglehub.dataset_download(
        "shivamb/vehicle-claim-fraud-detection"
    )
)

archivos = list(dataset_path.rglob("*.csv"))

if len(archivos) != 1:
    raise RuntimeError(
        "Se esperaba un único archivo CSV."
    )

df = pd.read_csv(archivos[0])


# ============================================================
# VALIDAR VARIABLES
# ============================================================

if TARGET not in df.columns:
    raise ValueError(
        f"No se encontró {TARGET}"
    )

faltantes = set(variables) - set(df.columns)

if faltantes:
    raise ValueError(
        f"Variables faltantes: {faltantes}"
    )


# ============================================================
# PREPARAR X E y
# ============================================================

X = df[variables].copy()

y = df[TARGET].copy()


# ============================================================
# REPRODUCIR PARTICIÓN ORIGINAL
# ============================================================

X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.40,
    random_state=SEED,
    stratify=y
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.50,
    random_state=SEED,
    stratify=y_temp
)


# ============================================================
# VERIFICAR DIMENSIONES
# ============================================================

print("\nDistribución de datos:")

print("Entrenamiento:", X_train.shape)
print("Validación:", X_val.shape)
print("Prueba:", X_test.shape)


# ============================================================
# EXPORTAR REFERENCIA
# ============================================================

output_path = (
    REFERENCE_DIR / "sentinel_reference.csv"
)

X_train.to_csv(
    output_path,
    index=False
)

print("\nReferencia creada correctamente:")
print(output_path)

print("\nRegistros:", len(X_train))
print("Variables:", len(X_train.columns))

print("\nProceso completado.")
