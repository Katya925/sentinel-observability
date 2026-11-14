
# Sentinel Observability
## Diseño de alertas inteligentes y automatización operativa

### 1. Introducción

Sentinel Observability incorpora mecanismos de monitorización
proactiva para detectar anomalías en el servicio de inferencia
de fraude en seguros.

El sistema utiliza Prometheus para evaluar reglas de alerta,
Grafana para visualizar indicadores y runbooks para responder
de manera estructurada ante incidentes.

Las alertas se alinean con los SLO definidos para el entorno
educativo y permiten priorizar incidentes según su impacto.

### 2. Objetivos del alertamiento

- Detectar indisponibilidad del backend.
- Identificar incrementos de latencia.
- Detectar errores HTTP 5xx.
- Priorizar incidentes según su severidad.
- Reducir alertas innecesarias.
- Facilitar el diagnóstico mediante métricas, logs y trazas.
- Documentar acciones correctivas.
- Establecer mecanismos futuros de automatización.

### 3. SLI, SLO y presupuestos de error

| Indicador | SLO propuesto | Error budget |
|---|---|---|
| Disponibilidad | >= 99% | 1% de tiempo no disponible |
| Latencia | 95% de solicitudes <= 500 ms | 5% de solicitudes lentas |
| Errores HTTP 5xx | < 1% | Menos del 1% de solicitudes válidas |

Los SLO corresponden a objetivos educativos y no representan
acuerdos contractuales de nivel de servicio.

El error budget de disponibilidad equivalente a 30 días
continuos es de 7.2 horas.

El consumo real de los presupuestos deberá calcularse
a partir de las mediciones del servicio.

### 4. Reglas de alertamiento implementadas

Las reglas están definidas en:

`monitoring/prometheus/rules/sentinel_alerts.yml`

| Alerta | Condición | Prioridad |
|---|---|---|
| BackendUnavailable | up == 0 durante 2 minutos | P1 |
| HighErrorRate | Errores 5xx > 5% durante 5 minutos, con tráfico mínimo | P1 |
| HighLatency | Latencia p95 > 500 ms durante 5 minutos, con tráfico mínimo | P2 |

Prometheus evalúa las reglas automáticamente.

La activación de una alerta indica que se cumplen
las condiciones configuradas, pero no ejecuta por sí misma
una acción correctiva.

### 5. Priorización de incidentes

#### P1 — Crítico

Corresponde a fallos que comprometen la disponibilidad
o provocan errores generalizados.

Ejemplos:

- BackendUnavailable.
- HighErrorRate.

Respuesta prevista:

- Diagnóstico inmediato.
- Ejecución del runbook.
- Evaluación de rollback o recuperación.
- Escalamiento cuando corresponda.

#### P2 — Alto

Corresponde a degradaciones significativas del rendimiento
o cambios relevantes en el comportamiento de los datos.

Ejemplos:

- HighLatency.
- Data drift significativo en variables prioritarias.

Respuesta prevista:

- Investigación de métricas.
- Análisis de logs y trazas.
- Aplicación de mitigaciones controladas.
- Seguimiento de la recuperación.

#### P3 — Preventivo

Corresponde a señales tempranas que requieren investigación,
pero no comprometen inmediatamente la continuidad.

Ejemplos:

- Incremento moderado de valores faltantes.
- Categorías nuevas en las entradas.
- Cambios menores en distribuciones.

### 6. Reducción de ruido

Las reglas operativas incorporan mecanismos como:

- Ventanas de evaluación de cinco minutos.
- Condiciones sostenidas mediante `for`.
- Volumen mínimo de solicitudes para alertas de
  latencia y errores.
- Priorización mediante etiquetas P1 y P2.

Como mejoras futuras se consideran:

- Agrupación de notificaciones.
- Inhibición de alertas derivadas.
- Periodos de silencio durante mantenimiento.
- Deduplicación y escalamiento mediante Alertmanager.

Estas últimas capacidades no se consideran implementadas
en la configuración actual.

### 7. Alertas de Data Drift

La detección de drift se implementó por lotes mediante Evidently.

Resultados refinados:

| Escenario | Variables con drift | Porcentaje |
|---|---:|---:|
| Control | 0 de 31 | 0% |
| Simulado | 2 de 31 | 6.45% |

Las variables afectadas fueron:

- Age.
- Make.

Se excluyó PolicyNumber del análisis estadístico
por su naturaleza de identificador.

#### Regla propuesta

Generar una alerta P2 cuando se detecte drift
en una variable prioritaria y el cambio persista
en evaluaciones consecutivas.

Esta regla está documentada como diseño futuro.
Actualmente no se publica automáticamente una métrica
de drift hacia Prometheus.

### 8. Error Budget Burn Rate

El burn rate representa la velocidad a la que se consume
el presupuesto de error permitido por un SLO.

Para un SLO de disponibilidad del 99%, el presupuesto
de errores es del 1%.

Ejemplo hipotético:

Si el 5% de las solicitudes falla durante una ventana,
el burn rate aproximado respecto al presupuesto
de errores del 1% sería:

5% / 1% = 5.

Esto representa un consumo cinco veces más rápido
que el ritmo uniforme permitido.

#### Diseño propuesto

- P1: consumo acelerado sostenido en ventanas corta y larga.
- P2: consumo elevado en ventanas de mayor duración.
- P3: advertencias preventivas.

Los umbrales definitivos y las ventanas múltiples
deberán calibrarse mediante mediciones reales.

El alertamiento automático por burn rate
todavía no está implementado.

### 9. Runbooks implementados

#### INC-001 — BackendUnavailable

Archivo:

`runbooks/INC-001_backend_unavailable.md`

Acciones ejecutadas:

1. Detención controlada del backend.
2. Observación de indisponibilidad.
3. Aplicación del procedimiento de recuperación.
4. Inicio del backend.
5. Verificación de estado healthy.
6. Confirmación de alerta Inactive.

#### INC-002 — HighLatency

Archivo:

`runbooks/INC-002_high_latency.md`

Acciones ejecutadas:

1. Introducción de retraso artificial de 1.5 segundos.
2. Generación de tráfico controlado.
3. Monitorización de latencia p95.
4. Desactivación del retraso.
5. Recreación del backend.
6. Verificación de recuperación funcional.
7. Confirmación de alerta Inactive.

Los tiempos y estados específicos deben consultarse
en los registros de cada runbook.

### 10. Respuesta automatizada

#### 10.1 Detección automática implementada

Prometheus evalúa automáticamente las reglas
de disponibilidad, latencia y errores.

Los dashboards permiten consultar el comportamiento
del servicio.

#### 10.2 Recuperación manual implementada

Durante las simulaciones, las acciones correctivas
se ejecutaron manualmente mediante Docker Compose.

No se implementó un mecanismo automático
de reinicio o rollback basado en las alertas.

#### 10.3 Reinicio automatizado propuesto

Flujo previsto:

1. Detectar indisponibilidad.
2. Confirmar la condición mediante comprobaciones adicionales.
3. Verificar que no existe mantenimiento programado.
4. Ejecutar una recuperación controlada.
5. Comprobar disponibilidad y salud.
6. Registrar el resultado y escalar si persiste el problema.

#### 10.4 Rollback automatizado propuesto

Flujo previsto:

1. Detectar degradación persistente.
2. Identificar la versión del modelo desplegada.
3. Comprobar la disponibilidad de una versión anterior validada.
4. Solicitar aprobación cuando corresponda.
5. Restaurar la versión autorizada.
6. Ejecutar pruebas funcionales.
7. Verificar los SLO y registrar la intervención.

#### 10.5 Reentrenamiento propuesto

Flujo previsto:

1. Detectar drift persistente.
2. Confirmar disponibilidad de etiquetas y datos confiables.
3. Evaluar degradación predictiva.
4. Ejecutar reentrenamiento en un entorno aislado.
5. Comparar métricas con el modelo vigente.
6. Solicitar aprobación humana.
7. Desplegar únicamente un modelo validado.
8. Mantener posibilidad de rollback.

El drift por sí solo no debe desencadenar
un reemplazo automático del modelo.

### 11. Gobernanza operativa

La gobernanza contempla:

- Registro de incidentes.
- Versionado de configuraciones.
- Evidencias reproducibles.
- Trazabilidad de evaluaciones en MLflow.
- Revisión humana de decisiones.
- Separación entre detección y acciones correctivas.
- Documentación de cambios y recuperaciones.

El modelo Sentinel no está aprobado para uso productivo.

### 12. Evidencias

Las evidencias de alertamiento e incidentes
se encuentran en:

`docs/evidencias/`

Entre ellas:

- `16_prometheus_alertas_configuradas.png`
- `17_inc001_alerta_firing.png`
- `18_inc001_recuperacion.png`
- `19_inc002_high_latency_firing.png`
- `20_inc002_latencia_elevada.png`
- `21_inc002_recuperacion.png`
- `22_inc002_prediccion_recuperada.png`

La existencia y correspondencia de cada archivo
debe verificarse antes de publicar el repositorio.

### 13. Limitaciones

- No se configuró Alertmanager.
- No se implementó notificación externa automática.
- No se implementó rollback automático.
- No se implementó reentrenamiento automático.
- No existe una alerta automática de drift.
- No se implementaron reglas de burn rate.
- La ejecución se realizó en un entorno local educativo.

### 14. Conclusión

Sentinel Observability dispone de un sistema inicial
de alertamiento operativo mediante Prometheus.

Las reglas permiten detectar indisponibilidad,
errores y degradaciones de latencia.

Las simulaciones documentadas permiten evaluar
la respuesta ante incidentes y la recuperación
del servicio mediante runbooks.

El proyecto establece una base para incorporar
posteriormente acciones correctivas automatizadas,
gestión avanzada de notificaciones y gobernanza MLOps.

### 15. Referencias

- Material académico T19.
- Material académico T20.
- docs/indicadores_slo.md.
- docs/arquitectura_observabilidad.md.
- Documentación oficial de Prometheus y Grafana.
- Runbooks INC-001 e INC-002.
