# Reglas de Negocio

## Esquema Canonico

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

## Reglas de Identificacion de Hojas

- Una hoja pertenece a la fuente si coincide con el `year` y `month` de la
  configuracion.
- Si el nombre contiene una fecha completa, se usa esa fecha.
- Si el nombre contiene solo el dia, se arma la fecha con `year` y `month`.
- Hojas auxiliares como `Resumen` deben omitirse.

## Reglas de Encabezados

- Se ignoran acentos, mayusculas y simbolos.
- Se reparan textos con mojibake cuando es posible.
- Se resuelven alias hacia un nombre canonico.
- Si existen columnas duplicadas, se distinguen por nombre unico de lectura.
- `Cliente 2` prevalece como `cliente` cuando corresponde al dato real.

## Reglas de Validacion

Una fila es venta valida solo si:

- tiene `descripcion` no vacia;
- tiene `monto` numerico mayor a cero;
- no representa una salida de caja.

## Reglas de Exclusion

Se excluyen:

- filas completamente vacias;
- filas con ruido residual sin venta real;
- filas con `monto` vacio, invalido o igual a cero;
- filas con texto `salida de caja` o `salidas de caja` en campos relevantes.

## Reglas de Normalizacion

- `nro` se recalcula por hoja usando solo ventas validas.
- `cantidad` vacia se reemplaza por `1`.
- `monto` y `monto sin igv` se transforman a decimal.
- `metodo de pago` se normaliza a mayusculas y variantes como `POS`.
- `hora` se convierte a formato `HH:MM:SS` cuando sea posible.
- `cliente` y `encargado` se normalizan como texto en mayusculas.
- `dni` y `telefono` quedan solo con digitos.
- `fecha de carga` refleja el momento de ejecucion del ETL.

## Reglas de Trazabilidad

- `fuente` identifica el bloque configurado en YAML.
- `documento` identifica el spreadsheet de origen.
- `hoja` identifica la pestana de origen.
- `id registro` es un consecutivo global solo para filas efectivamente nuevas.

## Regla de Duplicidad

La deduplicacion se basa en una clave de negocio construida con:

- `fecha`
- `fuente`
- `documento`
- `hoja`
- `hora`
- `descripcion`
- `monto`
- `cliente`
