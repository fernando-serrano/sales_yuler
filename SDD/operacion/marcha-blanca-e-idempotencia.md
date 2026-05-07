# Marcha Blanca e Idempotencia

Fecha de decision: `2026-05-06`

## Objetivo

Evitar que una nueva ejecucion del pipeline vuelva a insertar registros ya
existentes en el consolidado.

## Decision

Durante la marcha blanca, el pipeline no debe trabajar con reinyeccion completa
ni con sobreescritura total como comportamiento por defecto.

La estrategia adoptada es:

- carga incremental;
- lectura limitada a una ventana deslizante;
- validacion de duplicidad antes de escribir;
- insercion solo de registros nuevos;
- log de registros omitidos por duplicidad.

## Ventana de Procesamiento

Ventana sugerida:

- `hoy - 3 dias` a `hoy`

Si el negocio suele corregir ventas atrasadas:

- ampliar a `7 dias`

## Implementacion de Ventana

Desde `2026-05-06`, la ventana se aplica en dos niveles:

- filtro de fuentes por mes relevante;
- filtro de hojas por fecha exacta dentro del rango.

Configuracion actual:

- `PIPELINE_LOOKBACK_DAYS=3` por defecto
- `PIPELINE_RUN_DATE=<yyyy-mm-dd>` opcional para corridas controladas

## Por Que No Solo el Dia Actual

Inyectar solo el dia actual es rapido, pero tiene riesgo alto si:

- alguien corrige una venta de ayer;
- una hoja se completa tarde;
- una venta se registra despues del cierre;
- hubo una corrida fallida y se reintenta luego.

Por eso, para una operacion automatica, es mejor una ventana corta deslizante
con deduplicacion.

## Criterio de Duplicidad

- Si la clave ya existe en destino, no se inserta el registro.
- Si la clave no existe, se agrega al consolidado.

## Implementacion Adoptada

Desde `2026-05-06`, el pipeline opera con esta logica en `append`:

- lee los registros existentes del consolidado;
- construye una clave de negocio por fila;
- compara entradas nuevas contra el destino;
- omite duplicados existentes;
- omite duplicados repetidos dentro de la misma corrida;
- asigna `id registro` solo a filas efectivamente nuevas;
- reintenta lecturas ante fallos transitorios de Google Sheets como `429`,
  `500`, `502`, `503` y `504`.

## Flujo Automatico Recomendado

1. Leer fuentes de la ventana objetivo.
2. Normalizar registros.
3. Generar `dedup_key` por fila.
4. Leer claves existentes del mismo rango en destino.
5. Omitir duplicados.
6. Insertar solo filas nuevas.
7. Registrar metricas operativas.

## Decision Final

Para este proyecto, se recomienda:

- no sobreescribir en cada ejecucion;
- no limitarse solo al dia actual como unica estrategia;
- cargar una ventana deslizante corta;
- deduplicar automaticamente antes de insertar.

## Despliegue en GitHub Actions

Para la operacion automatica en GitHub Actions:

- el workflow debe ejecutar pruebas antes del ETL en corridas manuales;
- el ETL debe correr en modo `append`;
- la ventana debe ser configurable por variables;
- las corridas no deben solaparse sobre la misma rama.

## Ventana Horaria de Ejecucion

Desde `2026-05-06`, la automatizacion en GitHub Actions queda limitada al
rango de negocio:

- `10:00` a `22:30`
- zona horaria `America/Lima`
- frecuencia `cada 30 minutos`

Implementacion:

- planificacion `cron` en `UTC`;
- validacion adicional de horario en el propio workflow;
- posibilidad de excepcion manual con `force_run=true`.
