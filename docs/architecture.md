# Arquitectura Propuesta

## Capas

- `sales_yuler/interfaces/`: puntos de entrada, CLI y futuros triggers.
- `sales_yuler/application/`: orquestación del pipeline y casos de uso.
- `sales_yuler/domain/`: reglas de negocio, esquema canónico y normalización.
- `sales_yuler/infrastructure/`: adaptadores externos como Google Sheets y carga de configuración.

## Estructura Actual Recomendada

```text
sales_yuler/
  application/
  domain/
    sales/
  infrastructure/
    google/
  interfaces/
```

## Siguiente Evolución Recomendada

- Agregar `pipelines/` si van a coexistir múltiples pipelines de negocio.
- Separar `raw`, `staging` y `marts` si luego almacenan datasets intermedios.
- Incorporar `orchestration/` para jobs de Airflow, Dagster o Prefect.
- Incorporar `observability/` para métricas, alertas y data quality checks.

## Diseño Formal

La documentación de diseño detallada vive en `SDD/`:

- `SDD/README.md`
- `SDD/01-contexto-y-objetivos.md`
- `SDD/02-arquitectura-logica.md`
- `SDD/03-reglas-de-negocio.md`
- `SDD/04-evaluacion-celery.md`
- `SDD/05-roadmap.md`
