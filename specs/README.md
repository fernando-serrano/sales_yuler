# Especificación de Sistema

Documentación técnica y de diseño del pipeline `sales_yuler`.

## Estructura de Documentación

### [00 - Visión General](./00-overview/README.md)
Propósito del proyecto, principios y guía de navegación de documentos.

### [01 - Objetivos y Contexto](./01-objetivos/README.md)
Contexto del negocio, alcance, requisitos funcionales y no funcionales.

### [02 - Arquitectura](./02-arquitectura/README.md)
Diseño de capas, componentes, responsabilidades y relaciones entre módulos.

### [03 - Dominio y Reglas de Negocio](./03-dominio/README.md)
Lógica de negocio, entidades, invariantes y criterios del dominio.

### [04 - Especificación de Módulos](./04-modulos/README.md)
Descripción detallada de cada módulo: responsabilidades, interfaces, flujos.

### [05 - Infraestructura y Herramientas](./05-infraestructura/README.md)
APIs externas, cuotas técnicas, restricciones, decisiones de herramientas.

### [06 - Operación e Idempotencia](./06-operacion/README.md)
Marcha blanca, criterios de idempotencia, estrategias de despliegue.

### [07 - Roadmap y Avances](./07-roadmap/README.md)
Estado del proyecto, hitos completados, evolucion esperada y mejoras futuras.

## Cómo Navegar

- Para entender QUÉ hacemos: `01-objetivos/`
- Para entender CÓMO lo hacemos: `02-arquitectura/` + `04-modulos/`
- Para entender LAS REGLAS: `03-dominio/`
- Para entender RESTRICCIONES: `05-infraestructura/`
- Para entender OPERACIÓN: `06-operacion/`
- Para ver PROGRESO: `07-roadmap/`

## Criterios del Marco de Diseño

✓ Separación estricta entre interfaces, aplicación, dominio e infraestructura
✓ Reglas de negocio independientes del proveedor (Google Sheets)
✓ Trazabilidad completa por registro, fuente, documento y hoja
✓ Idempotencia como requisito obligatorio
✓ Observabilidad integrada en toda la cadena
✓ Testabilidad de lógica sin dependencias externas
✓ Evolución incremental sin reescritura de dominio

## Estado Actual

**Última actualización**: 2026-05-15  
**Modo de operación recomendado**: Append con deduplicación previa  
**Ventana de lectura**: Deslizante (rolling window)
