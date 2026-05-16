# Especificación de Módulos

Este directorio describe los módulos que componen el sistema,
sus responsabilidades, interfaces y cómo se comunican entre sí.

## Estructura de Módulos

### Extractores
- **Google Sheets Extractor**
  - Responsabilidad: Lectura de datos de Google Sheets
  - Ubicación: `sales_yuler/extractors/`
  - Interfaz: Conexión a Google API, manejo de cuotas
  - Salida: Datos en crudo (raw data)

### Transformadores
- **Sales Transformer**
  - Responsabilidad: Normalización y transformación de ventas
  - Ubicación: `sales_yuler/transformers/`
  - Entrada: Datos crudos de extractores
  - Salida: Datos normalizados según esquema del dominio

### Deduplicadores
- **Sales Deduplication**
  - Responsabilidad: Eliminación de registros duplicados
  - Ubicación: `sales_yuler/domain/sales/deduplication.py`
  - Criterios: Combinación de campos únicos por fuente
  - Política: Pre-insert para marcha blanca append

### Loaders
- **Database Loader** (Futuro)
  - Responsabilidad: Persistencia de datos procesados
  - Ubicación: `sales_yuler/loaders/`
  - Modo: Append con idempotencia

## Flujo de Datos Entre Módulos

```
Extractor (Google Sheets)
    ↓ (datos crudos)
Transformer (normalizar)
    ↓ (datos válidos)
Deduplicator (eliminar duplicados)
    ↓ (datos limpios)
Loader (persistencia)
    ↓
Base de datos
```

## Puntos de Integración

- **Rates Limiting**: Entre extractor e infraestructura de Google
- **Error Handling**: En cada límite de módulo
- **Logging**: Trazabilidad completa por registro
