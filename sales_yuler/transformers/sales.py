import re
import unicodedata
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from sales_yuler.extractors.google_sheets import WorksheetRows
from sales_yuler.schema import CANONICAL_COLUMNS, COLUMN_ALIASES, OUTPUT_COLUMNS


def normalize_sales_rows(batch: WorksheetRows) -> list[dict[str, Any]]:
    sale_date = _date_from_worksheet(batch.source.year, batch.source.month, batch.worksheet_title)
    loaded_at = datetime.now().isoformat(timespec="seconds")
    normalized_rows: list[dict[str, Any]] = []

    for raw_row in batch.rows:
        row = _normalize_row_keys(raw_row)
        if _is_empty_sale_row(row):
            continue

        normalized = {column: row.get(column, "") for column in CANONICAL_COLUMNS}
        normalized["fecha"] = sale_date.isoformat() if sale_date else ""
        normalized["monto"] = _normalize_money(normalized["monto"])
        normalized["monto sin igv"] = _normalize_money(normalized["monto sin igv"])
        normalized["dni"] = str(normalized["dni"]).strip()
        normalized["telefono"] = str(normalized["telefono"]).strip()
        normalized["fuente"] = batch.source.name
        normalized["documento"] = batch.document_title
        normalized["hoja"] = batch.worksheet_title
        normalized["fecha de carga"] = loaded_at

        normalized_rows.append({column: normalized.get(column, "") for column in OUTPUT_COLUMNS})

    return normalized_rows


def _normalize_row_keys(raw_row: dict[str, Any]) -> dict[str, Any]:
    row: dict[str, Any] = {}
    for key, value in raw_row.items():
        canonical_key = COLUMN_ALIASES.get(_normalize_key(str(key)))
        if canonical_key:
            row[canonical_key] = value
    return row


def _normalize_key(value: str) -> str:
    without_accents = "".join(
        char
        for char in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(char)
    )
    cleaned = re.sub(r"\s+", " ", without_accents.replace(".", " ").strip().lower())
    return cleaned


def _is_empty_sale_row(row: dict[str, Any]) -> bool:
    meaningful_fields = ["descripcion", "cliente", "monto", "cantidad"]
    return all(str(row.get(field, "")).strip() == "" for field in meaningful_fields)


def _date_from_worksheet(year: int, month: int, worksheet_title: str) -> date | None:
    match = re.search(r"\d{1,2}", worksheet_title)
    if not match:
        return None

    day = int(match.group())
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _normalize_money(value: Any) -> str:
    text = str(value).strip()
    if not text:
        return ""

    cleaned = text.replace("S/", "").replace("s/", "").replace(",", "").strip()
    try:
        return str(Decimal(cleaned))
    except InvalidOperation:
        return text
