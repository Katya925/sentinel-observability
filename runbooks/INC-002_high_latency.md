
# Runbook INC-002 — HighLatency

## 1. Identificación

- Proyecto: Sentinel Observability
- Incidente: INC-002
- Servicio: sentinel-backend
- Prioridad: P2 — Alta
- Tipo: Degradación de rendimiento
- Entorno: Docker Compose local

## 2. Objetivo

Detectar y responder a un incremento anómalo
de la latencia del servicio de inferencia.

## 3. Condición de activación

La alerta HighLatency se activa cuando:

- La latencia p95 supera 500 milisegundos.
- Existen al menos 20 solicitudes en cinco minutos.
- La condición permanece activa durante cinco minutos.

## 4. Diagnóstico

1. Revisar el dashboard de Grafana.
2. Consultar la latencia p95 de /predict.
3. Verificar el estado del backend.
4. Consultar logs estructurados.
5. Revisar trazas OpenTelemetry en Tempo.
6. Identificar el origen de la degradación.

## 5. Respuesta al incidente

1. Confirmar que la degradación es reproducible.
2. Identificar la causa de la latencia elevada.
3. Aplicar una mitigación controlada.
4. Retirar la falla simulada.
5. Verificar la recuperación de la latencia.
6. Confirmar que HighLatency regresa a Inactive.

## 6. Criterios de recuperación

- Backend disponible y healthy.
- Endpoint /predict funcional.
- Latencia p95 dentro del objetivo.
- Alerta HighLatency en estado Inactive.

## 7. Evidencias requeridas

- Dashboard antes de la simulación.
- Incremento de latencia.
- Alerta HighLatency en estado Firing.
- Ejecución del procedimiento de recuperación.
- Dashboard después de la recuperación.
- Alerta resuelta.

## 8. Resultados

Pendiente de ejecutar la simulación.

Los tiempos y métricas se registrarán
con los valores realmente observados.

## 9. Registro de ejecución del incidente

### Escenario simulado

Se introdujo un retraso artificial de 1.5 segundos
en el endpoint POST /predict mediante la variable
SENTINEL_SIMULATE_LATENCY_SECONDS.

Se ejecutó un generador de tráfico controlado para
evaluar el comportamiento del servicio.

### Detección

La latencia p95 se monitorizó mediante Prometheus
y se visualizó en Grafana.

- SLO de latencia: 500 ms.
- Alerta configurada: HighLatency.
- Prioridad: P2.
- Estado observado de la alerta: Firing.
- Latencia p95 máxima observada: 2.48s

### Respuesta ejecutada

Se desactivó el retraso artificial:

SENTINEL_SIMULATE_LATENCY_SECONDS=0

Se recreó el contenedor del backend y se verificó
su funcionamiento.

### Resultados de recuperación

| Indicador | Resultado |
|---|---|
| Backend después de recuperación | Up (healthy) |
| Latencia p95 posterior | 243ms |
| Estado final de HighLatency | Inactive |
| Predicciones después de recuperación | Exitosas, Streamlit generó predicción correctamente |

### Evidencias

- docs/evidencias/19_inc002_high_latency_firing.png
- docs/evidencias/20_inc002_latencia_elevada.png
- docs/evidencias/21_inc002_recuperacion.png

### Conclusión

La simulación permitió evaluar la detección
de degradación de latencia y la aplicación
del procedimiento de recuperación.

Los resultados definitivos corresponden a
las mediciones y estados observados.
