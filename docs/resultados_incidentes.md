
# Sentinel Observability
## Resultados de simulación y respuesta a incidentes

### 1. Introducción

Este documento consolida los resultados de dos incidentes
simulados durante la implementación de Sentinel Observability.

El objetivo fue evaluar la detección de fallas, el funcionamiento
de las alertas operativas y la ejecución de procedimientos
estructurados de recuperación.

Las simulaciones se realizaron en un entorno local educativo,
utilizando Docker Compose, FastAPI, Prometheus y Grafana.

### 2. Incidentes evaluados

| ID | Incidente | Prioridad | Resultado |
|---|---|---|---|
| INC-001 | Indisponibilidad del backend | P1 | Servicio recuperado |
| INC-002 | Incremento de latencia | P2 | Servicio recuperado |

### 3. INC-001 — Indisponibilidad del backend

#### Objetivo

Evaluar la detección de indisponibilidad del servicio
de inferencia y su posterior recuperación.

#### Escenario

Se detuvo controladamente el contenedor del backend:

`docker compose stop backend`

#### Detección

Prometheus supervisó el servicio mediante la métrica:

`up{job="sentinel-backend"}`

La alerta BackendUnavailable está configurada para
activarse después de dos minutos de indisponibilidad.

#### Respuesta ejecutada

Se aplicó el runbook INC-001 y se inició nuevamente
el backend:

`docker compose start backend`

#### Resultados

| Indicador | Resultado |
|---|---|
| Estado inicial | Up (healthy) |
| Estado durante el incidente | Backend detenido |
| Estado final | Up (healthy) |
| Alerta final | Inactive |
| Recuperación | Satisfactoria |

Estado Firing observado: [Confirmar según evidencia].

Tiempo de detección: [Registrar si se midió].

Tiempo de recuperación: [Registrar si se midió].

#### Evidencias

- `docs/evidencias/17_inc001_alerta_firing.png`
- `docs/evidencias/18_inc001_recuperacion.png`

### 4. INC-002 — Incremento de latencia

#### Objetivo

Evaluar la detección y recuperación de una degradación
del rendimiento del endpoint POST /predict.

#### Escenario

Se introdujo un retraso artificial de 1.5 segundos
mediante la variable:

`SENTINEL_SIMULATE_LATENCY_SECONDS=1.5`

Se generaron solicitudes controladas utilizando:

`simulations/generar_latencia.py`

#### Detección

Se monitorizó la latencia p95 mediante Prometheus
y el dashboard de Grafana.

La alerta HighLatency está configurada para activarse
cuando la latencia supera 500 milisegundos durante
cinco minutos, con un volumen mínimo de solicitudes.

#### Respuesta ejecutada

Se retiró el retraso artificial:

`SENTINEL_SIMULATE_LATENCY_SECONDS=0`

Posteriormente se recreó el backend mediante Docker Compose.

#### Resultados

| Indicador | Resultado |
|---|---|
| Estado inicial | Backend disponible |
| Falla simulada | Retraso artificial de 1.5 segundos |
| Estado final | Up (healthy) |
| Alerta final | Inactive |
| Predicción posterior | Satisfactoria |
| Recuperación | Satisfactoria |

Estado Firing observado: [Confirmar según evidencia].

Latencia p95 máxima: [Registrar valor observado].

Latencia p95 posterior: [Registrar valor observado].

Tiempo de recuperación: [Registrar si se midió].

#### Evidencias

- `docs/evidencias/19_inc002_high_latency_firing.png`
- `docs/evidencias/20_inc002_latencia_elevada.png`
- `docs/evidencias/21_inc002_recuperacion.png`
- `docs/evidencias/22_inc002_prediccion_recuperada.png`

### 5. Comparación de incidentes

| Criterio | INC-001 | INC-002 |
|---|---|---|
| Tipo | Disponibilidad | Rendimiento |
| Servicio afectado | FastAPI | FastAPI |
| Alerta | BackendUnavailable | HighLatency |
| Prioridad | P1 | P2 |
| Herramienta de detección | Prometheus | Prometheus |
| Visualización | Prometheus | Grafana |
| Respuesta | Inicio del backend | Retiro del retraso |
| Estado final | Recuperado | Recuperado |

### 6. Evaluación de los runbooks

Los runbooks proporcionaron procedimientos
estructurados para:

1. Identificar el incidente.
2. Consultar indicadores.
3. Diagnosticar la falla.
4. Aplicar una acción correctiva.
5. Verificar la recuperación.
6. Documentar el resultado.

Las acciones correctivas se ejecutaron manualmente.

### 7. Lecciones aprendidas

- Los indicadores operativos permiten observar
  degradaciones del servicio.
- Las alertas requieren ventanas temporales para
  evitar activaciones por eventos aislados.
- Los runbooks facilitan la recuperación controlada.
- La latencia p95 permite observar cambios de rendimiento.
- Los estados de Docker y Prometheus deben interpretarse
  de forma diferenciada.
- Las evidencias permiten reconstruir la secuencia
  de los incidentes.

### 8. Limitaciones

- Las fallas fueron simuladas en un entorno local.
- No se evaluaron incidentes reales de producción.
- No se implementó rollback automático.
- No se ejecutó reentrenamiento automático.
- Los tiempos exactos dependen de los registros observados.
- Las pruebas no garantizan el cumplimiento continuo
  de los SLO durante un periodo mensual.

### 9. Conclusión

Las simulaciones permitieron comprobar la recuperación
del backend de Sentinel Observability después de una
indisponibilidad y una degradación de latencia.

El proyecto demuestra la aplicación de procedimientos
estructurados de respuesta a incidentes, respaldados
por métricas operativas y evidencias documentadas.

La arquitectura proporciona una base para evolucionar
hacia mecanismos de respuesta automatizada y
gobernanza operativa más avanzada.

### 10. Referencias

- runbooks/INC-001_backend_unavailable.md
- runbooks/INC-002_high_latency.md
- docs/indicadores_slo.md
- docs/alertas_y_automatizacion.md
- Material académico T19 y T20.
