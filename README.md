# Sentinel Observability
## Monitorización proactiva, mantenimiento y gobernanza operativa de un modelo de detección de fraude en seguros

**Modelo:** Random Forest  
**Entorno:** Docker Compose local  

---

## 1. Descripción del proyecto

Sentinel Observability amplía el proyecto Sentinel Fraud Detection desarrollado en Fase II, mediante una arquitectura de observabilidad moderna para supervisar un servicio de Machine Learning.

La solución integra:

- Métricas operativas con Prometheus.
- Dashboards de monitorización con Grafana.
- Logs estructurados en formato JSON.
- Trazas distribuidas mediante OpenTelemetry y Tempo.
- Detección de Data Drift con Evidently.
- Seguimiento de evaluaciones mediante MLflow.
- Alertas operativas alineadas con SLO.
- Simulación de incidentes y ejecución de runbooks.

El objetivo es detectar anomalías, facilitar el diagnóstico y demostrar procedimientos de recuperación del servicio.

El sistema se ejecuta localmente y no está aprobado para producción.

---

## 2. Relación con Sentinel Fraud Detection

Sentinel Observability continúa el proyecto original de detección de fraude en seguros.

Repositorio original:

https://github.com/Katya925/sentinel-fraud-detection

La solución conserva el modelo Random Forest, el backend FastAPI y el frontend Streamlit.

La nueva fase incorpora capacidades de monitorización, detección de anomalías y gobernanza operativa.

---

## 3. Arquitectura

```text
                  USUARIO
                     |
                     v
                STREAMLIT
                     |
                     v
                  FASTAPI
                     |
                     v
               RANDOM FOREST
                     |
              PREDICCIÓN ML
                     |
       +-------------+-------------+
       |             |             |
       v             v             v
    MÉTRICAS        LOGS         TRAZAS
       |             |             |
       v             |             v
   PROMETHEUS        |       OPENTELEMETRY
       |             |             |
       v             |             v
    GRAFANA          |           TEMPO
                     |             |
                     v             v
                 DOCKER LOGS     GRAFANA

       MONITORIZACIÓN DEL MODELO
                     |
                     v
                 EVIDENTLY
                     |
                     v
                  MLFLOW
```

La arquitectura implementada se documenta en:

[Arquitectura de observabilidad](docs/arquitectura_observabilidad.md)

---

## 4. Tecnologías

| Tecnología | Función |
|---|---|
| Python | Desarrollo y automatización |
| FastAPI | Servicio de inferencia |
| Streamlit | Interfaz de usuario |
| Random Forest | Modelo predictivo |
| Docker Compose | Orquestación local |
| Prometheus | Métricas y alertas |
| Grafana | Dashboards operativos |
| OpenTelemetry | Instrumentación de trazas |
| Tempo | Almacenamiento de trazas |
| Evidently | Detección de Data Drift |
| MLflow | Seguimiento experimental |

Los logs estructurados se consultan mediante Docker Compose.

La centralización en Loki queda como mejora futura.

---

## 5. Estructura del repositorio

```text
Sentinel-Observability/
├── backend/
│   ├── main.py
│   ├── logging_config.py
│   ├── tracing_config.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── ...
├── frontend/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── monitoring/
│   ├── prometheus/
│   │   ├── prometheus.yml
│   │   └── rules/
│   │       └── sentinel_alerts.yml
│   └── tempo/
│       └── tempo.yaml
├── drift/
│   ├── data/
│   │   ├── reference/
│   │   └── current/
│   ├── reports/
│   └── scripts/
├── simulations/
│   └── generar_latencia.py
├── runbooks/
│   ├── INC-001_backend_unavailable.md
│   └── INC-002_high_latency.md
├── docs/
│   ├── indicadores_slo.md
│   ├── arquitectura_observabilidad.md
│   ├── alertas_y_automatizacion.md
│   ├── resultados_incidentes.md
│   └── evidencias/
├── tests/
├── compose.yaml
├── .gitignore
└── README.md
```

---

## 6. Instalación y ejecución

### Requisitos

- Windows con Docker Desktop.
- Docker Compose.
- Python compatible con las dependencias del proyecto.
- Git.
- Navegador web.

### Iniciar servicios

Desde la carpeta del proyecto:

```cmd
docker compose config --quiet
docker compose up -d --build
docker compose ps
```

El archivo `.env` debe contener una contraseña local
para Grafana:

```dotenv
GRAFANA_ADMIN_PASSWORD=REEMPLAZAR_POR_CONTRASENA_LOCAL
```

No publicar `.env` en GitHub.

### Servicios locales

| Servicio | Dirección |
|---|---|
| FastAPI | http://127.0.0.1:8000/docs |
| Streamlit | http://localhost:8501 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

Tempo se consulta desde Grafana utilizando:

`http://tempo:3200`

---

## 7. Métricas operativas

FastAPI expone:

`GET /metrics`

Las métricas instrumentadas incluyen:

- `sentinel_http_requests_total`
- `sentinel_http_request_duration_seconds`
- `sentinel_predictions_total`
- `sentinel_fraud_alerts_total`
- `sentinel_prediction_errors_total`

Prometheus recopila las métricas cada 15 segundos.

### Dashboard Grafana

**Sentinel Observability — Salud y Rendimiento**

Contiene cuatro indicadores:

1. Total de predicciones.
2. Latencia p95.
3. Tráfico HTTP.
4. Tasa de errores HTTP 5xx.

La evidencia se encuentra en `docs/evidencias/`.

---

## 8. SLI, SLO y Error Budgets

| Indicador | Objetivo |
|---|---|
| Disponibilidad | >= 99% |
| Latencia | 95% de solicitudes <= 500 ms |
| Errores HTTP 5xx | < 1% |

Los objetivos son referencias técnicas del laboratorio.

Para una disponibilidad del 99% durante 30 días,
el presupuesto teórico de indisponibilidad es
de 7.2 horas.

El cálculo automatizado de consumo de error budgets
queda como ampliación pendiente.

Documento:

[Indicadores y SLO](docs/indicadores_slo.md)

---

## 9. Logs y trazas

### Logs estructurados

El backend registra eventos JSON con:

- Timestamp.
- Nivel de severidad.
- Request ID.
- Endpoint.
- Método HTTP.
- Código de respuesta.
- Duración.

Consultar:

```cmd
docker compose logs --tail=50 backend
```

### Trazas distribuidas

OpenTelemetry genera trazas de solicitudes HTTP.

Las trazas se exportan a Tempo mediante OTLP/gRPC
y se consultan desde Grafana Explore.

Se verificaron trazas del servicio `sentinel-backend`.

---

## 10. Detección de Data Drift

Se utilizó Evidently para comparar datos de referencia
con lotes simulados.

### Datos

- Dataset original: 15,420 reclamaciones.
- Referencia de entrenamiento: 9,252 registros.
- Lotes evaluados: 1,000 registros.
- Variables analizadas: 31.
- Variable excluida del análisis: PolicyNumber.

### Resultados

| Escenario | Variables con drift | Porcentaje |
|---|---:|---:|
| Control | 0 de 31 | 0% |
| Drift simulado | 2 de 31 | 6.45% |

Las variables con drift detectado fueron:

- Age.
- Make.

Estos resultados no demuestran por sí mismos
una pérdida de precisión del modelo.

### Reproducir análisis

Con un entorno Python configurado:

```cmd
python drift\scripts\crear_referencia.py
python drift\scripts\generar_lotes.py
python drift\scripts\analizar_drift.py
```

Los reportes se generan en:

`drift/reports/`

---

## 11. Seguimiento con MLflow

Experimento:

`Sentinel_Observability_Data_Drift`

Ejecuciones:

- `control_refinado`
- `simulado_refinado`

Cada ejecución registra métricas y reportes Evidently
como artefactos.

### Registrar resultados

```cmd
python drift\scripts\registrar_mlflow.py
```

### Iniciar MLflow

```cmd
python -m mlflow ui --backend-store-uri ./mlruns --host 127.0.0.1 --port 5000
```

Abrir:

http://127.0.0.1:5000

---

## 12. Alertas inteligentes

Se implementaron reglas de Prometheus:

| Alerta | Condición | Prioridad |
|---|---|---|
| BackendUnavailable | Backend no disponible durante 2 minutos | P1 |
| HighErrorRate | Errores HTTP 5xx > 5% durante 5 minutos y tráfico mínimo | P1 |
| HighLatency | p95 > 500 ms durante 5 minutos y tráfico mínimo | P2 |

Configuración:

`monitoring/prometheus/rules/sentinel_alerts.yml`

Consultar alertas:

http://localhost:9090/alerts

Documento:

[Alertas y automatización](docs/alertas_y_automatizacion.md)

---

## 13. Simulación de incidentes

### INC-001 — Indisponibilidad del backend

Se simuló la detención del backend mediante:

```cmd
docker compose stop backend
```

La recuperación se realizó mediante:

```cmd
docker compose start backend
```

Resultado final:

- Backend healthy.
- Alerta BackendUnavailable Inactive.
- Servicio recuperado.

[Runbook INC-001](runbooks/INC-001_backend_unavailable.md)

### INC-002 — Incremento de latencia

Se introdujo un retraso artificial de 1.5 segundos
en el endpoint de predicción.

Se utilizó:

```cmd
python simulations\generar_latencia.py
```

Después de la simulación se retiró el retraso y
se recreó el backend.

Resultado final:

- Backend healthy.
- Alerta HighLatency Inactive.
- Predicción posterior satisfactoria.

[Runbook INC-002](runbooks/INC-002_high_latency.md)

Los incidentes se ejecutaron exclusivamente
en un entorno educativo local.

[Resultados de incidentes](docs/resultados_incidentes.md)

---

## 14. Respuesta automatizada y gobernanza

La detección de condiciones anómalas mediante
Prometheus está automatizada.

Las acciones correctivas de los incidentes
se ejecutaron manualmente siguiendo runbooks.

Como mejoras futuras se consideran:

- Rollback automatizado.
- Reentrenamiento sujeto a validación.
- Alertas automáticas de drift.
- Cálculo operativo de error budgets.
- Notificaciones mediante Alertmanager.
- Escalamiento controlado de servicios.

No se implementaron acciones automáticas de
rollback o reentrenamiento.

---

## 15. Evidencias

Las capturas se encuentran en:

`docs/evidencias/`

Incluyen:

- Instrumentación de métricas.
- Dashboards Grafana.
- Logs estructurados.
- Trazas OpenTelemetry y Tempo.
- Resultados de Evidently.
- Ejecuciones y artefactos MLflow.
- Reglas de Prometheus.
- Alertas e incidentes simulados.
- Recuperación de servicios.

Las evidencias deben corresponder a resultados
reales observados durante la ejecución.

---

## 16. Seguridad

- No publicar credenciales.
- Excluir `.env` de Git.
- Mantener servicios accesibles solo localmente.
- No registrar datos personales innecesarios.
- No cargar modelos serializados de fuentes desconocidas.
- Mantener revisión humana en decisiones de fraude.

---

## 17. Limitaciones

- Prototipo educativo local.
- Sin despliegue cloud.
- Modelo no aprobado para producción.
- Sin garantía de cumplimiento mensual de SLO.
- Drift evaluado por lotes.
- Calidad predictiva dependiente de etiquetas reales.
- Sin rollback automático.
- Sin reentrenamiento automático.
- Sin alertamiento automático de drift.
- Sin centralización de logs en Loki.

---

## 18. Conclusiones

Sentinel Observability amplía el proyecto Sentinel
con capacidades de monitorización proactiva,
observabilidad moderna y gestión operativa.

La implementación permite recopilar métricas,
registrar logs, consultar trazas, detectar cambios
estadísticos en los datos y realizar seguimiento
experimental mediante MLflow.

Las simulaciones de indisponibilidad y latencia
permitieron comprobar procedimientos de recuperación
del servicio.

La solución constituye una base reproducible
para evolucionar hacia una operación MLOps con
mayor automatización y gobernanza.

---

## 19. Referencias

- Material académico T19.
- Material académico T20.
- Proyecto Sentinel Fraud Detection.
- Documentación oficial de Prometheus.
- Documentación oficial de Grafana y Tempo.
- Documentación oficial de OpenTelemetry.
- Documentación oficial de Evidently.
- Documentación oficial de MLflow.
