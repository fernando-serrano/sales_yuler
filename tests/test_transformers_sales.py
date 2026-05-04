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
    assert rows[0]["monto"] == 118.0
    assert rows[0]["metodo de pago"] == "Yape"
    assert rows[0]["fuente"] == "ventas_2024_12"
    assert rows[0]["documento"] == "Ventas diciembre"
    assert rows[0]["hoja"] == "05"


def test_normalize_sales_rows_uses_second_client_and_skips_cash_out_rows():
    source = SourceConfig(
        name="ventas_prueba",
        url="https://docs.google.com/spreadsheets/d/example/edit",
        year=2026,
        month=5,
    )
    batch = WorksheetRows(
        source=source,
        document_title="Ventas prueba",
        worksheet_title="03",
        rows=[
            {
                "N°": "1",
                "Cliente": "",
                "Cantidad de productos": "2",
                "Descripción / Productos": "Pulsera",
                "Tipo de Joya": "Pulsera",
                "Tipo de Material": "Plata",
                "MONTO": "S/.120,00",
                "Monto (Sin I.G.V)": "S/.101,69",
                "Método de Pago": "Tarjeta",
                "Hora": "10:30",
                "Cliente 2": "María",
                "DNI": "12345678",
                "Teléfono": "999888777",
                "Encargado": "Fernando",
            },
            {
                "N°": "",
                "Cliente": "Salidas de caja",
                "Cantidad de productos": "",
                "Descripción / Productos": "",
                "MONTO": "",
                "Cliente 2": "",
            },
            {
                "N°": "",
                "Cliente": "",
                "Cantidad de productos": "",
                "Descripción / Productos": "",
                "MONTO": "",
                "Cliente 2": "",
            },
        ],
    )

    rows = normalize_sales_rows(batch)

    assert len(rows) == 1
    assert rows[0]["fecha"] == "2026-05-03"
    assert rows[0]["nro"] == "1"
    assert rows[0]["cantidad"] == "2"
    assert rows[0]["descripcion"] == "Pulsera"
    assert rows[0]["tipo de joya"] == "Pulsera"
    assert rows[0]["tipo de material"] == "Plata"
    assert rows[0]["monto"] == 120.0
    assert rows[0]["monto sin igv"] == 101.69
    assert rows[0]["metodo de pago"] == "Tarjeta"
    assert rows[0]["hora"] == "10:30"
    assert rows[0]["cliente"] == "María"
    assert rows[0]["dni"] == "12345678"
    assert rows[0]["telefono"] == "999888777"
    assert rows[0]["encargado"] == "Fernando"


def test_normalize_sales_rows_converts_peruvian_currency_to_numbers():
    source = SourceConfig(
        name="ventas_prueba",
        url="https://docs.google.com/spreadsheets/d/example/edit",
        year=2026,
        month=4,
    )
    batch = WorksheetRows(
        source=source,
        document_title="Ventas prueba",
        worksheet_title="01",
        rows=[
            {
                "NÂ°": "1",
                "Cantidad de productos": "1",
                "DescripciÃ³n / Productos": "Anillo",
                "MONTO": "S/.50,00",
                "Monto (Sin I.G.V)": "S/.42,37",
            },
            {
                "NÂ°": "2",
                "Cantidad de productos": "1",
                "DescripciÃ³n / Productos": "Cadena",
                "MONTO": "S/.175,00",
                "Monto (Sin I.G.V)": "S/.148,31",
            },
        ],
    )

    rows = normalize_sales_rows(batch)

    assert rows[0]["monto"] == 50.0
    assert rows[0]["monto sin igv"] == 42.37
    assert rows[1]["monto"] == 175.0
    assert rows[1]["monto sin igv"] == 148.31
