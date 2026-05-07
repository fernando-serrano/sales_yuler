from sales_yuler.domain.dates import (
    date_from_worksheet_title,
    format_date_ddmmyyyy,
    worksheet_title_belongs_to_month,
)


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
