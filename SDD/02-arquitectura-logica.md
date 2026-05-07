# Arquitectura Lógica

## Vista General

```text
interfaces -> application -> domain <- infrastructure
```

## Capas

### `interfaces`

Responsabilidad:

- recibir comandos externos;
- resolver parámetros de ejecución;
- invocar casos de uso.

Módulos actuales:

- `sales_yuler/interfaces/cli.py`

### `application`

Responsabilidad:

- coordinar el flujo end-to-end;
- construir dependencias de infraestructura;
- secuenciar extracción, transformación y carga;
- asignar identificadores globales.

Módulos actuales:

- `sales_yuler/application/pipeline.py`

### `domain`

Responsabilidad:

- definir el esquema canónico;
- encapsular reglas de fechas;
- limpiar encabezados y campos;
- validar ventas;
- normalizar filas de salida.

Módulos actuales:

- `sales_yuler/domain/schema.py`
- `sales_yuler/domain/dates.py`
- `sales_yuler/domain/sales/models.py`
- `sales_yuler/domain/sales/field_normalizers.py`
- `sales_yuler/domain/sales/transformations.py`

### `infrastructure`

Responsabilidad:

- acceder a Google Sheets;
- resolver credenciales;
- leer configuración externa;
- adaptarse a APIs concretas.

Módulos actuales:

- `sales_yuler/infrastructure/settings.py`
- `sales_yuler/infrastructure/google/client.py`
- `sales_yuler/infrastructure/google/sheets_extractor.py`
- `sales_yuler/infrastructure/google/sheets_loader.py`

## Flujo de Ejecución

1. CLI carga variables de entorno y argumentos.
2. Application lee settings y fuentes habilitadas.
3. Infrastructure crea cliente de Google.
4. Extractor lee cada spreadsheet y filtra hojas válidas.
5. Domain normaliza y valida filas.
6. Application agrega `id registro`.
7. Loader escribe el consolidado final.

## Fortalezas

- La lógica de negocio ya no depende del CLI.
- El dominio es testeable sin acceso a Google.
- La infraestructura quedó encapsulada.
- La estructura soporta evolución hacia varios pipelines.

## Deuda Técnica Vigente

- El pipeline aún agrega todas las filas en memoria antes de cargar.
- No hay estado de checkpoints ni watermark por fuente.
- No existe contrato formal de calidad de datos por dataset.
- La carga `append` no es idempotente.
