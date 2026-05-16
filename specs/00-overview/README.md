# Visión General del Proyecto

Este documento proporciona una visión general del proyecto `sales_yuler`,
su propósito, contexto y cómo se estructura la documentación técnica.

## Propósito del Proyecto

`sales_yuler` es un pipeline de extracción, transformación y carga (ETL) 
de datos de ventas de joyas desde Google Sheets hacia un almacén centralizado.

## Principios Rectores

- **Separación de capas**: Interfaces → Aplicación → Dominio → Infraestructura
- **Independencia del dominio**: Reglas de negocio aisladas de proveedores externos
- **Idempotencia obligatoria**: Garantizar operación segura y repetible
- **Observabilidad**: Trazabilidad completa de datos desde origen hasta destino
- **Testabilidad**: Lógica verificable independientemente de dependencias externas

## Cómo Usar Esta Documentación

Consulta los subdirectorios según tu rol:

- **Analista / Product Owner**: Comienza en `01-objetivos/`
- **Arquitecto / Tech Lead**: Revisa `02-arquitectura/` y `03-dominio/`
- **Ingeniero Backend**: Estudia `03-dominio/`, `04-modulos/` e `05-infraestructura/`
- **DevOps / SRE**: Ve a `06-operacion/` e `05-infraestructura/`
- **Gestor de Proyecto**: Consulta `07-roadmap/`
