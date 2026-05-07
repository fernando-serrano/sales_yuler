# Evaluación de Celery

## Pregunta

¿Conviene usar Celery para las fases de normalización de registros?

## Respuesta Corta

No como siguiente paso inmediato.

Sí puede contemplarse a futuro, pero no es la mejor primera inversión para el
estado actual del pipeline.

## Razones

### 1. El cuello de botella principal no es la normalización

La normalización actual es liviana y principalmente CPU-light:

- limpieza de texto;
- mapeo de columnas;
- parseo de fechas;
- parseo de montos;
- descarte de filas inválidas.

El costo dominante hoy está más cerca de:

- latencia de lectura contra Google Sheets;
- límites de cuota de la API;
- escritura final en la hoja consolidada;
- ausencia de carga incremental.

### 2. Celery introduce complejidad operativa

Celery agrega componentes nuevos:

- broker como Redis o RabbitMQ;
- workers;
- monitoreo de colas;
- manejo de reintentos distribuidos;
- problemas de orden, duplicación e idempotencia.

Para un pipeline todavía lineal y de un solo destino, eso sería un salto grande
de complejidad respecto al valor inmediato.

### 3. La granularidad fila por fila sería un mal diseño

No conviene crear una tarea Celery por registro:

- aumenta demasiado el overhead;
- dificulta el orden y el cálculo de `nro` por hoja;
- complica la trazabilidad;
- hace más frágil la recomposición del dataset final.

Si alguna vez se usa Celery, la unidad correcta sería como mínimo:

- por fuente;
- por documento;
- por hoja;
- o por batch de hojas.

## Cuándo Sí Empezaría a Tener Sentido

Celery empieza a ser razonable si se cumplen varios de estos puntos:

- decenas o cientos de fuentes simultáneas;
- necesidad de procesar documentos en paralelo;
- integración con más sistemas además de Google Sheets;
- SLA de procesamiento más exigente;
- colas de trabajo persistentes y reintentos por unidad de negocio;
- infraestructura ya preparada con Redis o RabbitMQ.

## Recomendación Actual

Orden recomendado de evolución:

1. Mantener la normalización dentro del proceso actual.
2. Introducir particionado lógico por fuente y por hoja.
3. Agregar carga incremental e idempotencia.
4. Incorporar orquestación del pipeline con Prefect, Dagster o Airflow.
5. Evaluar paralelización por fuente o por hoja.
6. Solo después decidir si Celery es necesario.

## Alternativas Más Adecuadas Antes que Celery

### Opción A: Paralelismo local controlado

Usar `concurrent.futures` o multiprocessing por fuente o por hoja para
paralelizar trabajo independiente sin introducir broker distribuido.

### Opción B: Orquestación externa

Usar Prefect, Dagster o Airflow para:

- scheduling;
- retries;
- observabilidad;
- reejecución por partición;
- separación entre coordinación y ejecución.

### Opción C: Batch staging

Persistir extracción en una zona intermedia y normalizar desde ahí. Esto suele
dar más valor que distribuir workers demasiado pronto.

## Decisión

### Estado

Aceptada para la versión actual del proyecto.

### Decisión

No incorporar Celery en esta fase.

### Revisión futura

Reevaluar cuando exista:

- carga incremental;
- particionado por fuente/hoja;
- métricas de volumen y tiempos reales;
- necesidad comprobada de paralelismo distribuido.
