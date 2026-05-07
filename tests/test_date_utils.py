from sales_yuler.domain.dates import (
    build_processing_window,
    date_from_worksheet_title,
    format_date_ddmmyyyy,
    source_month_intersects_window,
    worksheet_title_belongs_to_window,
    worksheet_title_belongs_to_month,
)
from datetime import date


def test_date_from_worksheet_title_formats_january_day_only_as_ddmmyyyy():
    sale_date = date_from_worksheet_title(2026, 1, "1")

    assert format_date_ddmmyyyy(sale_date) == "01/01/2026"


def test_date_from_worksheet_title_formats_full_dates_as_ddmmyyyy():
    assert format_date_ddmmyyyy(date_from_worksheet_title(2026, 1, "1/01/2026")) == "01/01/2026"
    assert format_date_ddmmyyyy(date_from_worksheet_title(2026, 2, "2026-02-20")) == "20/02/2026"
    assert format_date_ddmmyyyy(date_from_worksheet_title(2026, 5, "1/5/26")) == "01/05/2026"
    assert format_date_ddmmyyyy(date_from_worksheet_title(2025, 10, "03/010/25")) == "03/10/2025"
    assert format_date_ddmmyyyy(date_from_worksheet_title(2026, 3, "06/.3/2026")) == "06/03/2026"


def test_worksheet_title_belongs_to_month_applies_to_any_source_month():
    assert worksheet_title_belongs_to_month(2026, 1, "31")
    assert worksheet_title_belongs_to_month(2026, 1, "2026-01-31")
    assert worksheet_title_belongs_to_month(2025, 10, "03/010/25")
    assert worksheet_title_belongs_to_month(2026, 3, "06/.3/2026")
    assert not worksheet_title_belongs_to_month(2026, 1, "1/02/2026")
    assert not worksheet_title_belongs_to_month(2026, 2, "29")
    assert not worksheet_title_belongs_to_month(2026, 3, "Resumen")


def test_build_processing_window_uses_lookback_days_inclusive():
    start_date, end_date = build_processing_window(date(2026, 5, 6), 3)

    assert start_date == date(2026, 5, 3)
    assert end_date == date(2026, 5, 6)


def test_source_month_intersects_window_for_cross_month_ranges():
    start_date = date(2026, 4, 29)
    end_date = date(2026, 5, 2)

    assert source_month_intersects_window(2026, 4, start_date, end_date)
    assert source_month_intersects_window(2026, 5, start_date, end_date)
    assert not source_month_intersects_window(2026, 3, start_date, end_date)


def test_worksheet_title_belongs_to_window_filters_exact_days():
    start_date = date(2026, 5, 3)
    end_date = date(2026, 5, 6)

    assert worksheet_title_belongs_to_window(2026, 5, "03", start_date, end_date)
    assert worksheet_title_belongs_to_window(2026, 5, "2026-05-06", start_date, end_date)
    assert not worksheet_title_belongs_to_window(2026, 5, "02", start_date, end_date)
    assert not worksheet_title_belongs_to_window(2026, 5, "Resumen", start_date, end_date)
