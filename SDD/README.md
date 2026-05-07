# Software Design Description

Este directorio concentra la descripcion de diseno del pipeline `sales_yuler`
segun la arquitectura actual por capas y la logica de negocio consolidada.

## Indice

1. [Contexto y Objetivos](./01-contexto-y-objetivos.md)
2. [Arquitectura Logica](./02-arquitectura-logica.md)
3. [Reglas de Negocio](./03-reglas-de-negocio.md)
4. [Evaluacion de Celery](./04-evaluacion-celery.md)
5. [Roadmap Tecnico](./05-roadmap.md)
6. [Marcha Blanca e Idempotencia](./06-marcha-blanca-e-idempotencia.md)

## Criterios del Marco Actual

El diseno adopta estos criterios:

- Separacion estricta entre interfaces, aplicacion, dominio e infraestructura.
- Regla de negocio aislada del proveedor externo.
- Trazabilidad por registro, fuente, documento y hoja.
- Idempotencia como criterio obligatorio para la marcha blanca.
- Observabilidad y testabilidad como requisitos de ingenieria.
- Evolucion incremental hacia pipelines mas grandes sin reescribir el dominio.

## Estado operativo

Desde `2026-05-06`, la operacion automatica recomendada del proyecto es
`append` con deduplicacion previa al insert.
