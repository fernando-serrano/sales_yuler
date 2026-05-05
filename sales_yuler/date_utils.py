import calendar
import re
from datetime import date
from typing import Any


def date_from_worksheet_title(year: int, month: int, worksheet_title: Any) -> date | None:
    worksheet_date = parse_full_date_text(worksheet_title)
    if worksheet_date:
        return worksheet_date

    day = parse_day_only_text(worksheet_title)
    if day is None:
        return None

    return _safe_date(year, month, day)


def format_date_ddmmyyyy(value: date | None) -> str:
    return value.strftime("%d/%m/%Y") if value else ""


def worksheet_title_belongs_to_month(year: int, month: int, worksheet_title: Any) -> bool:
    worksheet_date = parse_full_date_text(worksheet_title)
    if worksheet_date:
        return worksheet_date.year == year and worksheet_date.month == month

    day = parse_day_only_text(worksheet_title)
    if day is None:
        return False

    _, month_days = calendar.monthrange(year, month)
    return 1 <= day <= month_days


def parse_full_date_text(value: Any) -> date | None:
    text = str(value).strip()
    iso_match = re.search(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b", text)
    if iso_match:
        year = int(iso_match.group(1))
        month = int(iso_match.group(2))
        day = int(iso_match.group(3))
        return _safe_date(year, month, day)

    date_match = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2}|\d{4})\b", text)
    if not date_match:
        return None

    day = int(date_match.group(1))
    month = int(date_match.group(2))
    year = int(date_match.group(3))
    if year < 100:
        year += 2000

    return _safe_date(year, month, day)


def parse_day_only_text(value: Any) -> int | None:
    text = str(value).strip()
    match = re.fullmatch(r"\d{1,2}", text)
    return int(text) if match else None


def _safe_date(year: int, month: int, day: int) -> date | None:
    try:
        return date(year, month, day)
    except ValueError:
        return None
