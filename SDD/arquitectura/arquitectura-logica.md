# Arquitectura Logica

## Vista General

```text
interfaces -> application -> domain <- infrastructure
```

## Capas

### `interfaces`

Responsabilidad:

- recibir comandos externos;
- resolver parametros de ejecucion;
- invocar casos de uso.

Modulos actuales:

- `sales_yuler/interfaces/cli.py`

### `application`

Responsabilidad:

- coordinar el flujo end-to-end;
- construir dependencias de infraestructura;
- secuenciar extraccion, transformacion y carga;
- asignar identificadores globales.

Modulos actuales:

- `sales_yuler/application/pipeline.py`

### `domain`

Responsabilidad:

- definir el esquema canonico;
- encapsular reglas de fechas;
- limpiar encabezados y campos;
- validar ventas;
- normalizar filas de salida;
- construir claves de deduplicacion.

Modulos actuales:

- `sales_yuler/domain/schema.py`
- `sales_yuler/domain/dates.py`
- `sales_yuler/domain/sales/models.py`
- `sales_yuler/domain/sales/field_normalizers.py`
- `sales_yuler/domain/sales/transformations.py`
- `sales_yuler/domain/sales/deduplication.py`

### `infrastructure`

Responsabilidad:

- acceder a Google Sheets;
- resolver credenciales;
- leer configuracion externa;
- aplicar control de cuota y reintentos;
- adaptarse a APIs concretas.

Modulos actuales:

- `sales_yuler/infrastructure/settings.py`
- `sales_yuler/infrastructure/google/client.py`
- `sales_yuler/infrastructure/google/rate_limit.py`
- `sales_yuler/infrastructure/google/sheets_extractor.py`
- `sales_yuler/infrastructure/google/sheets_loader.py`

## Flujo de Ejecucion

1. CLI carga variables de entorno y argumentos.
2. Application construye la ventana de procesamiento.
3. Application filtra fuentes elegibles por mes.
4. Infrastructure crea cliente de Google.
5. Extractor lee spreadsheets y filtra hojas validas por fecha.
6. Domain normaliza y valida filas.
7. Domain construye claves de deduplicacion.
8. Loader compara contra destino e inserta solo filas nuevas.

## Fortalezas

- La logica de negocio no depende del CLI.
- El dominio es testeable sin acceso a Google.
- La infraestructura esta encapsulada.
- La estructura soporta evolucion hacia varios pipelines.

## Deuda Tecnica Vigente

- El pipeline aun agrega todas las filas del rango en memoria antes de cargar.
- No hay estado de checkpoints ni watermark por fuente.
- No existe contrato formal de calidad de datos por dataset.
