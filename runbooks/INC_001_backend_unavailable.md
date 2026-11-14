
# Runbook INC-001 — BackendUnavailable

## 1. Identificación

- Proyecto: Sentinel Observability
- Servicio: sentinel-backend
- Incidente: INC-001
- Prioridad: P1 — Crítico
- Alerta: BackendUnavailable
- Entorno: Docker Compose local

## 2. Objetivo

Detectar la indisponibilidad del backend FastAPI y
restablecer el servicio mediante un procedimiento controlado.

## 3. Condición de activación

La alerta se activa cuando Prometheus detecta que
el backend permanece inaccesible durante 2 minutos.

Regla:

`up{job="sentinel-backend"} == 0`

## 4. Procedimiento de diagnóstico

1. Consultar el estado de la alerta en Prometheus.
2. Verificar el estado del contenedor backend.
3. Revisar los logs del servicio.
4. Identificar la causa de la indisponibilidad.

## 5. Procedimiento de recuperación

1. Iniciar nuevamente el backend.
2. Esperar a que alcance el estado healthy.
3. Verificar el endpoint /health.
4. Confirmar que Prometheus vuelve a recopilar métricas.
5. Comprobar que la alerta deja de estar activa.

## 6. Criterios de recuperación

- Backend en estado healthy.
- Endpoint /health responde HTTP 200.
- Métrica up del backend igual a 1.
- Alerta BackendUnavailable en estado Inactive.

## 7. Evidencias

- Estado normal del servicio.
- Alerta activada.
- Estado del contenedor durante el incidente.
- Ejecución del procedimiento de recuperación.
- Servicio restaurado.
- Alerta resuelta.

## 8. Conclusión

La conclusión se documentará después de ejecutar
la simulación y verificar los resultados reales.


## 9. Registro de ejecución del incidente

### Identificación

- ID: INC-001
- Nombre: Indisponibilidad del backend FastAPI
- Servicio afectado: sentinel-backend
- Entorno: Docker Compose local
- Prioridad: P1 - Crítico
- Tipo: Incidente simulado

### Escenario

Se simuló la indisponibilidad del backend de Sentinel
Observability mediante la detención controlada del
contenedor Docker.

Comando utilizado:

```cmd
docker compose stop backend
```

### Detección

El sistema de monitorización utiliza Prometheus
para supervisar la disponibilidad del backend.

Regla:

```promql
up{job="sentinel-backend"} == 0
```

La alerta BackendUnavailable está configurada
con un periodo de espera de 2 minutos.

### Respuesta al incidente

Se aplicó el runbook de recuperación mediante:

```cmd
docker compose start backend
```

Posteriormente se verificó:

- Estado del contenedor Docker.
- Disponibilidad del endpoint /health.
- Estado del target en Prometheus.
- Resolución de la alerta BackendUnavailable.

### Resultados observados

| Indicador | Resultado |
|---|---|
| Estado inicial | Up (healthy) |
| Estado durante el incidente | Backend detenido |
| Alerta BackendUnavailable | Firing |
| Estado posterior | Up (healthy) |
| Endpoint /health | HTTP 200 |
| Estado final de alerta | Inactive |

### Tiempos del incidente

- Inicio: No registrado
- Detección: No registrado
- Recuperación: No registrado
- Tiempo total: No registrado

### Evidencias

- `docs/evidencias/17_inc001_alerta_firing.png`
- `docs/evidencias/18_inc001_recuperacion.png`

### Conclusión

La simulación permite evaluar la detección de
indisponibilidad del backend y la aplicación de
un procedimiento estructurado de recuperación.

El resultado definitivo se establecerá después
de verificar el estado final del servicio y
la resolución de la alerta.

