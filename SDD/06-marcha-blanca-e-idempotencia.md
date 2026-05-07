# Marcha Blanca e Idempotencia

Fecha de decision: `2026-05-06`

## Objetivo

Evitar que una nueva ejecucion del pipeline vuelva a insertar registros ya
existentes en el consolidado.

## Decision

Durante la marcha blanca, el pipeline no debe trabajar con reinyeccion completa
ni con sobreescritura total como comportamiento por defecto.

La estrategia recomendada es:

- carga incremental;
- lectura limitada a una ventana deslizante;
- validacion de duplicidad antes de escribir;
- insercion solo de registros nuevos;
- log de registros omitidos por duplicidad.

## Recomendacion operativa

### No recomendado

- Sobrescribir todo el consolidado en cada corrida.
- Inyectar solo "lo de hoy" de forma estricta.

### Recomendado

Procesar una ventana deslizante corta y validar duplicidad contra el destino.

Ventana sugerida para marcha blanca:

- `hoy - 3 dias` a `hoy`

Si el negocio suele corregir ventas atrasadas:

- ampliar a `7 dias`

## Implementacion de ventana

Desde `2026-05-06`, la ventana se aplica en dos niveles:

- filtro de fuentes por mes relevante;
- filtro de hojas por fecha exacta dentro del rango.

Configuracion actual:

- `PIPELINE_LOOKBACK_DAYS=3` por defecto
- `PIPELINE_RUN_DATE=<yyyy-mm-dd>` opcional para corridas controladas

## Por que no solo el dia actual

Inyectar solo el dia actual es rapido, pero tiene un riesgo alto:

- si alguien corrige una venta de ayer;
- si una hoja se completa tarde;
- si una venta se registra despues del cierre;
- si hubo una corrida fallida y se reintenta luego;

entonces esos datos pueden no entrar nunca.

Por eso, para una operacion automatica, suele ser mejor una ventana corta
deslizante con deduplicacion.

## Criterio de duplicidad

Se recomienda construir una clave de negocio deterministica por registro.

### Clave sugerida

La clave debe derivarse de campos estables del negocio:

- `fecha`
- `fuente`
- `documento`
- `hoja`
- `hora`
- `descripcion`
- `monto`
- `cliente`

Si `hora` o `cliente` vienen vacios en algunos casos, la clave puede seguir
siendo valida siempre que el conjunto restante identifique suficientemente la
venta.

### Regla

- Si la clave ya existe en destino, no se inserta el registro.
- Si la clave no existe, se agrega al consolidado.

## Implementacion adoptada

Desde `2026-05-06`, el pipeline opera con esta logica en `append`:

- lee los registros existentes del consolidado;
- construye una clave de negocio por fila;
- compara entradas nuevas contra el destino;
- omite duplicados existentes;
- omite duplicados repetidos dentro de la misma corrida;
- asigna `id registro` solo a filas efectivamente nuevas.
- reintenta lecturas ante fallos transitorios de Google Sheets como `429`,
  `500`, `502`, `503` y `504`.

## Flujo automatico recomendado

1. Leer fuentes de la ventana objetivo.
2. Normalizar registros.
3. Generar una `dedup_key` por fila.
4. Leer del destino solo las claves existentes de la misma ventana.
5. Comparar claves de entrada contra claves ya existentes.
6. Omitir duplicados.
7. Insertar solo filas nuevas.
8. Registrar metricas:
   - filas leidas
   - filas validas
   - filas duplicadas
   - filas nuevas insertadas

## Comportamiento esperado en una reejecucion

Si el script corre otra vez sobre el mismo rango:

- los registros ya presentes deben validarse;
- los duplicados deben omitirse;
- solo deben entrar filas nuevas o realmente faltantes.

En otras palabras: la reejecucion debe ser segura.

## Marcha blanca recomendada

### Etapa 1

- Mantener una corrida diaria o varias corridas al dia.
- Procesar una ventana de 3 dias.
- No usar `replace` como modo regular.
- Usar `append` con deduplicacion.

### Etapa 2

Despues de observar comportamiento real:

- reducir a 1 dia si nunca hay correcciones retroactivas;
- mantener 3 a 7 dias si hay ajustes frecuentes.

## Impacto sobre `id registro`

`id registro` ya no debe ser el criterio de deduplicacion.

Debe seguir siendo:

- un identificador tecnico del consolidado;
- asignado solo a filas efectivamente nuevas.

La deduplicacion debe basarse en la clave de negocio, no en el consecutivo.

## Campos adicionales recomendados

Para soportar esta estrategia, se recomienda agregar al esquema:

- `dedup_key`
- `fecha de actualizacion origen` si luego existe ese dato
- `estado de carga` en caso de auditoria futura

## Decision final

Para este proyecto, recomiendo:

- no sobreescribir en cada ejecucion;
- no limitarse solo al dia actual como unica estrategia;
- cargar una ventana deslizante corta;
- deduplicar automaticamente antes de insertar.

Esta es la opcion mas segura para una marcha blanca automatica.
