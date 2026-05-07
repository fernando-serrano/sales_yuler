# Evaluacion de Celery

## Pregunta

Conviene usar Celery para las fases de normalizacion de registros?

## Respuesta Corta

No como siguiente paso inmediato.

Si puede contemplarse a futuro, pero no es la mejor primera inversion para el
estado actual del pipeline.

## Razones

### 1. El cuello de botella principal no es la normalizacion

La normalizacion actual es liviana y principalmente CPU-light:

- limpieza de texto;
- mapeo de columnas;
- parseo de fechas;
- parseo de montos;
- descarte de filas invalidas.

El costo dominante hoy esta mas cerca de:

- latencia de lectura contra Google Sheets;
- limites de cuota de la API;
- escritura final en la hoja consolidada;
- ausencia de carga incremental.

### 2. Celery introduce complejidad operativa

Celery agrega componentes nuevos:

- broker como Redis o RabbitMQ;
- workers;
- monitoreo de colas;
- manejo de reintentos distribuidos;
- problemas de orden, duplicacion e idempotencia.

Para un pipeline todavia lineal y de un solo destino, eso seria un salto grande
de complejidad respecto al valor inmediato.

### 3. La granularidad fila por fila seria un mal diseno

No conviene crear una tarea Celery por registro.

Si alguna vez se usa Celery, la unidad correcta deberia ser como minimo:

- por fuente;
- por documento;
- por hoja;
- por batch de hojas.

## Recomendacion Actual

Orden recomendado de evolucion:

1. Mantener la normalizacion dentro del proceso actual.
2. Introducir particionado logico por fuente y por hoja.
3. Agregar carga incremental e idempotencia.
4. Incorporar orquestacion del pipeline con Prefect, Dagster o Airflow.
5. Evaluar paralelizacion por fuente o por hoja.
6. Solo despues decidir si Celery es necesario.

## Decision

- Estado: aceptada para la version actual del proyecto.
- Decision: no incorporar Celery en esta fase.
