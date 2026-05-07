# Sales Yuler ETL

ETL modular para consolidar ventas desde varios Google Sheets/Excel con muchas hojas diarias hacia una hoja maestra de Google Sheets consumible por Looker Studio.

## Documentacion de diseno

La documentacion formal de arquitectura y diseno vive en:

- `docs/architecture.md`
- `SDD/README.md`

## Modo operativo actual

Desde el `2026-05-06`, el modo recomendado para ejecucion automatica es
`append` con validacion de duplicados.

Esto significa:

- el pipeline ya no debe sobreescribir el consolidado en cada corrida;
- los registros existentes se validan antes de insertar;
- solo se agregan filas nuevas;
- `replace` queda reservado para recuperacion o reprocesos controlados.

Ademas, desde el `2026-05-06`, la lectura opera con una ventana deslizante para
evitar reprocesar meses completos innecesariamente.

- valor por defecto: `hoy - 3 dias` a `hoy`
- variable configurable: `PIPELINE_LOOKBACK_DAYS`
- fecha de referencia configurable: `PIPELINE_RUN_DATE`

## Flujo

1. Lee las fuentes declaradas en `config/sources.yml`.
2. Recorre todas las pestanas de cada documento.
3. Normaliza las columnas esperadas.
4. Agrega metadatos de trazabilidad.
5. Sobrescribe o anexa datos en una hoja maestra de Google Sheets.

## Columnas base

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

El proceso tambien agrega:

- `fecha`
- `fuente`
- `documento`
- `hoja`
- `fecha de carga`

`id registro` es un consecutivo global generado por el ETL para identificar cada
fila nueva del consolidado. `nro` es el correlativo de ventas validas dentro de
cada dia/pestana.

## Normalizacion de ventas

La fuente puede tener columnas con nombres distintos, acentos, mayusculas,
simbolos o columnas duplicadas. El ETL primero traduce los encabezados al esquema
canonico y luego aplica reglas de validacion, limpieza y trazabilidad.

Formato de entrada esperado en las hojas de ventas:

```text
Nro | Cliente | Cantidad de productos | Descripcion / Productos | Tipo de Joya | Tipo de Material | MONTO | Monto (Sin I.G.V) | Metodo de Pago | Hora | Cliente | DNI | Telefono | Encargado | Salidas de caja
```

### 1. Estandarizacion de columnas

Los encabezados se limpian antes de mapearlos: se ignoran acentos, mayusculas,
simbolos y espacios repetidos. Luego se convierten a estos campos canonicos:

| Entrada posible | Campo canonico |
| --- | --- |
| `Nro`, `nro`, `nro.`, `numero` | `nro` |
| `Cantidad de productos`, `cantidad productos` | `cantidad` |
| `Descripcion / Productos`, `descripcion productos` | `descripcion` |
| `Tipo de Joya`, `tipo joya` | `tipo de joya` |
| `Tipo de Material`, `tipo material` | `tipo de material` |
| `MONTO`, `monto` | `monto` |
| `Monto (Sin I.G.V)`, `monto sin igv` | `monto sin igv` |
| `Metodo de Pago`, `metodo de pago` | `metodo de pago` |
| `Cliente` | `cliente` |
| `DNI` | `dni` |
| `Telefono` | `telefono` |
| `Encargado` | `encargado` |

Si una hoja trae dos columnas llamadas `Cliente`, Google Sheets las lee como
`Cliente` y `Cliente 2`; el ETL toma `Cliente 2` como el `cliente` final de la
venta.

### 2. Validacion de ventas

Una fila solo se considera venta valida si cumple estas condiciones:

- Tiene `descripcion` con texto.
- Tiene `monto` numerico mayor a `0`.
- No esta marcada como `Salidas de caja`.

Se omiten automaticamente:

- Filas completamente vacias.
- Filas con solo datos residuales, por ejemplo `cliente = 0` pero sin
  `descripcion` ni `monto`.
- Filas con `monto` vacio, no numerico o igual a `0`.
- Filas donde aparezca `salida de caja` o `salidas de caja` en `descripcion`,
  `cliente`, `metodo de pago` o `encargado`.

### 3. Normalizacion de valores

Reglas por campo:

- `nro`: se recalcula despues del filtro de ventas validas. Empieza en `1` para
  cada dia/pestana y aumenta solo por ventas validas.
- `cantidad`: si viene vacia, se asume `1`.
- `monto`: se convierte a numero decimal. Ejemplos: `S/.120,00` -> `120.0`,
  `S/ 118.00` -> `118.0`.
- `monto sin igv`: se convierte a numero decimal con la misma regla de `monto`.
- `dni` y `telefono`: se guardan como texto limpio, sin espacios externos.

### 4. Normalizacion de fechas

`fecha` representa la fecha de la venta. Se infiere desde el nombre de la
pestana y siempre se guarda en formato `dd/mm/aaaa`.

Formatos aceptados:

| Nombre de pestana | Resultado en `fecha` |
| --- | --- |
| `1`, `01` con `year: 2026` y `month: 2` | `01/02/2026` |
| `1/5/26` | `01/05/2026` |
| `01/05/2026` | `01/05/2026` |
| `1-05-2026` | `01/05/2026` |
| `2026-02-01` | `01/02/2026` |
| `2026-02-20` | `20/02/2026` |

Si la pestana solo tiene el dia (`1`, `01`, `15`, etc.), el ETL usa `year` y
`month` desde `config/sources.yml`. Si la pestana trae una fecha completa, el ETL
usa esa fecha completa.

Antes de leer una pestana, el ETL valida que pertenezca al mes configurado para
la fuente. Por ejemplo, en una fuente con `year: 2026` y `month: 1`, se procesan
`1`, `31`, `1/01/2026` o `2026-01-31`, pero se omiten `1/02/2026`,
`2026-02-01`, `29` si el mes no tiene 29 dias, y pestanas auxiliares como
`Resumen`.

`fecha de carga` no es la fecha de venta. Es el momento exacto en que el ETL
cargo el registro al consolidado.

### 5. Identificadores y trazabilidad

- `id registro`: correlativo global del consolidado completo. Se asigna al final
  del proceso.
- `nro`: correlativo diario dentro de cada pestana, calculado solo con ventas
  validas.
- `fuente`: nombre de la fuente en `config/sources.yml`.
- `documento`: titulo del Google Sheet de origen.
- `hoja`: nombre de la pestana de origen.
- `fecha de carga`: fecha y hora de ejecucion del ETL.

### 6. Deteccion de duplicados

En modo `append`, el ETL compara cada fila normalizada contra los registros ya
existentes en la hoja destino.

La validacion usa una clave de negocio derivada de:

- `fecha`
- `fuente`
- `documento`
- `hoja`
- `hora`
- `descripcion`
- `monto`
- `cliente`

Si un registro ya existe, se omite. Si no existe, se inserta y recibe un nuevo
`id registro`.

La hoja destino debe tener estos campos:

```text
id registro | nro | cantidad | descripcion | tipo de joya | tipo de material | monto | monto sin igv | metodo de pago | hora | cliente | dni | telefono | encargado
```

## Configuracion local

1. Copia el archivo de ejemplo:

```powershell
Copy-Item .env.example .env
```

2. Completa tus variables:

```env
GOOGLE_SERVICE_ACCOUNT_FILE=secrets/ventas-joyas-bot-a7644f88f7d0.json
TARGET_SPREADSHEET_ID=1AMGRZ9vdJPXTHCvPLdu9Q954CkWU2tdsZ6VicGmGAbo
TARGET_WORKSHEET_NAME=ventas_consolidado
PIPELINE_LOOKBACK_DAYS=3
```

3. Crea un entorno virtual `.venv`:

```powershell
python -m venv .venv
```

4. Activa el entorno virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activacion por politicas de ejecucion, habilitala solo
para esta sesion:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\.venv\Scripts\Activate.ps1
```

Cuando el entorno este activo, deberias ver `(.venv)` al inicio de la terminal.

5. Instala dependencias:

```powershell
python -m pip install -r requirements.txt
```

6. Comparte los Google Sheets con el correo de la cuenta de servicio.

El correo esta dentro del archivo configurado en `GOOGLE_SERVICE_ACCOUNT_FILE`,
en el campo `client_email`. Debe tener permiso de lectura sobre las fuentes y
permiso de edicion sobre la hoja destino.

7. Ejecuta:

```powershell
python -m sales_yuler run
```

El modo por defecto es `append`. Si necesitas rehacer completamente la hoja
destino, puedes usar:

```powershell
python -m sales_yuler run --mode replace
```

Para una corrida controlada con fecha fija y ventana explicita:

```powershell
$env:PIPELINE_RUN_DATE="2026-05-06"
$env:PIPELINE_LOOKBACK_DAYS="3"
python -m sales_yuler run
```

Cada ejecucion crea una carpeta en `logs/` con el formato `dd-mm-aaaa hh-mm-ss`
y un archivo `sales_yuler.log`. Se conservan como maximo 10 carpetas de logs;
cuando se crea la onceava, se elimina la mas antigua.

Para ejecutar pruebas:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest tests
```

## Configuracion de fuentes

Edita `config/sources.yml`:

```yaml
sources:
  - name: ventas_2026_01
    url: "https://docs.google.com/spreadsheets/d/REEMPLAZAR/edit"
    year: 2026
    month: 1
    enabled: true
  - name: ventas_2026_02
    url: "https://docs.google.com/spreadsheets/d/REEMPLAZAR/edit"
    year: 2026
    month: 2
    enabled: true
```

Si cada pestana se llama `1`, `01`, `15`, etc., el ETL construye la fecha usando
`year`, `month` y el nombre de la hoja. Si el nombre de la pestana trae una fecha
completa como `1/5/26`, `01/05/2026`, `1/05/2026` o `2026-02-20`, el ETL la
normaliza a `dd/mm/aaaa`.

## GitHub Actions

Configura estos secrets en GitHub:

- `GOOGLE_SERVICE_ACCOUNT_JSON`
- `TARGET_SPREADSHEET_ID`
- `TARGET_WORKSHEET_NAME`

Para GitHub Actions no subas el archivo `secrets/*.json`. Copia el contenido
completo del JSON de la cuenta de servicio en el secret
`GOOGLE_SERVICE_ACCOUNT_JSON`.

El workflow `.github/workflows/sync-sales.yml` corre diariamente y tambien puede
ejecutarse manualmente. Su modo recomendado es `append`.
