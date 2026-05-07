# SDD

Este directorio concentra la documentacion de diseno del pipeline
`sales_yuler`, organizada por aspectos funcionales y tecnicos.

## Estructura

- [objetivos/](./objetivos/README.md)
  Contexto, alcance y objetivos del pipeline.
- [arquitectura/](./arquitectura/README.md)
  Arquitectura logica, capas y responsabilidades.
- [logica-negocio/](./logica-negocio/README.md)
  Reglas de negocio y criterios del dominio.
- [operacion/](./operacion/README.md)
  Marcha blanca, idempotencia y operacion automatica.
- [herramientas-reglas/](./herramientas-reglas/README.md)
  Restricciones tecnicas, cuotas, herramientas y decisiones.
- [avances/](./avances/README.md)
  Roadmap, estado y evolucion esperada.

## Criterios del marco actual

- Separacion estricta entre interfaces, aplicacion, dominio e infraestructura.
- Regla de negocio aislada del proveedor externo.
- Trazabilidad por registro, fuente, documento y hoja.
- Idempotencia como criterio obligatorio para la marcha blanca.
- Observabilidad y testabilidad como requisitos de ingenieria.
- Evolucion incremental hacia pipelines mas grandes sin reescribir el dominio.

## Estado operativo

Desde `2026-05-06`, la operacion automatica recomendada del proyecto es
`append` con deduplicacion previa al insert y ventana deslizante de lectura.
