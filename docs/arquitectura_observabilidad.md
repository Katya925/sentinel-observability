
# Sentinel Observability
## Arquitectura de monitorización, mantenimiento y gobernanza operativa

### 1. Introducción

Sentinel Observability es una extensión del proyecto académico
Sentinel, desarrollado para detectar posibles reclamaciones
fraudulentas en seguros de automóviles mediante Machine Learning.

El proyecto incorpora capacidades de observabilidad moderna,
monitorización proactiva, detección de data drift y respuesta
estructurada ante incidentes.

La solución se ejecuta localmente mediante Docker Compose,
sin desplegar infraestructura en la nube.

### 2. Objetivo de la arquitectura

Diseñar e implementar una arquitectura que permita:

- Monitorizar la disponibilidad del servicio.
- Medir latencia, tráfico y errores HTTP.
- Registrar logs estructurados.
- Generar y consultar trazas distribuidas.
- Detectar cambios en las distribuciones de entrada.
- Registrar evaluaciones del modelo mediante MLflow.
- Generar alertas operativas.
- Aplicar runbooks de respuesta ante incidentes.
- Documentar la recuperación del servicio.

### 3. Componentes tecnológicos

| Componente | Tecnología | Función |
|---|---|---|
| Frontend | Streamlit | Interfaz de reclamaciones |
| Backend | FastAPI | API REST e inferencia |
| Modelo ML | Random Forest | Estimación de riesgo de fraude |
| Contenedores | Docker Compose | Orquestación local |
| Métricas | Prometheus Client | Instrumentación del backend |
| Monitorización | Prometheus | Recopilación de métricas y evaluación de reglas |
| Dashboards | Grafana | Visualización operativa |
| Logs | Python logging | Generación de registros JSON |
| Trazas | OpenTelemetry | Instrumentación de solicitudes |
| Almacenamiento de trazas | Grafana Tempo | Recepción y consulta de trazas |
| Data drift | Evidently | Comparación estadística de distribuciones |
| Seguimiento ML | MLflow | Registro de evaluaciones y artefactos |

### 4. Arquitectura lógica

```text
                   USUARIO
                      |
                      v
               STREAMLIT
                      |
                      | HTTP / JSON
                      v
                  FASTAPI
                      |
                      v
             RANDOM FOREST
                      |
             RESULTADO / ALERTA

        OBSERVABILIDAD DEL BACKEND
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
       METRICAS      LOGS       TRAZAS
          |           |           |
          v           |           v
      PROMETHEUS      |       OPENTELEMETRY
          |           |           |
          v           |           v
       GRAFANA        |         TEMPO
                      |           |
                      |           v
                      |        GRAFANA
                      |
                      v
                DOCKER LOGS

       OBSERVABILIDAD DEL MODELO
                      |
             DATOS DE REFERENCIA
                      |
                      v
                  EVIDENTLY
                      |
             REPORTES HTML/JSON
                      |
                      v
                   MLFLOW
```

Los logs JSON se consultan actualmente mediante Docker Compose.
La integración con Loki se considera una ampliación futura.

### 5. Flujo de inferencia

1. El usuario introduce una reclamación en Streamlit.
2. Streamlit envía los datos mediante HTTP a FastAPI.
3. FastAPI valida las variables de entrada.
4. El pipeline ejecuta el preprocesamiento y la inferencia.
5. Se calcula una puntuación de fraude.
6. Se aplica el umbral de alerta configurado.
7. FastAPI devuelve el resultado.
8. Streamlit presenta la clasificación al usuario.

El modelo requiere revisión humana y no está aprobado
para decisiones automáticas de producción.

### 6. Monitorización de métricas

FastAPI expone el endpoint:

`GET /metrics`

Prometheus consulta este endpoint cada 15 segundos.

Las métricas principales son:

- `sentinel_http_requests_total`
- `sentinel_http_request_duration_seconds`
- `sentinel_predictions_total`
- `sentinel_fraud_alerts_total`
- `sentinel_prediction_errors_total`

Grafana permite visualizar las métricas recopiladas.

### 7. Dashboards operativos

Se implementó el dashboard:

**Sentinel Observability — Salud y Rendimiento**

Incluye cuatro indicadores:

1. Total de predicciones.
2. Latencia p95.
3. Tráfico HTTP en solicitudes por segundo.
4. Tasa de errores HTTP 5xx.

Los indicadores se alimentan de Prometheus.

El objetivo inicial de latencia es de 500 milisegundos
para el percentil 95.

La tasa objetivo de errores HTTP 5xx es inferior al 1%.

### 8. Logs estructurados

El backend genera registros JSON mediante Python logging.

Cada evento puede incluir:

- Timestamp UTC.
- Nivel de severidad.
- Servicio.
- Request ID.
- Método HTTP.
- Endpoint.
- Código de respuesta.
- Duración en milisegundos.

Los logs permiten investigar solicitudes y errores.

La consulta se realiza mediante:

`docker compose logs backend`

No se registran intencionalmente reclamaciones completas
ni credenciales.

### 9. Trazas distribuidas

OpenTelemetry instrumenta FastAPI y genera trazas
de las solicitudes HTTP.

Las trazas se exportan mediante OTLP/gRPC hacia Tempo.

Grafana permite consultar las trazas almacenadas
mediante la fuente de datos Tempo.

Se verificó la disponibilidad de trazas correspondientes
a solicitudes de predicción.

La incorporación de spans específicos para preprocesamiento
e inferencia queda como mejora futura.

### 10. Monitorización de Data Drift

Se implementó una evaluación por lotes utilizando Evidently.

Los datos de referencia proceden de la partición de
entrenamiento del modelo Sentinel.

Configuración:

- Dataset original: 15,420 registros.
- Referencia de entrenamiento: 9,252 registros.
- Variables del modelo: 32.
- Variables analizadas para drift: 31.
- Variable excluida del análisis: PolicyNumber.
- Tamaño de cada lote evaluado: 1,000 registros.

Se generaron dos escenarios:

**Control:** datos sin modificaciones deliberadas.

**Simulado:** datos con cambios introducidos en Age,
AccidentArea y Make.

Resultados refinados:

| Escenario | Variables con drift | Porcentaje |
|---|---:|---:|
| Control | 0 de 31 | 0% |
| Simulado | 2 de 31 | 6.45% |

Las variables identificadas con drift fueron Age y Make.

AccidentArea no superó el criterio estadístico aplicado.

La detección de data drift no demuestra por sí misma
una degradación predictiva del modelo.

### 11. Seguimiento mediante MLflow

Se creó el experimento:

`Sentinel_Observability_Data_Drift`

Incluye las ejecuciones:

- `control_refinado`
- `simulado_refinado`

Cada ejecución registra métricas del análisis y
los reportes Evidently como artefactos HTML y JSON.

MLflow se ejecuta localmente y permite consultar
el historial de evaluaciones.

### 12. Alertamiento operativo

Prometheus evalúa las siguientes reglas:

| Alerta | Condición | Prioridad |
|---|---|---|
| BackendUnavailable | Backend inaccesible durante 2 minutos | P1 |
| HighErrorRate | Errores 5xx > 5% durante 5 minutos y tráfico mínimo | P1 |
| HighLatency | p95 > 500 ms durante 5 minutos y tráfico mínimo | P2 |

Se incorporaron ventanas temporales y condiciones
de volumen mínimo para reducir alertas innecesarias.

Las alertas de data drift y consumo acelerado
de error budget quedan pendientes de implementación.

### 13. SLI, SLO y Error Budgets

Se definieron objetivos iniciales de laboratorio:

| Indicador | SLO |
|---|---|
| Disponibilidad | >= 99% |
| Latencia | 95% de solicitudes <= 500 ms |
| Errores HTTP 5xx | < 1% |

Para una disponibilidad objetivo del 99% durante
30 días continuos, el presupuesto teórico de
indisponibilidad es de 7.2 horas.

Estos valores representan objetivos de diseño,
no resultados certificados de operación mensual.

### 14. Gestión de incidentes

Se prepararon y ejecutaron dos runbooks.

#### INC-001 — Indisponibilidad del backend

Se detuvo controladamente el backend.

Prometheus permitió observar la condición
de indisponibilidad.

Posteriormente se inició el contenedor y se verificó:

- Backend healthy.
- Endpoint de salud funcional.
- Alerta BackendUnavailable en estado Inactive.

#### INC-002 — Incremento de latencia

Se introdujo un retraso artificial de 1.5 segundos
en las solicitudes de predicción.

Se generó tráfico controlado y se monitorizó
la latencia p95.

La recuperación consistió en retirar el retraso
y recrear el backend.

Se verificó:

- Backend healthy.
- Alerta HighLatency en estado Inactive.
- Predicción posterior satisfactoria.

La evidencia de activación Firing debe interpretarse
según el registro observado durante la simulación.

### 15. Respuesta automatizada y gobernanza

El sistema implementa detección automática mediante
reglas de Prometheus.

Las acciones correctivas ejecutadas durante las
simulaciones fueron controladas manualmente.

Como mecanismos de evolución se proponen:

- Reinicio automatizado bajo condiciones verificadas.
- Rollback hacia una versión previamente validada.
- Reentrenamiento sujeto a evaluación.
- Escalamiento de incidentes críticos.
- Aprobación humana antes de reemplazar modelos.

No se implementó un rollback automático ni un
reentrenamiento automático durante esta fase.

### 16. Seguridad y privacidad

La arquitectura se ejecuta en un entorno educativo local.

Se consideran las siguientes medidas:

- No registrar datos personales innecesarios.
- No almacenar credenciales en el código.
- Mantener `.env` fuera del repositorio público.
- Restringir los puertos publicados a localhost.
- Evitar la carga de modelos joblib no confiables.
- Mantener la revisión humana en decisiones de fraude.

### 17. Limitaciones

- El modelo no cumple todos los KPI originales de negocio.
- La monitorización de calidad predictiva depende de
  disponer de etiquetas reales.
- El drift se evalúa por lotes, no continuamente.
- MLflow se ejecuta como servicio local independiente.
- Los logs todavía no están centralizados en Loki.
- El consumo operativo de error budgets no está automatizado.
- Las acciones correctivas requieren intervención humana.
- No se realizó despliegue en la nube.

### 18. Evidencias

Las capturas de pantalla se encuentran en:

`docs/evidencias/`

Incluyen:

- Métricas de FastAPI.
- Dashboard Grafana.
- Logs estructurados.
- Trazas OpenTelemetry.
- Conexión Grafana–Tempo.
- Reportes Evidently.
- Experimentos MLflow.
- Reglas de Prometheus.
- Simulaciones y recuperación de incidentes.

### 19. Conclusión

Sentinel Observability amplía el proyecto Sentinel
mediante una arquitectura de observabilidad moderna.

La solución integra métricas, logs y trazas,
seguimiento de Data Drift, experimentación mediante
MLflow, dashboards operativos y procedimientos
estructurados de respuesta ante incidentes.

Las pruebas realizadas permiten demostrar el
funcionamiento de los principales componentes en
un entorno educativo local.

La arquitectura constituye una base para evolucionar
hacia una operación con mayor automatización,
gobernanza y resiliencia.

### 20. Referencias

- Material académico T19: observabilidad y monitorización.
- Material académico T20: continuidad y gestión operativa.
- Documentación técnica del proyecto Sentinel.
- Documentación oficial de Prometheus.
- Documentación oficial de Grafana y Tempo.
- Documentación oficial de OpenTelemetry.
- Documentación oficial de Evidently.
- Documentación oficial de MLflow.
