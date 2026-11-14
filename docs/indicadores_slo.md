
# Sentinel Observability — Indicadores, SLI, SLO y Error Budgets

## 1. Introducción

Sentinel Observability es una extensión del proyecto educativo Sentinel, desarrollado para identificar posibles fraudes en reclamaciones de seguros de automóviles mediante Machine Learning.

El objetivo de esta fase es implementar un sistema de monitorización proactiva que permita observar el comportamiento técnico y predictivo del servicio, detectar anomalías y responder de manera estructurada ante incidentes.

El sistema utiliza una arquitectura basada en FastAPI, Streamlit, Docker Compose y un modelo Random Forest previamente entrenado.

La monitorización se fundamentará en tres señales de observabilidad:

- **Métricas:** valores cuantitativos que describen el funcionamiento del sistema.
- **Logs:** registros estructurados de eventos y errores.
- **Trazas:** información que permite seguir una solicitud a través de sus componentes.

También se aplicarán conceptos de Site Reliability Engineering (SRE), incluyendo SLI, SLO, error budgets y gestión de incidentes.

## 2. Objetivos de la monitorización

Los objetivos específicos son:

1. Verificar la disponibilidad de los servicios.
2. Medir la latencia de las solicitudes.
3. Identificar errores de procesamiento.
4. Monitorizar el volumen de inferencias.
5. Analizar el comportamiento de las puntuaciones de fraude.
6. Detectar cambios en la distribución de los datos.
7. Identificar posibles degradaciones del modelo.
8. Generar alertas priorizadas.
9. Facilitar la respuesta ante incidentes.
10. Proporcionar evidencia técnica reproducible.

## 3. Definición de SLI y SLO

### 3.1 Service Level Indicator (SLI)

Un SLI es una medida cuantitativa del comportamiento de un servicio.

Para Sentinel se utilizarán indicadores relacionados con disponibilidad, latencia, errores y funcionamiento del modelo.

### 3.2 Service Level Objective (SLO)

Un SLO establece el valor objetivo que debe alcanzar un SLI durante una ventana de evaluación.

Los SLO de Sentinel son objetivos propuestos para un entorno educativo local y deberán validarse mediante mediciones reales.

### 3.3 Service Level Agreement (SLA)

Un SLA es un acuerdo formal sobre niveles de servicio.

Sentinel no cuenta con un SLA contractual, debido a que es un prototipo educativo.

Los SLO definidos se utilizarán exclusivamente como referencia técnica.

## 4. Indicadores técnicos del servicio

### 4.1 Disponibilidad

**Objetivo:** verificar que el backend responda correctamente a las solicitudes.

**SLI:**

Disponibilidad = (Solicitudes válidas atendidas / Total de solicitudes válidas) × 100

Las solicitudes válidas atendidas son aquellas que no fallan por causas atribuibles al servidor. Los errores de validación 4xx se analizarán por separado.

**SLO propuesto:** disponibilidad igual o superior al 99%.

**Ventana de evaluación:** 30 días.

**Fuente:** métricas HTTP de FastAPI recopiladas mediante Prometheus.

### 4.2 Latencia

**Objetivo:** medir el tiempo necesario para procesar una solicitud de inferencia.

**SLI:** duración de las solicitudes HTTP POST /predict.

**SLO propuesto:** al menos el 95% de las solicitudes debe completarse en 500 milisegundos o menos.

**Indicadores complementarios:**

- Latencia p50.
- Latencia p95.
- Latencia p99.

**Ventana de evaluación:** 30 días.

**Fuente:** histogramas Prometheus instrumentados en FastAPI.

### 4.3 Tasa de errores

**Objetivo:** detectar fallos técnicos durante el procesamiento.

**SLI:**

Tasa de errores = (Solicitudes con errores HTTP 5xx / Total de solicitudes válidas) × 100

**SLO propuesto:** menos del 1% de errores atribuibles al servidor.

**Ventana de evaluación:** 30 días.

**Fuente:** contadores HTTP de Prometheus.

### 4.4 Tráfico

**Objetivo:** monitorizar el volumen de solicitudes.

**Indicadores:**

- Solicitudes por segundo.
- Número de predicciones.
- Solicitudes por endpoint.
- Distribución de códigos HTTP.

**SLO:** no se establece inicialmente un objetivo contractual de tráfico.

El tráfico se utilizará para interpretar el comportamiento del servicio y detectar cambios anómalos.

### 4.5 Saturación

**Objetivo:** detectar limitaciones de recursos.

**Indicadores:**

- Utilización de CPU.
- Consumo de memoria.
- Reinicios de contenedores.
- Recursos disponibles.

Los umbrales se establecerán después de medir el comportamiento normal del sistema.

## 5. Indicadores del modelo de Machine Learning

### 5.1 Volumen de inferencias

**Métrica:** número total de predicciones ejecutadas.

**Nombre propuesto:**

`sentinel_predictions_total`

Permite conocer la utilización del modelo.

### 5.2 Alertas de fraude

**Métrica:** número de reclamaciones que superan el umbral de alerta.

**Nombre propuesto:**

`sentinel_fraud_alerts_total`

**Umbral del modelo:** 0.19.

Este valor corresponde al umbral seleccionado durante la experimentación de Sentinel.

La alerta de fraude es una salida del modelo y no debe confundirse con una alerta de incidente operativo.

### 5.3 Distribución de puntuaciones

**Objetivo:** observar cambios en las puntuaciones estimadas de fraude.

Se monitorizarán:

- Media de las puntuaciones.
- Mediana.
- Percentiles.
- Proporción de reclamaciones con alerta.

Los cambios relevantes se investigarán para determinar si están relacionados con data drift o con variaciones en el comportamiento del servicio.

### 5.4 Calidad predictiva

Se utilizarán las siguientes métricas cuando existan etiquetas reales disponibles:

- Precision.
- Recall.
- F1-Score.
- False Positive Rate (FPR).
- PR-AUC.

#### Resultados de referencia de Sentinel

| Métrica | Resultado de validación |
|---|---:|
| Precision | 29.59% |
| Recall | 31.35% |
| FPR | 4.76% |
| F1-Score | 30.45% |

Estos resultados corresponden al modelo Random Forest Optimizado con umbral 0.19.

Se utilizarán como referencia experimental y no como garantía de desempeño futuro.

**Importante:** sin etiquetas reales de fraude no es posible calcular directamente precision, recall o FPR de nuevas reclamaciones.

## 6. Detección de Data Drift

### 6.1 Objetivo

Detectar cambios en la distribución de las variables de entrada que puedan afectar el comportamiento del modelo.

### 6.2 Datos de referencia

Se utilizará un conjunto de referencia procedente de los datos de entrenamiento, conservando las variables originales y excluyendo `FraudFound_P` del análisis de entradas.

### 6.3 Datos actuales

Se utilizarán lotes de reclamaciones simuladas o datos de prueba recibidos por la API.

### 6.4 Variables prioritarias

Se analizarán inicialmente:

- Age.
- VehiclePrice.
- AccidentArea.
- Make.
- PolicyType.
- PastNumberOfClaims.

### 6.5 Métodos de detección

Para variables numéricas:

- Prueba Kolmogorov-Smirnov, cuando sea apropiada.
- Population Stability Index (PSI).
- Comparación de distribuciones y cuantiles.

Para variables categóricas:

- Comparación de frecuencias.
- Pruebas estadísticas apropiadas para categorías.
- Detección de categorías nuevas.

### 6.6 Umbrales exploratorios

Como regla inicial de laboratorio para PSI:

| PSI | Interpretación orientativa |
|---|---|
| < 0.10 | Cambio reducido |
| 0.10 a < 0.25 | Cambio que requiere seguimiento |
| ≥ 0.25 | Cambio relevante que requiere investigación |

Estos valores son convenciones exploratorias, no límites universales. Se contrastarán con el tamaño de muestra, la variable analizada y los resultados observados.

### 6.7 Frecuencia

En el entorno educativo se ejecutará la detección de drift por lotes, durante las simulaciones.

En un sistema operativo real podría establecerse una frecuencia diaria o semanal, dependiendo del volumen de reclamaciones.

## 7. Logs estructurados

### 7.1 Objetivo

Registrar eventos relevantes para diagnosticar errores y reconstruir el comportamiento del servicio.

### 7.2 Información mínima

Cada registro deberá incluir, cuando corresponda:

- Timestamp en UTC.
- Nivel de severidad.
- Nombre del servicio.
- Endpoint.
- Método HTTP.
- Código de respuesta.
- Duración de la solicitud.
- Identificador de solicitud.
- Identificador de traza.
- Versión del modelo.
- Tipo de error.

### 7.3 Niveles de logs

| Nivel | Uso |
|---|---|
| INFO | Operaciones normales |
| WARNING | Situaciones anómalas |
| ERROR | Fallos de procesamiento |
| CRITICAL | Fallos que comprometen el servicio |

### 7.4 Privacidad

No se registrarán reclamaciones completas, datos personales innecesarios ni credenciales.

Los logs deberán limitarse a información técnica necesaria para la observabilidad.

## 8. Trazas distribuidas

### 8.1 Objetivo

Seguir el recorrido de una solicitud desde su recepción hasta la generación de una predicción.

### 8.2 Componentes

Las trazas permitirán identificar:

1. Recepción de la solicitud HTTP.
2. Validación de datos.
3. Preprocesamiento.
4. Ejecución del modelo.
5. Generación de respuesta.

### 8.3 Información registrada

- Trace ID.
- Span ID.
- Servicio.
- Operación.
- Duración.
- Estado.
- Errores asociados.

Se utilizará OpenTelemetry para la instrumentación.

## 9. Error Budgets

### 9.1 Definición

Un error budget representa el margen de incumplimiento permitido por un SLO durante una ventana de evaluación.

### 9.2 Disponibilidad

**SLO:** 99% durante 30 días.

**Presupuesto de indisponibilidad:** 1%.

En una ventana continua de 30 días:

30 × 24 × 60 × 0.01 = 432 minutos.

**Error budget teórico:** 7.2 horas.

Esta equivalencia temporal es orientativa. El consumo real se medirá según el SLI definido y las ventanas efectivamente observadas.

### 9.3 Solicitudes fallidas

Para un SLO de éxito de 99%:

Error budget = 1% de las solicitudes válidas.

Ejemplo hipotético:

- Solicitudes: 10,000.
- Fallos permitidos: 100.

### 9.4 Latencia

Para el objetivo de 95% de solicitudes completadas en 500 ms o menos:

Error budget = 5% de las solicitudes que superan 500 ms.

Los presupuestos de latencia, disponibilidad y errores se evaluarán por separado, evitando sumarlos como si fueran equivalentes.

## 10. Diseño inicial de alertas inteligentes

| Alerta | Condición propuesta | Prioridad |
|---|---|---|
| BackendUnavailable | Servicio no disponible durante 2 minutos | P1 |
| HighErrorRate | Errores 5xx superiores al 5% durante 5 minutos | P1 |
| HighLatency | p95 superior a 500 ms durante 5 minutos | P2 |
| ErrorBudgetBurn | Consumo acelerado del presupuesto de error | P1/P2 según severidad |
| SignificantDataDrift | Drift relevante en variables prioritarias | P2 |
| UnknownCategories | Incremento sostenido de categorías nuevas | P3 |
| ModelPerformanceDrop | Degradación predictiva confirmada con etiquetas | P2 |

Los umbrales de alerta son condiciones de detección, no necesariamente idénticos a los SLO.

Para las métricas basadas en solicitudes se exigirá un volumen mínimo de observaciones, con el fin de reducir alertas causadas por muestras pequeñas.

## 11. Priorización de incidentes

### P1 — Crítico

Incidentes que comprometen la disponibilidad o provocan fallos generalizados.

**Respuesta:** ejecución inmediata del runbook y evaluación de rollback.

### P2 — Alto

Degradación importante de latencia, drift relevante o pérdida confirmada de calidad predictiva.

**Respuesta:** diagnóstico, mitigación y seguimiento prioritario.

### P3 — Preventivo

Cambios moderados que requieren investigación, pero no comprometen inmediatamente el servicio.

**Respuesta:** análisis programado y seguimiento.

## 12. Reducción de ruido en alertas

Se utilizarán:

- Ventanas temporales de evaluación.
- Condiciones sostenidas mediante `for`.
- Agrupación por servicio e incidente.
- Inhibición de alertas derivadas de una falla principal.
- Periodos de espera entre notificaciones.
- Umbrales mínimos de tráfico.
- Revisión de falsos positivos de alertamiento.

Estas estrategias se implementarán progresivamente mediante Prometheus y el componente de gestión de alertas.

## 13. Dashboards propuestos

### Dashboard 1 — Salud del servicio

Indicadores:

- Disponibilidad.
- Solicitudes por segundo.
- Latencia p50, p95 y p99.
- Errores HTTP.
- Estado de los contenedores.

### Dashboard 2 — Monitorización del modelo

Indicadores:

- Número de inferencias.
- Número de alertas de fraude.
- Distribución de puntuaciones.
- Errores de inferencia.
- Resultados de data drift.
- Métricas predictivas cuando existan etiquetas.

### Dashboard 3 — Gestión de incidentes

Indicadores:

- Alertas activas.
- Prioridad.
- Duración de incidentes.
- Consumo del error budget.
- Estado de los runbooks.
- Tiempo de recuperación.

## 14. Frecuencia de monitorización

| Elemento | Frecuencia inicial |
|---|---|
| Métricas técnicas | Cada 15 segundos |
| Dashboards | Actualización aproximada cada 15 segundos |
| Evaluación de alertas | Cada 15 segundos |
| Data drift | Por lote de simulación |
| Calidad predictiva | Cuando existan etiquetas |
| Revisión de incidentes | Después de cada simulación |

Estas frecuencias se ajustarán según el consumo de recursos del entorno local.

## 15. Herramientas

| Herramienta | Función |
|---|---|
| FastAPI | Servicio de inferencia |
| Prometheus | Recopilación de métricas |
| Grafana | Dashboards operativos |
| MLflow | Registro de evaluaciones del modelo |
| Evidently | Detección y reporte de data drift |
| OpenTelemetry | Instrumentación de trazas |
| Loki | Almacenamiento y consulta de logs |
| Tempo | Almacenamiento y consulta de trazas |
| Docker Compose | Ejecución local de componentes |

## 16. Evidencias esperadas

Durante la implementación se recopilarán:

1. Endpoint `/metrics` funcionando.
2. Prometheus recopilando métricas.
3. Dashboards Grafana con mediciones reales.
4. Logs estructurados.
5. Trazas de solicitudes.
6. Reportes de data drift.
7. Alertas activadas durante simulaciones.
8. Registros de incidentes.
9. Ejecución de runbooks.
10. Evidencia de recuperación del servicio.

Las evidencias se almacenarán en `docs/evidencias/`.

## 17. Alcance y limitaciones

Sentinel Observability es un proyecto educativo ejecutado localmente.

Los SLO definidos son objetivos de diseño y no compromisos contractuales.

El modelo de Machine Learning no cumple todos los KPI originales de negocio y no está aprobado para producción.

Las simulaciones se realizarán con datos públicos o sintéticos.

No se desplegará infraestructura en la nube.

## 18. Referencias

- Material académico T19 proporcionado para el proyecto.
- Material académico T20 proporcionado para el proyecto.
- Documentación técnica del proyecto Sentinel.
- Documentación oficial de Prometheus, Grafana, MLflow, Evidently y OpenTelemetry.

Las configuraciones y los umbrales específicos de Sentinel Observability son propuestas de diseño del proyecto y deberán contrastarse con las mediciones obtenidas durante la implementación.
