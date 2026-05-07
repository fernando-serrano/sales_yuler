from sales_yuler.infrastructure.google.sheets_extractor import (
    _records_from_values,
    _worksheet_belongs_to_source_month,
)
from sales_yuler.infrastructure.settings import SourceConfig


def test_worksheet_belongs_to_source_month_accepts_only_matching_full_dates():
    source = SourceConfig(
        name="ventas_2026_01",
        url="https://docs.google.com/spreadsheets/d/example/edit",
        year=2026,
        month=1,
    )

    assert _worksheet_belongs_to_source_month(source, "1/01/2026")
    assert _worksheet_belongs_to_source_month(source, "2026-01-31")
    assert not _worksheet_belongs_to_source_month(source, "1/02/2026")
    assert not _worksheet_belongs_to_source_month(source, "2026-02-01")


def test_worksheet_belongs_to_source_month_accepts_padded_month_typo():
    source = SourceConfig(
        name="ventas_2025_10",
        url="https://docs.google.com/spreadsheets/d/example/edit",
        year=2025,
        month=10,
    )

    assert _worksheet_belongs_to_source_month(source, "03/010/25")


def test_worksheet_belongs_to_source_month_uses_days_in_configured_month():
    february = SourceConfig(
        name="ventas_2026_02",
        url="https://docs.google.com/spreadsheets/d/example/edit",
        year=2026,
        month=2,
    )
    january = SourceConfig(
        name="ventas_2026_01",
        url="https://docs.google.com/spreadsheets/d/example/edit",
        year=2026,
        month=1,
    )

    assert _worksheet_belongs_to_source_month(february, "28")
    assert not _worksheet_belongs_to_source_month(february, "29")
    assert _worksheet_belongs_to_source_month(january, "31")
    assert not _worksheet_belongs_to_source_month(january, "Resumen")


def test_records_from_values_detects_headers_after_title_row():
    records = _records_from_values(
        [
            ["", "", "Control de ventas JOYERIA YULER 01/08/2024"],
            [
                "N°",
                "Cantidad",
                "Descripción",
                "MONTO",
                "Monto (Sin I.G.V)",
                "Met. Pago",
                "Hora",
                "Cliente",
                "DNI",
                "TELEFONO",
                "Salidas de caja",
            ],
            ["1", "1", "Recojo de pedido", "S/.30,00", "S/.25,4237", "EFECTIVO", "1:56pm", "Ana", "-", "999", ""],
        ]
    )

    assert records == [
        {
            "N°": "1",
            "Cantidad": "1",
            "Descripción": "Recojo de pedido",
            "MONTO": "S/.30,00",
            "Monto (Sin I.G.V)": "S/.25,4237",
            "Met. Pago": "EFECTIVO",
            "Hora": "1:56pm",
            "Cliente": "Ana",
            "DNI": "-",
            "TELEFONO": "999",
            "Salidas de caja": "",
        }
    ]
