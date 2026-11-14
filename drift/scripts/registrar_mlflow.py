
from pathlib import Path
import mlflow

# Directorios del proyecto
BASE_DIR = Path(__file__).resolve().parents[2]
REPORTS_DIR = BASE_DIR / "drift" / "reports"
MLRUNS_DIR = BASE_DIR / "mlruns"

MLRUNS_DIR.mkdir(parents=True, exist_ok=True)

# Almacenamiento local de experimentos
mlflow.set_tracking_uri(MLRUNS_DIR.as_uri())

mlflow.set_experiment(
    "Sentinel_Observability_Data_Drift"
)

# Resultados reales obtenidos con Evidently
escenarios = [
    {
        "nombre": "control_refinado",
        "columnas_drift": 0,
        "porcentaje_drift": 0.0,
        "reporte": "control"
    },
    {
        "nombre": "simulado_refinado",
        "columnas_drift": 2,
        "porcentaje_drift": 2 / 31 * 100,
        "reporte": "simulated"
    }
]

for escenario in escenarios:

    with mlflow.start_run(
        run_name=escenario["nombre"]
    ):

        mlflow.log_param(
            "modelo",
            "Sentinel Random Forest"
        )

        mlflow.log_param(
            "registros_actuales",
            1000
        )

        mlflow.log_param(
            "columnas_analizadas",
            31
        )

        mlflow.log_param(
            "columnas_excluidas",
            "PolicyNumber"
        )

        mlflow.log_metric(
            "columnas_con_drift",
            escenario["columnas_drift"]
        )

        mlflow.log_metric(
            "porcentaje_drift",
            escenario["porcentaje_drift"]
        )

        # Registrar los reportes generados
        for extension in ["html", "json"]:

            archivo = REPORTS_DIR / (
                f"{escenario['reporte']}_drift.{extension}"
            )

            if not archivo.is_file():
                raise FileNotFoundError(archivo)

            mlflow.log_artifact(
                str(archivo),
                artifact_path="evidently_reports"
            )

        print(
            "Registrado:",
            escenario["nombre"]
        )

print("Registro MLflow completado.")
