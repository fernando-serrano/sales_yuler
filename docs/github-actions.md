# Guia de Configuracion de GitHub Actions

## Objetivo

Esta guia explica como dejar operativo el workflow de `sales_yuler` en GitHub
Actions para ejecutar el ETL de forma automatica y segura.

## Archivo del workflow

El workflow principal del proyecto vive en:

- `.github/workflows/sync-sales.yml`

## Requisitos previos

Antes de activar GitHub Actions, verifica:

- el repositorio ya contiene el workflow actualizado;
- la cuenta de servicio de Google existe y su JSON es valido;
- la cuenta de servicio tiene acceso de lectura a las fuentes;
- la cuenta de servicio tiene acceso de edicion a la hoja destino;
- el `TARGET_SPREADSHEET_ID` corresponde al consolidado correcto.

## Secrets requeridos

Configura estos secrets en GitHub:

- `GOOGLE_SERVICE_ACCOUNT_JSON`
- `TARGET_SPREADSHEET_ID`
- `TARGET_WORKSHEET_NAME`

### Como configurarlos

1. Entra al repositorio en GitHub.
2. Abre `Settings`.
3. En el menu lateral, entra a `Secrets and variables`.
4. Abre `Actions`.
5. Crea cada secret con `New repository secret`.

## Valor esperado de cada secret

### `GOOGLE_SERVICE_ACCOUNT_JSON`

Debe contener el contenido completo del JSON de la cuenta de servicio.

No pongas la ruta del archivo. Debe ser el JSON completo copiado como texto.

### `TARGET_SPREADSHEET_ID`

Debe contener solo el identificador del Google Sheet destino.

Ejemplo:

```text
1AMGRZ9vdJPXTHCvPLdu9Q954CkWU2tdsZ6VicGmGAbo
```

### `TARGET_WORKSHEET_NAME`

Debe contener el nombre exacto de la pestana destino del consolidado.

Ejemplo:

```text
ventas_consolidado
```

## Variables operativas

El workflow permite usar estos parametros de corrida:

- `pipeline_lookback_days`
- `pipeline_run_date`
- `force_run`

## Comportamiento del workflow

### Corridas programadas

- Frecuencia: cada 30 minutos
- Ventana horaria: `10:00` a `22:30`
- Zona horaria operativa: `America/Lima`
- Modo de carga: `append`

### Corridas manuales

Una corrida manual:

- ejecuta pruebas antes del ETL;
- permite ajustar la ventana de lectura;
- puede forzarse fuera de horario con `force_run=true`.

## Compatibilidad con GitHub Actions

Desde `2026-05-06`, el workflow usa versiones compatibles con Node 24:

- `actions/checkout@v6`
- `actions/setup-python@v6`

Esto evita la advertencia de deprecacion asociada a Node 20 en runners de
GitHub Actions.

## Como lanzar la primera corrida manual

1. Ve a la pestaña `Actions` del repositorio.
2. Selecciona el workflow `Sync sales data`.
3. Haz clic en `Run workflow`.
4. Opcionalmente completa:
   - `pipeline_lookback_days`
   - `pipeline_run_date`
   - `force_run`
5. Ejecuta la corrida.

## Valores recomendados para la primera corrida

Para una validacion inicial controlada:

- `pipeline_lookback_days = 1`
- `pipeline_run_date =` vacio, o la fecha actual
- `force_run = true` solo si estas fuera del horario de negocio

## Verificaciones posteriores a la primera corrida

Despues de ejecutar el workflow, revisa:

- que el job `test` haya terminado en verde;
- que el job `sync` haya terminado en verde;
- que el log indique la ventana de procesamiento correcta;
- que no existan errores `429`, `500`, `502`, `503` o `504` repetidos;
- que la hoja destino reciba solo filas nuevas;
- que no se dupliquen registros al relanzar la corrida.

## Errores comunes

### Error de credenciales

Posibles causas:

- JSON incompleto o mal copiado;
- secret con nombre incorrecto;
- cuenta de servicio revocada o invalida.

### Error de permisos en Google Sheets

Posibles causas:

- la cuenta de servicio no tiene acceso a una fuente;
- la cuenta de servicio no tiene permiso de edicion en el consolidado.

### El workflow no corre fuera de horario

Esto es esperado.

La automatizacion valida la ventana de negocio `10:00` a `22:30` hora de Lima.

Si necesitas correr fuera de esa ventana, usa una corrida manual con:

```text
force_run = true
```

### El ETL corre pero no inserta filas

Posibles causas:

- no hubo registros nuevos dentro de la ventana;
- todos los registros fueron detectados como duplicados;
- las hojas revisadas no pertenecen al rango de fechas procesado.

## Recomendacion de operacion

Para marcha blanca:

- usar `append` como modo regular;
- mantener `PIPELINE_LOOKBACK_DAYS=3`;
- revisar logs durante los primeros dias;
- usar `replace` solo para reprocesos controlados.

## Checklist final

- Workflow presente en el repositorio
- Secrets creados
- Permisos de Google compartidos
- Primera corrida manual exitosa
- Validacion de deduplicacion correcta
- Validacion de horario correcta
- Corridas programadas activas
