from datetime import date

from sales_yuler.infrastructure.google.sheets_extractor import (
    _is_retryable_read_error,
    _records_from_values,
    _retry_wait_seconds,
    _worksheet_should_be_processed,
    _worksheet_belongs_to_source_month,
)
from sales_yuler.infrastructure.settings import SourceConfig


class _FakeResponse:
    def __init__(self, status_code: int, headers: dict[str, str] | None = None) -> None:
        self.status_code = status_code
        self.headers = headers or {}


class _FakeAPIError(Exception):
    def __init__(self, status_code: int, headers: dict[str, str] | None = None) -> None:
        self.response = _FakeResponse(status_code, headers=headers)

    def __str__(self) -> str:
        return f"APIError: [{self.response.status_code}]"


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


def test_retryable_read_error_accepts_transient_google_failures():
    assert _is_retryable_read_error(_FakeAPIError(429)) is True
    assert _is_retryable_read_error(_FakeAPIError(503)) is True
    assert _is_retryable_read_error(_FakeAPIError(500)) is True
    assert _is_retryable_read_error(_FakeAPIError(400)) is False


def test_retry_wait_seconds_uses_fixed_backoff_for_transient_errors():
    assert _retry_wait_seconds(_FakeAPIError(503)) == 10


def test_retry_wait_seconds_uses_retry_after_for_quota_errors():
    assert _retry_wait_seconds(_FakeAPIError(429, headers={"Retry-After": "70"})) == 70


def test_worksheet_should_be_processed_uses_window_when_present():
    source = SourceConfig(
        name="ventas_2026_05",
        url="https://docs.google.com/spreadsheets/d/example/edit",
        year=2026,
        month=5,
    )

    assert _worksheet_should_be_processed(source, "04", date(2026, 5, 3), date(2026, 5, 6))
    assert not _worksheet_should_be_processed(source, "02", date(2026, 5, 3), date(2026, 5, 6))
