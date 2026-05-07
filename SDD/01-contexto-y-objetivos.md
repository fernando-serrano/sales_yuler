# Contexto y Objetivos

## Problema

El negocio consolida ventas registradas en múltiples Google Sheets con hojas
diarias heterogéneas. Las fuentes presentan diferencias de encabezados, ruido
manual, errores de formato y registros no válidos como salidas de caja.

## Objetivo del Pipeline

Construir un ETL confiable que:

- lea fuentes declaradas en configuración;
- detecte hojas válidas del mes objetivo;
- normalice encabezados y valores;
- descarte filas no válidas;
- agregue trazabilidad de origen;
- cargue un consolidado listo para consumo analítico.

## Objetivos de Diseño

- Minimizar acoplamiento con Google Sheets.
- Mantener la lógica de negocio separada de la orquestación.
- Permitir crecimiento hacia orquestadores externos.
- Facilitar pruebas unitarias sobre reglas de negocio.
- Hacer explícitas las decisiones técnicas para futuras refactorizaciones.

## No Objetivos Actuales

- No se implementa aún almacenamiento intermedio persistente.
- No se implementa aún particionado físico por fecha.
- No se implementa aún carga incremental idempotente.
- No se introduce aún un broker distribuido ni workers asíncronos.
