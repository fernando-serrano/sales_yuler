from sales_yuler.domain.sales.transformations import normalize_sales_rows
from sales_yuler.infrastructure.google.sheets_extractor import WorksheetRows
from sales_yuler.infrastructure.settings import SourceConfig


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
                "DescripciÃ³n": "Anillo",
                "Monto": "S/ 118.00",
                "MÃ©todo de Pago": "Yape",
                "Cliente": "Ana",
                "DNI": 12345678,
                "TelÃ©fono": 999888777,
            }
        ],
    )

    rows = normalize_sales_rows(batch)

    assert len(rows) == 1
    assert rows[0]["fecha"] == "05/12/2024"
    assert rows[0]["descripcion"] == "Anillo"
    assert rows[0]["monto"] == 118.0
    assert rows[0]["metodo de pago"] == "YAPE"
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
                "NÂ°": "1",
                "Cliente": "",
                "Cantidad de productos": "2",
                "DescripciÃ³n / Productos": "Pulsera",
                "Tipo de Joya": "Pulsera",
                "Tipo de Material": "Plata",
                "MONTO": "S/.120,00",
                "Monto (Sin I.G.V)": "S/.101,69",
                "MÃ©todo de Pago": "Tarjeta",
                "Hora": "10:30",
                "Cliente 2": "MarÃ­a",
                "DNI": "12345678",
                "TelÃ©fono": "999888777",
                "Encargado": "Fernando",
            },
            {
                "NÂ°": "",
                "Cliente": "Salidas de caja",
                "Cantidad de productos": "",
                "DescripciÃ³n / Productos": "",
                "MONTO": "",
                "Cliente 2": "",
            },
            {
                "NÂ°": "",
                "Cliente": "",
                "Cantidad de productos": "",
                "DescripciÃ³n / Productos": "",
                "MONTO": "",
                "Cliente 2": "",
            },
        ],
    )

    rows = normalize_sales_rows(batch)

    assert len(rows) == 1
    assert rows[0]["fecha"] == "03/05/2026"
    assert rows[0]["nro"] == 1
    assert rows[0]["cantidad"] == "2"
    assert rows[0]["descripcion"] == "Pulsera"
    assert rows[0]["tipo de joya"] == "Pulsera"
    assert rows[0]["tipo de material"] == "Plata"
    assert rows[0]["monto"] == 120.0
    assert rows[0]["monto sin igv"] == 101.69
    assert rows[0]["metodo de pago"] == "TARJETA"
    assert rows[0]["hora"] == "10:30:00"
    assert rows[0]["cliente"] == "MARÍA"
    assert rows[0]["dni"] == "12345678"
    assert rows[0]["telefono"] == "999888777"
    assert rows[0]["encargado"] == "FERNANDO"


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
                "NÃ‚Â°": "1",
                "Cantidad de productos": "1",
                "DescripciÃƒÂ³n / Productos": "Anillo",
                "MONTO": "S/.50,00",
                "Monto (Sin I.G.V)": "S/.42,37",
            },
            {
                "NÃ‚Â°": "2",
                "Cantidad de productos": "1",
                "DescripciÃƒÂ³n / Productos": "Cadena",
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


def test_normalize_sales_rows_requires_description_and_amount_for_valid_sales():
    source = SourceConfig(
        name="ventas_prueba",
        url="https://docs.google.com/spreadsheets/d/example/edit",
        year=2026,
        month=5,
    )
    batch = WorksheetRows(
        source=source,
        document_title="Ventas prueba",
        worksheet_title="01",
        rows=[
            {
                "nro": "77",
                "cliente": "0",
                "cantidad": "",
                "descripcion": "",
                "monto": "",
            },
            {
                "nro": "78",
                "cantidad": "",
                "descripcion": "Aretes",
                "monto": "S/.80,00",
            },
            {
                "nro": "79",
                "cantidad": "2",
                "descripcion": "Collar",
                "monto": "0",
            },
        ],
    )

    rows = normalize_sales_rows(batch)

    assert len(rows) == 1
    assert rows[0]["nro"] == 1
    assert rows[0]["cantidad"] == 1
    assert rows[0]["descripcion"] == "Aretes"
    assert rows[0]["monto"] == 80.0


def test_normalize_sales_rows_formats_full_date_worksheet_titles():
    source = SourceConfig(
        name="ventas_prueba",
        url="https://docs.google.com/spreadsheets/d/example/edit",
        year=2026,
        month=5,
    )
    batch = WorksheetRows(
        source=source,
        document_title="Ventas prueba",
        worksheet_title="1/5/26",
        rows=[
            {
                "cantidad": "1",
                "descripcion": "Anillo",
                "monto": "S/.50,00",
            },
        ],
    )

    rows = normalize_sales_rows(batch)

    assert rows[0]["fecha"] == "01/05/2026"


def test_normalize_sales_rows_formats_iso_worksheet_titles():
    source = SourceConfig(
        name="ventas_2026_02",
        url="https://docs.google.com/spreadsheets/d/example/edit",
        year=2026,
        month=2,
    )
    batch = WorksheetRows(
        source=source,
        document_title="Ventas febrero",
        worksheet_title="2026-02-01",
        rows=[
            {
                "cantidad": "1",
                "descripcion": "Anillo",
                "monto": "S/.50,00",
            },
        ],
    )

    rows = normalize_sales_rows(batch)

    assert rows[0]["fecha"] == "01/02/2026"


def test_normalize_sales_rows_renumbers_valid_sales_within_the_day():
    source = SourceConfig(
        name="ventas_prueba",
        url="https://docs.google.com/spreadsheets/d/example/edit",
        year=2026,
        month=5,
    )
    batch = WorksheetRows(
        source=source,
        document_title="Ventas prueba",
        worksheet_title="07",
        rows=[
            {"nro": "4", "descripcion": "Anillo", "monto": "S/.50,00"},
            {"nro": "", "descripcion": "", "monto": ""},
            {"nro": "10", "descripcion": "Cadena", "monto": "S/.120,00"},
            {"nro": "11", "descripcion": "Pulsera", "monto": "0"},
            {"nro": "", "descripcion": "Aretes", "monto": "S/.80,00"},
        ],
    )

    rows = normalize_sales_rows(batch)

    assert [row["nro"] for row in rows] == [1, 2, 3]
    assert [row["descripcion"] for row in rows] == ["Anillo", "Cadena", "Aretes"]


def test_normalize_sales_rows_cleans_placeholder_noise_and_normalizes_contact_fields():
    source = SourceConfig(
        name="ventas_prueba",
        url="https://docs.google.com/spreadsheets/d/example/edit",
        year=2026,
        month=5,
    )
    batch = WorksheetRows(
        source=source,
        document_title="Ventas prueba",
        worksheet_title="08",
        rows=[
            {
                "Nro": "1",
                "Descripcion / Productos": "Anillo",
                "MONTO": "S/.50,00",
                "Hora": "9:5 pm",
                "Cliente 2": " ### MarÃ­a **** ",
                "DNI": "12.345.678----",
                "Telefono": "999-888-777",
                "Encargado": "... Pedro ...",
            },
            {
                "Nro": "2",
                "Descripcion / Productos": "Pulsera",
                "MONTO": "S/.80,00",
                "Hora": "----",
                "Cliente 2": "###",
                "DNI": "****",
                "Telefono": "....",
                "Encargado": "----",
            },
        ],
    )

    rows = normalize_sales_rows(batch)

    assert rows[0]["fecha"] == "08/05/2026"
    assert rows[0]["hora"] == "21:05:00"
    assert rows[0]["cliente"] == "MARÍA"
    assert rows[0]["dni"] == "12345678"
    assert rows[0]["telefono"] == "999888777"
    assert rows[0]["encargado"] == "PEDRO"
    assert rows[1]["hora"] == ""
    assert rows[1]["cliente"] == ""
    assert rows[1]["dni"] == ""
    assert rows[1]["telefono"] == ""
    assert rows[1]["encargado"] == ""


def test_normalize_sales_rows_normalizes_payment_methods_to_uppercase_and_pos():
    source = SourceConfig(
        name="ventas_prueba",
        url="https://docs.google.com/spreadsheets/d/example/edit",
        year=2026,
        month=5,
    )
    batch = WorksheetRows(
        source=source,
        document_title="Ventas prueba",
        worksheet_title="09",
        rows=[
            {"Descripcion / Productos": "Anillo", "MONTO": "S/.50,00", "Metodo de Pago": "P.O.S"},
            {"Descripcion / Productos": "Pulsera", "MONTO": "S/.80,00", "Metodo de Pago": "pos"},
            {"Descripcion / Productos": "Cadena", "MONTO": "S/.90,00", "Metodo de Pago": "POSS"},
            {"Descripcion / Productos": "Aretes", "MONTO": "S/.30,00", "Metodo de Pago": "yape"},
        ],
    )

    rows = normalize_sales_rows(batch)

    assert [row["metodo de pago"] for row in rows] == ["POS", "POS", "POS", "YAPE"]
