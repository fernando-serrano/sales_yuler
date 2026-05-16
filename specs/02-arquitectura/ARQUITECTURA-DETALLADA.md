# Arquitectura del Sistema sales_yuler

**Versión**: 2.0  
**Fecha de actualización**: 2026-05-15  
**Estado**: Producción

---

## 📋 Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Arquitectura de Capas](#arquitectura-de-capas)
3. [Componentes y Módulos](#componentes-y-módulos)
4. [Flujos de Datos](#flujos-de-datos)
5. [Patrones Arquitectónicos](#patrones-arquitectónicos)
6. [Decisiones Clave](#decisiones-clave)
7. [Evolución y Escalabilidad](#evolución-y-escalabilidad)

---

## 🎯 Visión General

`sales_yuler` es un **pipeline ETL (Extract-Transform-Load)** que:
- **Extrae** datos de ventas desde Google Sheets
- **Transforma** y normaliza los datos según reglas de negocio
- **Deduplica** registros para garantizar unicidad
- **Carga** datos limpios en un almacén centralizado

### Principios de Diseño

```
┌─────────────────────────────────────────────────────────┐
│                                                           │
│  SEPARACIÓN DE RESPONSABILIDADES (Clean Architecture)   │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐   │
│  │  Interfaces  │→ │ Aplicación   │→ │   Dominio   │   │
│  │   (CLI)      │  │   (Casos de  │  │  (Reglas de │   │
│  │              │  │    Uso)      │  │  Negocio)   │   │
│  └──────────────┘  └──────────────┘  └─────────────┘   │
│                          ↓                      ↑        │
│                  ┌──────────────────────────────────┐   │
│                  │   Infraestructura                │   │
│                  │  (Google Sheets API, Config)    │   │
│                  └──────────────────────────────────┘   │
│                                                           │
│  ✓ Independencia de proveedores externos                │
│  ✓ Testabilidad sin dependencias                        │
│  ✓ Fácil mantenimiento y evolución                      │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## 🏗️ Arquitectura de Capas

### 1. **INTERFACES (Capa de Entrada)**

**Ubicación**: `sales_yuler/interfaces/`  
**Responsabilidad**: Recibir comandos externos y coordinar con capas inferiores

#### Módulo: `cli.py`
- Parsea argumentos de línea de comandos
- Carga configuración desde variables de entorno
- Delega ejecución a la capa de aplicación
- Reporta estado y errores al usuario

**Interacciones**:
```
CLI Arguments / Env Vars
    ↓
cli.py (parse_args, load_config)
    ↓
Application.execute()
    ↓
Result / Error
```

**Contrato de Entrada**:
```python
--sources config/sources.yml      # Archivo de configuración de fuentes
--month 2026-05                   # Período a procesar
--mode [sync|append]              # Modo de operación
--window-days 7                   # Ventana deslizante de lectura
```

---

### 2. **APPLICATION (Capa de Orquestación)**

**Ubicación**: `sales_yuler/application/`  
**Responsabilidad**: Orquestar el flujo ETL y construir dependencias

#### Módulo: `pipeline.py`
- Construye la cadena de procesamiento
- Instancia componentes de infraestructura
- Coordina extracción → transformación → deduplicación → carga
- Asigna identificadores únicos globales (UUIDs)
- Maneja reintentos y recuperación ante fallos

**Responsabilidades Clave**:

```
Pipeline Execution Flow
├─ 1. Load Configuration
│  └─ Parse sources.yml, environment variables
│
├─ 2. Build Window
│  ├─ Calculate processing period
│  └─ Apply rolling window strategy
│
├─ 3. Instantiate Infrastructure
│  ├─ Google Sheets Client
│  ├─ Rate Limiter
│  └─ Database Connection (future)
│
├─ 4. Execute ETL Pipeline
│  ├─ Extract
│  ├─ Transform
│  ├─ Deduplicate
│  └─ Load
│
└─ 5. Report Results
   ├─ Records processed
   ├─ Duplicates removed
   ├─ Errors encountered
   └─ Timestamp and duration
```

**Interfaces de la Capa**:
```python
pipeline = Pipeline(
    config=SourcesConfig,
    start_date=date,
    end_date=date,
    window_days=7
)
result = pipeline.execute()  # → PipelineResult
```

---

### 3. **DOMAIN (Capa de Lógica de Negocio)**

**Ubicación**: `sales_yuler/domain/`  
**Responsabilidad**: Encapsular toda la lógica de negocio independiente de proveedores

#### 3.1 Modelos y Esquema

**`schema.py`**: Define la estructura canónica de datos
```python
# Esquema universal de ventas
{
    "id": UUID,              # Identificador único global
    "source_id": str,        # Origen de datos
    "document_id": str,      # ID del documento (Google Sheet)
    "sheet_name": str,       # Hoja específica
    "row_number": int,       # Fila en la fuente original
    "sale_date": date,       # Fecha de venta normalizada
    "product": str,          # Producto normalizado
    "quantity": int,         # Cantidad
    "unit_price": float,     # Precio unitario
    "total_amount": float,   # Monto total
    "customer_name": str,    # Cliente normalizado
    "observations": str,     # Notas
    "processed_at": datetime,# Timestamp de procesamiento
    "source_hash": str       # Hash para deduplicación
}
```

**`dates.py`**: Lógica especializada en fechas
```python
# Interpretación de fechas en múltiples formatos
parse_sale_date(value, format_hints)  # Maneja DD/MM/YYYY, YYYY-MM-DD, etc.
validate_date_range(date, min_date, max_date)  # Validación de rango
normalize_date(date) → ISO 8601  # Normalización a formato estándar
```

#### 3.2 Normalizaciones

**`field_normalizers.py`**: Transformaciones de campos individuales
```python
normalize_product(name: str) → str
normalize_customer(name: str) → str
normalize_phone(phone: str) → str
normalize_currency(amount: str|float) → float
```

**Reglas de Normalización**:
- Trim whitespace
- Lowercase (cuando aplica)
- Estandarizar separadores
- Validar rangos y tipos

#### 3.3 Transformaciones

**`transformations.py`**: Lógica de transformación de filas
```python
class SalesTransformer:
    def transform_row(raw_row: dict) → Sale:
        """Convierte fila cruda a Sale normalizado"""
        # Valida campos obligatorios
        # Normaliza cada campo
        # Calcula campos derivados
        # Retorna Sale o falla con ValidationError
```

#### 3.4 Deduplicación

**`deduplication.py`**: Estrategia de eliminación de duplicados
```python
class DeduplicationStrategy:
    def build_dedup_key(sale: Sale) → str:
        """Clave única por fuente"""
        # Hash(source_id + document_id + sheet_name + row_number)
        
    def deduplicate(sales: List[Sale]) → List[Sale]:
        """Elimina duplicados en lote"""
```

**Criterios de Duplicación**:
```
Dos ventas son duplicadas si:
├─ Tienen el mismo source_id
├─ Tienen el mismo document_id (Google Sheet)
├─ Tienen el mismo sheet_name
└─ Tienen el mismo row_number
```

---

### 4. **INFRASTRUCTURE (Capa de Integración)**

**Ubicación**: `sales_yuler/infrastructure/`  
**Responsabilidad**: Acceso a sistemas externos, configuración, credenciales

#### 4.1 Configuración

**`settings.py`**: Gestión centralizada de configuración
```python
class AppSettings:
    - GOOGLE_CREDENTIALS_PATH
    - DATABASE_URL (future)
    - LOG_LEVEL
    - RATE_LIMIT_QPM (queries per minute)
    - MAX_RETRIES
    - TIMEOUT_SECONDS
```

**Precedencia de Configuración**:
1. Variables de entorno (máxima prioridad)
2. Archivo `.env`
3. Valores por defecto en código
4. Archivo de configuración YAML (sources.yml)

#### 4.2 Integración con Google Sheets

**`google/client.py`**: Cliente base de Google
```python
class GoogleSheetsClient:
    def __init__(credentials: dict):
        self.service = build_sheets_service(credentials)
    
    def get_spreadsheet(spreadsheet_id: str) → Spreadsheet
    def get_sheet_data(spreadsheet_id, sheet_name, range) → List[List[str]]
    def write_data(spreadsheet_id, sheet_name, range, values) → WriteResult
```

**`google/rate_limit.py`**: Control de cuotas y reintentos
```python
class RateLimiter:
    def __init__(qpm: int = 100):  # Queries per minute
        self.delay = 60 / qpm
    
    async def acquire():
        # Espera según el rate limit
    
    def retry_with_backoff(func, max_retries=3):
        # Reintentos exponenciales: 1s, 2s, 4s, 8s...
```

**Estrategia de Reintentos**:
```
Intento 1: Fallo → espera 1 segundo
Intento 2: Fallo → espera 2 segundos
Intento 3: Fallo → espera 4 segundos
Intento 4: Fallo → error definitivo
```

**`google/sheets_extractor.py`**: Lectura de Google Sheets
```python
class SheetsExtractor:
    def extract_sales(
        spreadsheet_id: str,
        sheet_name: str,
        date_range: DateRange
    ) → Iterator[dict]:
        """Extrae filas de una hoja de cálculo"""
        # Lee rango especificado
        # Filtra por fecha
        # Valida formato de encabezado
        # Retorna iterador de filas
```

**`google/sheets_loader.py`**: Escritura en Google Sheets (future)
```python
class SheetsLoader:
    def load_processed_sales(
        results: List[Sale]
    ) → LoadResult:
        """Escribe ventas procesadas en hoja de destino"""
```

#### 4.3 Modelos de Configuración

**`sources.yml`**: Especificación de fuentes
```yaml
sources:
  - name: "tienda-principal"
    spreadsheet_id: "abc123..."
    sheets:
      - name: "Ventas Mayo 2026"
        date_column: A
        header_row: 1
        data_start_row: 2
    
  - name: "tienda-secundaria"
    spreadsheet_id: "def456..."
    sheets:
      - name: "Registros"
        date_column: C
```

---

## 🔄 Flujos de Datos

### Flujo ETL Completo

```
┌─────────────────┐
│  Google Sheets  │  ← Fuente de datos
└────────┬────────┘
         │ raw_rows
         ↓
┌──────────────────────┐
│  SheetsExtractor     │  ← Lectura con rate limiting
│  (Infrastructure)    │
└────────┬─────────────┘
         │ raw_row[]
         ↓
┌──────────────────────┐
│  SalesTransformer    │  ← Normalización y validación
│  (Domain)            │
└────────┬─────────────┘
         │ Sale[]
         ↓
┌──────────────────────┐
│  Deduplicator        │  ← Eliminación de duplicados
│  (Domain)            │
└────────┬─────────────┘
         │ Sale[] (deduped)
         ↓
┌──────────────────────┐
│  SheetsLoader        │  ← Persistencia
│  (Infrastructure)    │
└────────┬─────────────┘
         │ LoadResult
         ↓
┌─────────────────────┐
│ Resultado Final     │  → Reporte
└─────────────────────┘
```

### Flujo de Datos en Detalles

#### Fase 1: Configuración
```
CLI → parse arguments
  ↓
Load sources.yml
  ↓
Build date window [start_date, end_date]
  ↓
Create extractor per source
```

#### Fase 2: Extracción
```
For each source:
  For each sheet:
    Acquire rate limit token
    Read sheet metadata
    Get data range [header_row, last_row]
    Filter by date_range
    Yield raw rows
```

#### Fase 3: Transformación
```
For each raw_row:
  Parse fields according to schema
  Normalize values (trim, lowercase, etc.)
  Validate constraints (type, range, format)
  Calculate derived fields
  Create Sale object
  → ValidationError if any rule fails
```

#### Fase 4: Deduplicación
```
Collect all Sales from phase 3
Build dedup_key = hash(source + document + sheet + row)
Group by dedup_key
Keep only first occurrence per key
Return deduplicated list
```

#### Fase 5: Carga
```
For each Sale:
  Check if already exists in target
  If new → insert
  If duplicate → skip
  Record result (inserted/skipped)
Report summary
```

---

## 🎨 Patrones Arquitectónicos

### 1. **Clean Architecture / Hexagonal**

```
┌─────────────────────────────────┐
│        Interfaces               │  ← Puertos externos (CLI)
│    (HTTP, CLI, Files, etc)      │
└──────────────┬──────────────────┘
               │
        ┌──────↓──────┐
        │ Application │  ← Casos de uso, orquestación
        └──────┬──────┘
               │
       ┌───────↓────────┐
       │     Domain     │  ← Lógica de negocio pura
       └───────┬────────┘
               │
    ┌──────────↓──────────┐
    │  Infrastructure     │  ← Adaptadores (Google, DB, etc)
    └─────────────────────┘
```

**Ventajas**:
- Dominio aislado y testeable
- Fácil cambiar de proveedor (Google → otro)
- Independencia de frameworks

### 2. **Repository Pattern** (Future)

```python
# Abstracción para acceso a datos
interface SalesRepository:
    find_by_id(id) → Sale
    find_duplicates(key) → List[Sale]
    save(sale) → SaveResult
    delete(id) → DeleteResult
```

### 3. **Strategy Pattern**

Utilizado para deduplicación y transformaciones:
```python
# Diferentes estrategias de deduplicación
class DuplicateStrategy:
    def check(sale1, sale2) → bool

# Diferentes estrategias de rate limiting
class RateLimitStrategy:
    def acquire() → bool
```

### 4. **Iterator Pattern**

Lectura en streaming para economizar memoria:
```python
# En lugar de cargar todos en memoria
extracted_sales = extractor.extract()  # Iterator[Sale]

for sale in extracted_sales:  # Procesa de a uno
    transformed = transformer.transform(sale)
    deduplicated.add(transformed)
```

---

## 🔐 Decisiones Clave

| Decisión | Opción Elegida | Razón |
|----------|---|---|
| Deduplicación | Pre-insert en memoria | Garantiza no duplicar sin locks en BD |
| Rate Limiting | Token bucket | Predecible y eficiente |
| Formato de config | YAML | Legible, flexible, estándar |
| Identificadores | UUID v4 | Globalmente único, distribuido |
| Logging | Structured JSON | Parseables, consultables |
| Reintentos | Exponential backoff | Evita sobrecargar Google |
| Validación | Strict schemas | Fail-fast, datos limpios |

---

## 📈 Evolución y Escalabilidad

### Evolución del Diseño

```
Versión 1.0 (Actual)
├─ Single threaded
├─ In-memory deduplication
├─ Google Sheets only
└─ Manual scheduling

Versión 2.0 (Planeado)
├─ Async/await pipeline
├─ Distributed deduplication (Redis)
├─ Multiple sources (Sheets, CSV, API)
└─ Scheduled jobs (Celery/APScheduler)

Versión 3.0 (Futuro)
├─ Streaming (Kafka/Pub-Sub)
├─ Real-time transformations
├─ Data quality SLAs
└─ Multi-tenant support
```

### Escalabilidad

**Dimensión 1: Número de Fuentes**
- Actual: 1-5 sources
- Limitación: Tiempo total de ejecución
- Solución: Procesar en paralelo por source

**Dimensión 2: Volumen de Datos**
- Actual: <10k registros por ejecución
- Limitación: Google Sheets API quotas (10k QPD)
- Solución: Batch processing, streaming

**Dimensión 3: Frecuencia de Ejecución**
- Actual: Manual (1-2x diarias)
- Limitación: Costos, idempotencia
- Solución: Scheduler + checkpoints

### Puntos de Extensión

```
1. Nuevas Fuentes de Datos
   └─ Implementar SalesExtractor interface
   
2. Nuevas Reglas de Validación
   └─ Agregar validadores a SalesTransformer
   
3. Nuevos Destinos
   └─ Implementar SalesLoader interface
   
4. Nuevas Transformaciones
   └─ Extender domain/sales/transformations.py
```

---

## 📊 Métricas Clave

| Métrica | Objetivo | Estrategia |
|---------|----------|-----------|
| Latencia E2E | < 5 min | Async processing |
| Accuracy | 99.9% | Strict validation |
| Deduplication Ratio | 5-15% | Hash-based strategy |
| API Success Rate | 99%+ | Retry logic + monitoring |
| Data Completeness | 100% | Schema validation |

---

## 🔗 Referencias

- [Reglas de Negocio](../03-dominio/README.md)
- [Módulos Detallados](../04-modulos/README.md)
- [Infraestructura](../05-infraestructura/README.md)
- [Operación](../06-operacion/README.md)

