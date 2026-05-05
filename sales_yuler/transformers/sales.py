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
        if _is_cash_out_row(row) or not _is_valid_sale_row(row):
            continue

        normalized = {column: row.get(column, "") for column in CANONICAL_COLUMNS}
        normalized["nro"] = len(normalized_rows) + 1
        normalized["fecha"] = _format_date(sale_date)
        normalized["cantidad"] = _normalize_quantity(normalized["cantidad"])
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
    only_words = re.sub(r"[^a-zA-Z0-9]+", " ", without_accents)
    cleaned = re.sub(r"\s+", " ", only_words.strip().lower())
    return cleaned


def _is_valid_sale_row(row: dict[str, Any]) -> bool:
    description = str(row.get("descripcion", "")).strip()
    amount = _money_as_decimal(row.get("monto", ""))
    return bool(description) and amount is not None and amount > 0


def _is_cash_out_row(row: dict[str, Any]) -> bool:
    fields = ["descripcion", "cliente", "metodo de pago", "encargado"]
    text = " ".join(str(row.get(field, "")).strip().lower() for field in fields)
    return "salida de caja" in text or "salidas de caja" in text


def _date_from_worksheet(year: int, month: int, worksheet_title: str) -> date | None:
    full_date = _parse_date_text(worksheet_title)
    if full_date:
        return full_date

    match = re.search(r"\d{1,2}", worksheet_title)
    if not match:
        return None

    day = int(match.group())
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _parse_date_text(value: Any) -> date | None:
    text = str(value).strip()
    iso_match = re.search(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b", text)
    if iso_match:
        year = int(iso_match.group(1))
        month = int(iso_match.group(2))
        day = int(iso_match.group(3))
        try:
            return date(year, month, day)
        except ValueError:
            return None

    match = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2}|\d{4})\b", text)
    if not match:
        return None

    day = int(match.group(1))
    month = int(match.group(2))
    year = int(match.group(3))
    if year < 100:
        year += 2000

    try:
        return date(year, month, day)
    except ValueError:
        return None


def _format_date(value: date | None) -> str:
    return value.strftime("%d/%m/%Y") if value else ""


def _normalize_quantity(value: Any) -> Any:
    text = str(value).strip()
    return 1 if not text else value


def _normalize_money(value: Any) -> Any:
    amount = _money_as_decimal(value)
    if amount is None:
        return str(value).strip()

    return float(amount)


def _money_as_decimal(value: Any) -> Decimal | None:
    text = str(value).strip()
    if not text:
        return None

    cleaned = (
        text.replace("S/.", "")
        .replace("s/.", "")
        .replace("S/", "")
        .replace("s/", "")
        .strip()
    )
    cleaned = re.sub(r"\s+", "", cleaned)
    if "," in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    else:
        cleaned = cleaned.replace(",", "")

    try:
        amount = Decimal(cleaned).quantize(Decimal("0.01"))
    except InvalidOperation:
        return None

    return amount
