# Contexto y Objetivos

## Problema

El negocio consolida ventas registradas en multiples Google Sheets con hojas
diarias heterogeneas. Las fuentes presentan diferencias de encabezados, ruido
manual, errores de formato y registros no validos como salidas de caja.

## Objetivo del Pipeline

Construir un ETL confiable que:

- lea fuentes declaradas en configuracion;
- detecte hojas validas del periodo objetivo;
- normalice encabezados y valores;
- descarte filas no validas;
- agregue trazabilidad de origen;
- cargue un consolidado listo para consumo analitico.

## Objetivos de Diseno

- Minimizar acoplamiento con Google Sheets.
- Mantener la logica de negocio separada de la orquestacion.
- Permitir crecimiento hacia orquestadores externos.
- Facilitar pruebas unitarias sobre reglas de negocio.
- Hacer explicitas las decisiones tecnicas para futuras refactorizaciones.

## No Objetivos Actuales

- No se implementa aun almacenamiento intermedio persistente.
- No se implementa aun particionado fisico por fecha.
- No se introduce aun un broker distribuido ni workers asincronos.
