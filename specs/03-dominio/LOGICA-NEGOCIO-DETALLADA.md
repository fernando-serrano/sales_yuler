# Lógica de Negocio y Dominio

**Versión**: 2.0  
**Fecha de actualización**: 2026-05-15  
**Área**: Domain-Driven Design

---

## 📋 Tabla de Contenidos

1. [Conceptos de Negocio](#conceptos-de-negocio)
2. [Entidades del Dominio](#entidades-del-dominio)
3. [Reglas de Negocio](#reglas-de-negocio)
4. [Flujos de Decisión](#flujos-de-decisión)
5. [Invariantes del Sistema](#invariantes-del-sistema)
6. [Casos Especiales](#casos-especiales)

---

## 💼 Conceptos de Negocio

### ¿Qué es una Venta?

Una **venta** es el registro de una transacción de productos de joyería:

```
Venta = {
  Qué se vendió:
    ├─ Producto (ej: "Anillo de oro 18K")
    ├─ Cantidad (ej: 2 unidades)
    └─ Precio unitario (ej: $450,000)
    
  Cuándo se vendió:
    └─ Fecha y hora
    
  Quién vendió / Quién compró:
    ├─ Vendedor (implícito en la fuente)
    └─ Cliente (ej: "María García")
    
  Dónde está registrado:
    ├─ Google Sheet específico
    ├─ Número de fila en la hoja
    └─ Tienda/sucursal origen
    
  Metadatos de trazabilidad:
    ├─ ID único global
    ├─ Hash de deduplicación
    ├─ Timestamp de procesamiento
    └─ Observaciones/notas
}
```

### Fuentes de Datos

Las ventas provienen de **múltiples fuentes**:

```
┌─────────────────────────────┐
│   Google Sheets             │
│  (Principal)                │
│                             │
│ ├─ Tienda Principal         │
│ ├─ Tienda Secundaria        │
│ └─ Pop-up Ventas Mayo       │
│                             │
└─────────────────────────────┘
```

Cada fuente tiene:
- **ID único**: identificador en Google Drive
- **Hojas múltiples**: cada sheet es un registro de ventas
- **Formato variable**: columnas pueden cambiar por fuente
- **Fechas de validez**: rango de datas confiables

---

## 🏛️ Entidades del Dominio

### 1. **Sale (Venta Normalizada)**

Es la representación canónica de una venta después de procesamiento:

```python
@dataclass
class Sale:
    # Identificación
    id: UUID                    # Único global, asignado por el sistema
    source_id: str              # Origen (ej: "tienda-principal")
    
    # Ubicación en la fuente
    document_id: str            # ID de Google Sheet
    sheet_name: str             # Nombre de la hoja
    row_number: int             # Fila en la fuente
    
    # Datos de la transacción
    sale_date: date             # Fecha de venta normalizada (ISO 8601)
    product: str                # Producto normalizado
    quantity: int               # Cantidad (validado: >= 1)
    unit_price: Decimal         # Precio unitario (validado: > 0)
    total_amount: Decimal       # Monto total = quantity × unit_price
    customer_name: str          # Cliente normalizado
    
    # Metadatos
    observations: str | None    # Notas adicionales
    source_hash: str            # Hash para deduplicación
    processed_at: datetime      # Timestamp de procesamiento
    
    @property
    def revenue_stream(self) -> str:
        """Clasifica por tipo de producto"""
        if "oro" in self.product.lower():
            return "oro"
        elif "plata" in self.product.lower():
            return "plata"
        else:
            return "otros"
```

### 2. **RawRow (Fila Cruda)**

Representación de una fila antes de procesar:

```python
@dataclass
class RawRow:
    sheet_name: str
    row_number: int
    values: dict[str, str]      # Campo → valor como string
    extracted_at: datetime
```

### 3. **DeduplicationKey (Clave de Deduplicación)**

Identifica unívocamente un registro dentro de una fuente:

```python
@dataclass
class DeduplicationKey:
    source_id: str
    document_id: str
    sheet_name: str
    row_number: int
    
    def to_hash(self) -> str:
        """Genera hash SHA256 de la clave"""
        key_str = f"{self.source_id}:{self.document_id}:{self.sheet_name}:{self.row_number}"
        return hashlib.sha256(key_str.encode()).hexdigest()
```

**Por qué esta clave:**
- Es **estable**: una fila siempre tendrá las mismas coordenadas
- Es **única**: no hay dos filas con el mismo (sheet, row_number)
- Es **rastreable**: permite auditar contra la fuente original

### 4. **ProcessingWindow (Ventana de Procesamiento)**

Define qué datos procesar en cada ejecución:

```python
@dataclass
class ProcessingWindow:
    start_date: date            # Inicio (inclusivo)
    end_date: date              # Fin (inclusivo)
    sources: list[str]          # Fuentes a incluir
    mode: str                   # "sync" o "append"
    
    @property
    def duration_days(self) -> int:
        return (self.end_date - self.start_date).days
```

---

## 📋 Reglas de Negocio

### R1: Validación de Campos Obligatorios

```
Campos obligatorios para cualquier venta:
├─ Fecha: REQUERIDA (no nula, válida)
├─ Producto: REQUERIDO (mínimo 3 caracteres)
├─ Cantidad: REQUERIDA (entero > 0)
├─ Precio: REQUERIDO (número > 0)
└─ Cliente: REQUERIDO (mínimo 2 caracteres)

Acción si falla:
  → RECHAZAR la fila con ValidationError
  → REGISTRAR el error en logs con detalles
  → NO procesar esta fila en adelante
```

### R2: Normalización de Fechas

```
Entrada de fecha puede ser:
├─ DD/MM/YYYY (ej: "15/05/2026")
├─ YYYY-MM-DD (ej: "2026-05-15")
├─ Texto de fecha (ej: "15 de mayo de 2026")
└─ Timestamp

Proceso de normalización:
  1. Trim whitespace
  2. Detectar formato
  3. Parsear a date object
  4. Validar en rango [1990, 2100]
  5. Convertir a ISO 8601

Salida:
  → date(2026, 5, 15)
  → Almacenado como "2026-05-15"

Acción si falla:
  → Registrar error
  → Rechazar fila
```

### R3: Normalización de Productos

```
Transformaciones aplicadas:
├─ Trim whitespace
├─ Lowercase (para comparación)
├─ Estandarizar separadores:
│  ├─ " / " → " - "
│  ├─ "  " (múltiples espacios) → " "
│  └─ Remover caracteres especiales innecesarios
├─ Expandir abreviaturas:
│  ├─ "K" → "quilates"
│  ├─ "gr" → "gramos"
│  └─ "pz" → "piezas"
└─ Validar contra diccionario de productos (futuro)

Ejemplos:
  "ANILLO ORO  18K"  → "anillo oro 18 quilates"
  "collar/plata"     → "collar plata"
  "pulsera-diamante" → "pulsera diamante"
```

### R4: Validación de Cantidades

```
Regla:
  quantity ∈ ℤ+ (enteros positivos)
  
Restricciones:
  ├─ Mínimo: 1 unidad
  ├─ Máximo: 1000 unidades (validación de sanidad)
  └─ Tipo: debe ser número entero

Conversión:
  "5"     → 5 ✓
  "5.0"   → 5 ✓
  "5.5"   → RECHAZAR (no es entero)
  "0"     → RECHAZAR (no puede ser 0)
  "-5"    → RECHAZAR (no puede ser negativo)
```

### R5: Validación de Precios

```
Regla:
  unit_price, total_amount ∈ ℝ+ (números reales positivos)
  
Restricciones:
  ├─ Mínimo: $1 (validación de sanidad)
  ├─ Máximo: $10,000,000
  ├─ Precisión: máximo 2 decimales
  └─ Separador: aceptar "." o ","

Conversión:
  "$1.500,00" (Colombia)    → 1500.00 ✓
  "1500.00" (USA)           → 1500.00 ✓
  "1500"                    → 1500.00 ✓
  "1500.555"                → RECHAZAR (3 decimales)
  "-1500"                   → RECHAZAR (negativo)
```

### R6: Validación de Clientes

```
Regla:
  customer_name ∈ [string | null]
  
Restricciones si presente:
  ├─ Mínimo 2 caracteres
  ├─ Máximo 100 caracteres
  ├─ No puede ser solo números
  └─ Remover títulos (Dr., Ing., etc.)

Normalización:
  ├─ Trim whitespace
  ├─ Title case si es apropriado
  ├─ Expandir abreviaturas de nombre
  └─ Remover caracteres especiales peligrosos

Ejemplos:
  "  JUAN GARCIA  "  → "Juan García"
  "DR. LUIS LOPEZ"   → "Luis López"
  "123456"           → RECHAZAR (solo números)
```

### R7: Integridad de Transacción

```
Invariante:
  total_amount = quantity × unit_price
  
Validación:
  abs(total_amount - (quantity × unit_price)) < 0.01
  
Acción si falla:
  → ADVERTENCIA: registrar discrepancia
  → USAR el valor calculado
  → NO rechazar (podría ser redondeo)
```

### R8: Deduplicación Pre-Insert

```
Política: NO PERMITIR duplicados en BD
  
Estrategia:
  1. Construir clave de dedup = hash(source + sheet + row)
  2. Comparar contra clave de ultimo procesamiento
  3. Si ya existe:
     → SKIP (contar como "ignored")
     → NO insertar
  4. Si es nuevo:
     → INSERTAR
     → CONTAR como "inserted"

Objetivo:
  ├─ Idempotencia: N ejecuciones = resultado idéntico
  ├─ Seguridad: no se duplican datos
  └─ Recuperación: puedo reprocesar sin riesgo
```

### R9: Rastrabilidad Completa

```
Para cada venta, registrar:
  ├─ Origen exacto: source_id, document_id, sheet_name, row_number
  ├─ Timestamp: exact cuando se procesó
  ├─ ID único: UUID v4 para trazabilidad global
  ├─ Hash: para auditar contra la fuente
  └─ Errores: si falló alguna validación

Uso:
  → Auditoría: ¿de dónde viene este registro?
  → Debugging: ¿por qué falló este?
  → Reprocessing: ¿qué filas debo reintentar?
```

### R10: Ventana de Procesamiento

```
Configuración por ejecución:
  
  ProcessingWindow {
    start_date: date,       # Primero que se procesa
    end_date: date,         # Último que se procesa
    sources: [str],         # Cuáles fuentes incluir
    mode: "sync" | "append" # Estrategia de carga
  }

Filtrado:
  └─ Procesar solo ventas: start_date ≤ sale_date ≤ end_date

Rolling Window Strategy:
  └─ Ventana deslizante: ej, últimos 7 días
  └─ Útil para: procesar incrementalmente sin perder nada
```

---

## 🔄 Flujos de Decisión

### Flujo de Validación de una Fila

```
RawRow recibido
    ↓
¿Tiene todos los campos obligatorios?
├─ NO → RECHAZAR (error: campos faltantes)
└─ SÍ ↓
    
¿Es la fecha válida?
├─ NO → RECHAZAR (error: fecha inválida)
└─ SÍ ↓
    
¿Está la fecha en rango de ventana?
├─ NO → SKIP (fuera de ventana, sin error)
└─ SÍ ↓
    
¿Son cantidad y precio válidos (tipos, rangos)?
├─ NO → RECHAZAR (error: validación numérica)
└─ SÍ ↓
    
¿Es el producto reconocible?
├─ NO → ADVERTENCIA (pero continuar con valor normalizado)
└─ SÍ ↓
    
Construir Sale normalizado
    ↓
¿Es NUEVO según dedup_key?
├─ NO → SKIP (duplicado, contar como deduped)
└─ SÍ → INSERT (registrar como nuevo)
```

### Flujo de Deduplicación

```
Tengo lista: [Sale1, Sale2, Sale3, ...]
    ↓
Para cada Sale:
  dedup_key = hash(source + sheet + row)
  ↓
  ¿dedup_key ya está en BD?
  ├─ SÍ → marcar como IGNORED (ya existe)
  └─ NO → marcar como NEW
    ↓
Retornar solo [NEW sales]
    ↓
Persistir en BD
```

---

## 🔒 Invariantes del Sistema

Condiciones que **SIEMPRE** deben ser verdaderas:

| Invariante | Descripción | Verificación |
|-----------|-------------|--------------|
| **I1: Unicidad de ID** | Cada Sale tiene un id único | `len(set(s.id for s in all_sales)) == len(all_sales)` |
| **I2: Integridad de Dedup** | No hay filas duplicadas | `no duplicates by dedup_key` |
| **I3: Validez de Fecha** | Todas las fechas son válidas | `1990 <= sale_date.year <= 2100` |
| **I4: Validez de Cantidades** | Cantidades > 0 | `all(s.quantity >= 1 for s in sales)` |
| **I5: Validez de Precios** | Precios > 0 y precisión 2 dec | `all(s.unit_price > 0 for s in sales)` |
| **I6: Cálculo de Total** | Total = Qty × Precio | `abs(s.total_amount - s.quantity × s.unit_price) < 0.01` |
| **I7: Rastrabilidad** | Todo sale tiene origen | `all(s.source_id and s.document_id and s.sheet_name for s in sales)` |
| **I8: Timestamps** | processed_at siempre llenado | `all(s.processed_at for s in sales)` |

---

## 🎯 Casos Especiales

### Caso 1: Fila con Precio Nulo
```
Entrada: cantidad=5, precio=NULL, total=NULL
Acción: RECHAZAR
Razón: El precio es obligatorio para calcular ingresos
```

### Caso 2: Total Calculado ≠ Total Ingresado
```
Entrada: qty=5, unitPrice=1000, total=6000 (debería ser 5000)
Acción: ADVERTENCIA + usar total calculado
Razón: Posible error en la fuente, pero podemos inferir correctamente
```

### Caso 3: Fila Duplicada en Diferentes Fechas
```
Entrada: misma fila pero en múltiples sheets (ej, backup)
Dedup Key: source + sheet + row → diferente por sheet
Acción: Procesar ambas (no son duplicados por nuestra clave)
Nota: La fuente es responsable de evitar duplicados entre sheets
```

### Caso 4: Ventana de Procesamiento Vacía
```
Entrada: start_date=2026-05-01, end_date=2026-05-01, sin datos
Acción: Completar ejecución normalmente
Resultado: 0 registros procesados, 0 errores
Logging: "Processing window empty but valid"
```

### Caso 5: Fila Fuera de Ventana pero Nueva
```
Entrada: sale_date=2026-04-01, ventana=[2026-05-01, 2026-05-15]
Acción: SKIP (no procesar)
Razón: Fuera de ventana, aunque sea nueva
Logging: "Row skipped: outside processing window"
```

### Caso 6: Producto Irreconocible
```
Entrada: producto="XYZABC" (no existe en catálogo)
Acción: Normalizar a lowercase "xyzabc" y procesar
Razón: No sabemos todos los productos, pero normalizamos lo que recibimos
Nota: Futuro: validar contra catálogo maestro
```

---

## 📊 Métricas Derivadas

Métricas que se pueden calcular sobre las Sales:

```python
# Ingresos por stream
revenue_by_stream = {
    "oro": sum(s.total_amount for s in sales if s.revenue_stream == "oro"),
    "plata": sum(...),
    "otros": sum(...)
}

# Cantidad de transacciones
transaction_count = len(sales)

# Ticket promedio
average_ticket = sum(s.total_amount for s in sales) / len(sales)

# Productos más vendidos
top_products = Counter(s.product for s in sales).most_common(10)

# Ratio de deduplicación
dedup_ratio = ignored_count / (inserted_count + ignored_count)
```

---

## 🔗 Referencias

- [Arquitectura Detallada](../02-arquitectura/ARQUITECTURA-DETALLADA.md)
- [Módulos](../04-modulos/README.md)
- [Infraestructura](../05-infraestructura/README.md)

