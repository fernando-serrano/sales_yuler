# Arquitectura propuesta

## Capas

- `sales_yuler/interfaces/`: puntos de entrada, CLI y futuros triggers.
- `sales_yuler/application/`: orquestación del pipeline y casos de uso.
- `sales_yuler/domain/`: reglas de negocio, esquema canónico y normalización.
- `sales_yuler/infrastructure/`: adaptadores externos como Google Sheets y carga de configuración.

## Estructura actual recomendada

```text
sales_yuler/
  application/
  domain/
    sales/
  infrastructure/
    google/
  interfaces/
```

## Siguiente evolución recomendada

- Agregar `pipelines/` si van a coexistir múltiples pipelines de negocio.
- Separar `raw`, `staging` y `marts` si luego almacenan datasets intermedios.
- Incorporar `orchestration/` para jobs de Airflow, Dagster o Prefect.
- Incorporar `observability/` para métricas, alertas y data quality checks.
