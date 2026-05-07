# Software Design Description

Este directorio concentra la descripción de diseño del pipeline `sales_yuler`
según la arquitectura actual por capas y la lógica de negocio consolidada.

## Índice

1. [Contexto y Objetivos](./01-contexto-y-objetivos.md)
2. [Arquitectura Lógica](./02-arquitectura-logica.md)
3. [Reglas de Negocio](./03-reglas-de-negocio.md)
4. [Evaluación de Celery](./04-evaluacion-celery.md)
5. [Roadmap Técnico](./05-roadmap.md)

## Criterios del Marco Actual

El diseño adopta estos criterios:

- Separación estricta entre interfaces, aplicación, dominio e infraestructura.
- Regla de negocio aislada del proveedor externo.
- Trazabilidad por registro, fuente, documento y hoja.
- Idempotencia como criterio deseable de evolución.
- Observabilidad y testabilidad como requisitos de ingeniería.
- Evolución incremental hacia pipelines más grandes sin reescribir el dominio.
