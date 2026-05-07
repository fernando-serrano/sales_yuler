# Roadmap Tecnico

## Fase 1. Base actual endurecida

- Mantener arquitectura por capas.
- Consolidar documentacion de diseno.
- Asegurar cobertura de pruebas del dominio.
- Corregir codificacion y calidad de logs donde aplique.

## Fase 2. Pipeline mas serio de datos

- Introducir `pipelines/` si aparecen mas casos de uso.
- Crear modelo de particion por `fuente`, `year`, `month`, `hoja`.
- Agregar checkpoints o watermark de ejecucion.
- Implementar clave de deduplicacion e idempotencia para `append`.
- Procesar una ventana deslizante de 3 a 7 dias en marcha blanca.

## Fase 3. Observabilidad

- Metricas por fuente, hoja y filas validas.
- Conteos de filas descartadas por motivo.
- Conteos de filas duplicadas omitidas.
- Alertas por fallos de extraccion o escritura.
- Reporte de calidad de datos por corrida.

## Fase 4. Persistencia intermedia

- Agregar zona `raw/` para extraccion cruda.
- Agregar zona `staging/` para datos normalizados.
- Agregar zona `marts/` para salidas analiticas.

## Fase 5. Orquestacion

- Elegir Prefect, Dagster o Airflow segun escala operativa.
- Separar definicion del job de la logica del dominio.
- Introducir reejecucion por particion.

## Fase 6. Paralelizacion

- Medir tiempos por fase.
- Paralelizar por fuente o por hoja si el volumen lo justifica.
- Evaluar Celery solo si el paralelismo distribuido ya es una necesidad real.
