# Sales Yuler ETL

ETL modular para consolidar ventas desde varios Google Sheets/Excel con muchas hojas diarias hacia una hoja maestra de Google Sheets consumible por Looker Studio.

## Flujo

1. Lee las fuentes declaradas en `config/sources.yml`.
2. Recorre todas las pestañas de cada documento.
3. Normaliza las columnas esperadas.
4. Agrega metadatos de trazabilidad.
5. Sobrescribe o anexa datos en una hoja maestra de Google Sheets.

## Columnas base

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

3. Instala dependencias:

```powershell
pip install -r requirements.txt
```

4. Ejecuta:

```powershell
python -m sales_yuler.cli run --mode replace
```

Para ejecutar pruebas:

```powershell
pip install -r requirements-dev.txt
python -m pytest tests
```

## Configuracion de fuentes

Edita `config/sources.yml`:

```yaml
sources:
  - name: ventas_2024_12
    url: "https://docs.google.com/spreadsheets/d/..."
    year: 2024
    month: 12
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
