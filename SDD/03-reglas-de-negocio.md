# Reglas de Negocio

## Esquema Canónico

Campos base:

- `id registro`
- `nro`
- `cantidad`
- `descripcion`
- `tipo de joya`
- `tipo de material`
- `monto`
- `monto sin igv`
- `metodo de pago`
- `hora`
- `cliente`
- `dni`
- `telefono`
- `encargado`
- `fecha`
- `fuente`
- `documento`
- `hoja`
- `fecha de carga`

## Reglas de Identificación de Hojas

- Una hoja pertenece a la fuente si coincide con el `year` y `month` de la
  configuración.
- Si el nombre contiene una fecha completa, se usa esa fecha.
- Si el nombre contiene solo el día, se arma la fecha con `year` y `month`.
- Hojas auxiliares como `Resumen` deben omitirse.

## Reglas de Encabezados

- Se ignoran acentos, mayúsculas y símbolos.
- Se reparan textos con mojibake cuando es posible.
- Se resuelven alias hacia un nombre canónico.
- Si existen columnas duplicadas, se distinguen por nombre único de lectura.
- `Cliente 2` prevalece como `cliente` cuando corresponde al dato real.

## Reglas de Validación

Una fila es venta válida solo si:

- tiene `descripcion` no vacía;
- tiene `monto` numérico mayor a cero;
- no representa una salida de caja.

## Reglas de Exclusión

Se excluyen:

- filas completamente vacías;
- filas con ruido residual sin venta real;
- filas con `monto` vacío, inválido o igual a cero;
- filas con texto `salida de caja` o `salidas de caja` en campos relevantes.

## Reglas de Normalización

- `nro` se recalcula por hoja usando solo ventas válidas.
- `cantidad` vacía se reemplaza por `1`.
- `monto` y `monto sin igv` se transforman a decimal.
- `metodo de pago` se normaliza a mayúsculas y variantes como `POS`.
- `hora` se convierte a formato `HH:MM:SS` cuando sea posible.
- `cliente` y `encargado` se normalizan como texto en mayúsculas.
- `dni` y `telefono` quedan solo con dígitos.
- `fecha de carga` refleja el momento de ejecución del ETL.

## Reglas de Trazabilidad

- `fuente` identifica el bloque configurado en YAML.
- `documento` identifica el spreadsheet de origen.
- `hoja` identifica la pestaña de origen.
- `id registro` es un consecutivo global del consolidado.
