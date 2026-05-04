# Sales Yuler ETL

ETL modular para consolidar ventas desde varios Google Sheets/Excel con muchas hojas diarias hacia una hoja maestra de Google Sheets consumible por Looker Studio.

## Flujo

1. Lee las fuentes declaradas en `config/sources.yml`.
2. Recorre todas las pestañas de cada documento.
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

`id registro` es un consecutivo generado por el ETL para identificar cada fila del
consolidado. `nro` conserva el orden original que viene de cada hoja fuente.

## Normalizacion de ventas

La fuente puede tener columnas con nombres distintos o duplicados. Para la primera prueba se espera este formato de entrada:

```text
N° | Cliente | Cantidad de productos | Descripción / Productos | Tipo de Joya | Tipo de Material | MONTO | Monto (Sin I.G.V) | Método de Pago | Hora | Cliente | DNI | Teléfono | Encargado | Salidas de caja
```

Reglas aplicadas:

- `N°` se normaliza como `nro`.
- `Cantidad de productos` se normaliza como `cantidad`.
- `Descripción / Productos` se normaliza como `descripcion`.
- `MONTO` se normaliza como `monto`.
- `Monto (Sin I.G.V)` se normaliza como `monto sin igv`.
- Si hay dos columnas `Cliente`, se toma la segunda como el `cliente` de la venta.
- Las filas vacias se omiten.
- Las filas marcadas como `Salidas de caja` se omiten porque no son ventas.

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
```

3. Crea un entorno virtual `.venv`:

```powershell
python -m venv .venv
```

4. Activa el entorno virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activacion por politicas de ejecucion, habilitala solo para esta sesion:

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

El correo esta dentro del archivo configurado en `GOOGLE_SERVICE_ACCOUNT_FILE`, en el campo `client_email`. Debe tener permiso de lectura sobre las fuentes y permiso de edicion sobre la hoja destino.

7. Ejecuta:

```powershell
python -m sales_yuler run --mode replace
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
  - name: ventas_prueba_2026_05
    url: "https://docs.google.com/spreadsheets/d/1Lvr6Zy-tDtHlpUQFBKlgM1iY8FM4r8l6Vn6-tGVVHvQ/edit?gid=1552053166#gid=1552053166"
    year: 2026
    month: 5
    enabled: true
```

Si cada pestaña se llama `1`, `01`, `15`, etc., el ETL construye la fecha usando `year`, `month` y el nombre de la hoja.

## GitHub Actions

Configura estos secrets en GitHub:

- `GOOGLE_SERVICE_ACCOUNT_JSON`
- `TARGET_SPREADSHEET_ID`
- `TARGET_WORKSHEET_NAME`

Para GitHub Actions no subas el archivo `secrets/*.json`. Copia el contenido completo del JSON de la cuenta de servicio en el secret `GOOGLE_SERVICE_ACCOUNT_JSON`.

El workflow `.github/workflows/sync-sales.yml` corre diariamente y tambien puede ejecutarse manualmente.
