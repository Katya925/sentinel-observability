
# ============================================================
# SENTINEL OBSERVABILITY
# FASE 6 - ANÁLISIS DE DATA DRIFT CON EVIDENTLY
# ============================================================

from pathlib import Path
import json

import pandas as pd

from evidently import Report, Dataset, DataDefinition
from evidently.presets import DataDriftPreset


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

REFERENCE_PATH = (
    BASE_DIR / "data" / "reference" / "sentinel_reference.csv"
)

CURRENT_DIR = BASE_DIR / "data" / "current"

REPORTS_DIR = BASE_DIR / "reports"

REPORTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CARGA DE DATOS
# ============================================================

reference = pd.read_csv(REFERENCE_PATH)

control = pd.read_csv(
    CURRENT_DIR / "sentinel_control.csv"
)

drift = pd.read_csv(
    CURRENT_DIR / "sentinel_drift.csv"
)


# ============================================================
# EXCLUSIÓN DE IDENTIFICADORES DEL ANÁLISIS DE DRIFT
# ============================================================

COLUMNAS_EXCLUIDAS = ["PolicyNumber"]

for columna in COLUMNAS_EXCLUIDAS:
    if columna not in reference.columns:
        raise ValueError(
            f"No se encontró la columna {columna}"
        )

reference = reference.drop(columns=COLUMNAS_EXCLUIDAS)
control = control.drop(columns=COLUMNAS_EXCLUIDAS)
drift = drift.drop(columns=COLUMNAS_EXCLUIDAS)

print("Variables analizadas:", len(reference.columns))
print("Variables excluidas:", COLUMNAS_EXCLUIDAS)



if list(reference.columns) != list(control.columns):
    raise ValueError(
        "Las columnas del control no coinciden con la referencia."
    )

if list(reference.columns) != list(drift.columns):
    raise ValueError(
        "Las columnas del lote drift no coinciden con la referencia."
    )


# ============================================================
# DEFINICIÓN DE TIPOS
# ============================================================

# Age es numérica.
# El resto de las variables se tratan inicialmente
# como categóricas, según el dataset de Sentinel.

numerical_columns = ["Age"]

categorical_columns = [
    col for col in reference.columns
    if col not in numerical_columns
]

data_definition = DataDefinition(
    numerical_columns=numerical_columns,
    categorical_columns=categorical_columns
)


# ============================================================
# PREPARAR DATASETS EVIDENTLY
# ============================================================

reference_dataset = Dataset.from_pandas(
    reference,
    data_definition=data_definition
)


# ============================================================
# FUNCIÓN DE ANÁLISIS
# ============================================================

def analizar_lote(nombre, current_df):

    print(f"\nAnalizando escenario: {nombre}")

    current_dataset = Dataset.from_pandas(
        current_df,
        data_definition=data_definition
    )

    report = Report(
        metrics=[
            DataDriftPreset()
        ]
    )

    snapshot = report.run(
        reference_data=reference_dataset,
        current_data=current_dataset
    )

    # Guardar reporte visual
    html_path = REPORTS_DIR / f"{nombre}_drift.html"

    snapshot.save_html(
        str(html_path)
    )

    # Guardar resultados estructurados
    json_path = REPORTS_DIR / f"{nombre}_drift.json"

    snapshot.save_json(
        str(json_path)
    )

    print("Reporte HTML:", html_path)
    print("Reporte JSON:", json_path)

    return snapshot


# ============================================================
# EJECUCIÓN DE ESCENARIOS
# ============================================================

analizar_lote(
    "control",
    control
)

analizar_lote(
    "simulated",
    drift
)

print("\nAnálisis de Data Drift completado.")
