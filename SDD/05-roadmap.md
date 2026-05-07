# Roadmap Técnico

## Fase 1. Base actual endurecida

- Mantener arquitectura por capas.
- Consolidar documentación de diseño.
- Asegurar cobertura de pruebas del dominio.
- Corregir codificación y calidad de logs donde aplique.

## Fase 2. Pipeline más serio de datos

- Introducir `pipelines/` si aparecen más casos de uso.
- Crear modelo de partición por `fuente`, `year`, `month`, `hoja`.
- Agregar checkpoints o watermark de ejecución.
- Diseñar estrategia de idempotencia para `append`.

## Fase 3. Observabilidad

- Métricas por fuente, hoja y filas válidas.
- Conteos de filas descartadas por motivo.
- Alertas por fallos de extracción o escritura.
- Reporte de calidad de datos por corrida.

## Fase 4. Persistencia intermedia

- Agregar zona `raw/` para extracción cruda.
- Agregar zona `staging/` para datos normalizados.
- Agregar zona `marts/` para salidas analíticas.

## Fase 5. Orquestación

- Elegir Prefect, Dagster o Airflow según escala operativa.
- Separar definición del job de la lógica del dominio.
- Introducir reejecución por partición.

## Fase 6. Paralelización

- Medir tiempos por fase.
- Paralelizar por fuente o por hoja si el volumen lo justifica.
- Evaluar Celery solo si el paralelismo distribuido ya es una necesidad real.
