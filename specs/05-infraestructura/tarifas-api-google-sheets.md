# API Google Sheets

## Tarifas, cuotas y criterios de uso

## Proposito

Este documento resume el costo operativo y las restricciones mas relevantes de
la API de Google Sheets para el proyecto `sales_yuler`.

## Resumen ejecutivo

- La API de Google Sheets no tiene costo adicional por uso.
- El riesgo principal no es financiero, sino de cuotas y latencia.
- Para este pipeline, el diseno debe optimizar lecturas, reducir escrituras
  innecesarias y manejar correctamente errores `429`.

## Costo

Segun la documentacion oficial de Google, el uso de la API de Google Sheets no
tiene cargo adicional.

### Implicacion para `sales_yuler`

- No se requiere un modelo de costeo por llamada.
- Si se requiere controlar volumen y frecuencia por limites de cuota.
- El foco tecnico debe estar en eficiencia, retries y particionado logico.

## Cuotas relevantes

Google publica cuotas por minuto que se recargan cada minuto.

| Tipo | Limite por proyecto | Limite por usuario por proyecto |
| --- | ---: | ---: |
| Lecturas | 300 por minuto | 60 por minuto |
| Escrituras | 300 por minuto | 60 por minuto |

## Restricciones operativas importantes

| Restriccion | Implicacion |
| --- | --- |
| Payload recomendado de hasta 2 MB | Conviene agrupar bien las operaciones y evitar cargas demasiado grandes. |
| Solicitudes atomicas | Si una actualizacion falla, toda la solicitud falla. |
| Timeout alrededor de 180 segundos | Solicitudes demasiado grandes pueden agotarse. |
| Error `429 Too Many Requests` | Se requiere backoff exponencial truncado. |

## Implicaciones para la arquitectura

### Lectura

- Conviene procesar hojas validas y omitir hojas auxiliares lo antes posible.
- Debe mantenerse control de ritmo entre lecturas.
- Los reintentos deben usar backoff exponencial truncado.

### Escritura

- Conviene minimizar escrituras repetidas sobre la hoja consolidada.
- Si el volumen crece, sera mejor escribir por batch que por fila.
- En escenarios futuros, una zona intermedia puede reducir presion sobre
  Sheets.

### Paralelizacion

- Paralelizar sin control puede romper facilmente las cuotas.
- Antes de usar Celery o workers distribuidos, conviene medir cuantas lecturas
  y escrituras por minuto consume realmente el pipeline.

## Recomendaciones para `sales_yuler`

### Corto plazo

- Mantener retries con backoff ante `429`.
- Seguir filtrando hojas por mes antes de normalizar.
- Evitar escrituras innecesarias en modo `append`.

### Mediano plazo

- Medir numero de llamadas por fuente, hoja y corrida.
- Disenar carga incremental e idempotente.
- Evaluar persistencia intermedia si crece el numero de fuentes.

### Largo plazo

- Si la cantidad de documentos aumenta de forma importante, revisar una
  arquitectura con staging y orquestacion externa.
- Revaluar paralelizacion solo con metricas reales de cuota y volumen.

## Decision de diseno

Para el estado actual del sistema:

- Google Sheets sigue siendo un destino valido.
- La principal limitacion es la cuota, no la tarifa.
- La arquitectura debe priorizar eficiencia de llamadas y resiliencia frente a
  limites de uso.

## Fuentes oficiales

- [Google Sheets API usage limits](https://developers.google.com/workspace/sheets/api/limits)
- [Google Sheets API scopes](https://developers.google.com/workspace/sheets/api/scopes)
