from sales_yuler.config import SourceConfig
from sales_yuler.extractors.google_sheets import _worksheet_belongs_to_source_month


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
