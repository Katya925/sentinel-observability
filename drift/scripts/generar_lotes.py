# ============================================================
# SENTINEL OBSERVABILITY
# FASE 6 - GENERACIÓN DE LOTES PARA DATA DRIFT
# ============================================================

from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURACIÓN
# ============================================================

SEED = 42
N_REGISTROS = 1000

rng = np.random.default_rng(SEED)

BASE_DIR = Path(__file__).resolve().parents[1]

REFERENCE_PATH = (
    BASE_DIR / "data" / "reference" / "sentinel_reference.csv"
)

CURRENT_DIR = BASE_DIR / "data" / "current"

CURRENT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CARGAR DATOS DE REFERENCIA
# ============================================================

df = pd.read_csv(REFERENCE_PATH)

if len(df) < N_REGISTROS:
    raise ValueError(
        "La referencia no contiene suficientes registros."
    )


# ============================================================
# LOTE 1 - CONTROL
# ============================================================

control = df.sample(
    n=N_REGISTROS,
    random_state=SEED
).copy()

control.to_csv(
    CURRENT_DIR / "sentinel_control.csv",
    index=False
)


# ============================================================
# LOTE 2 - DATA DRIFT SIMULADO
# ============================================================

drift = df.sample(
    n=N_REGISTROS,
    random_state=SEED + 1
).copy()


# ------------------------------------------------------------
# CAMBIO 1 - DISTRIBUCIÓN DE EDAD
# ------------------------------------------------------------

# Incrementar la edad en registros numéricos válidos
edades = pd.to_numeric(
    drift["Age"],
    errors="coerce"
)

mask = edades.notna() & (edades > 0)

drift.loc[mask, "Age"] = (
    edades.loc[mask] + 15
).clip(upper=90)


# ------------------------------------------------------------
# CAMBIO 2 - ÁREA DEL ACCIDENTE
# ------------------------------------------------------------

# Incrementar la proporción de accidentes urbanos
drift["AccidentArea"] = rng.choice(
    ["Urban", "Rural"],
    size=len(drift),
    p=[0.95, 0.05]
)


# ------------------------------------------------------------
# CAMBIO 3 - FABRICANTE DEL VEHÍCULO
# ------------------------------------------------------------

# Concentrar una mayor proporción en una categoría existente
marcas = drift["Make"].dropna()

if marcas.empty:
    raise ValueError(
        "No existen marcas válidas en la referencia."
    )

marca_frecuente = marcas.mode().iloc[0]

mask_marcas = rng.random(len(drift)) < 0.70

drift.loc[mask_marcas, "Make"] = marca_frecuente


# ============================================================
# EXPORTAR LOTE CON DRIFT
# ============================================================

drift.to_csv(
    CURRENT_DIR / "sentinel_drift.csv",
    index=False
)


# ============================================================
# RESUMEN
# ============================================================

print("\nLotes generados correctamente.")

print("Control:", control.shape)
print("Drift:", drift.shape)

print("\nEdad media:")

print(
    "Control:",
    pd.to_numeric(
        control["Age"],
        errors="coerce"
    ).mean()
)

print(
    "Drift:",
    pd.to_numeric(
        drift["Age"],
        errors="coerce"
    ).mean()
)

print("\nDistribución AccidentArea - Control:")
print(control["AccidentArea"].value_counts(normalize=True))

print("\nDistribución AccidentArea - Drift:")
print(drift["AccidentArea"].value_counts(normalize=True))

print("\nProceso completado.")
