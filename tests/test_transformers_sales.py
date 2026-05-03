from sales_yuler.config import SourceConfig
from sales_yuler.extractors.google_sheets import WorksheetRows
from sales_yuler.transformers.sales import normalize_sales_rows


def test_normalize_sales_rows_maps_aliases_and_metadata():
    source = SourceConfig(
        name="ventas_2024_12",
        url="https://docs.google.com/spreadsheets/d/example/edit",
        year=2024,
        month=12,
    )
    batch = WorksheetRows(
        source=source,
        document_title="Ventas diciembre",
        worksheet_title="05",
        rows=[
            {
                "nro.": 1,
                "Cantidad de productos": 2,
                "Descripción": "Anillo",
                "Monto": "S/ 118.00",
                "Método de Pago": "Yape",
                "Cliente": "Ana",
                "DNI": 12345678,
                "Teléfono": 999888777,
            }
        ],
    )

    rows = normalize_sales_rows(batch)

    assert len(rows) == 1
    assert rows[0]["fecha"] == "2024-12-05"
    assert rows[0]["descripcion"] == "Anillo"
    assert rows[0]["monto"] == "118.00"
    assert rows[0]["metodo de pago"] == "Yape"
    assert rows[0]["fuente"] == "ventas_2024_12"
    assert rows[0]["documento"] == "Ventas diciembre"
    assert rows[0]["hoja"] == "05"
