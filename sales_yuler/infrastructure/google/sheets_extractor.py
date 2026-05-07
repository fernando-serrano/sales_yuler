import logging
import re
import time
import unicodedata
from dataclasses import dataclass
from typing import Any

import gspread
from gspread.exceptions import APIError

from sales_yuler.domain.dates import worksheet_title_belongs_to_month
from sales_yuler.domain.schema import COLUMN_ALIASES
from sales_yuler.domain.sales.models import SalesBatch
from sales_yuler.infrastructure.settings import SourceConfig


logger = logging.getLogger(__name__)
READ_DELAY_SECONDS = 1.3
MAX_READ_ATTEMPTS = 5
QUOTA_RETRY_SECONDS = 65


@dataclass(frozen=True)
class WorksheetRows(SalesBatch):
    pass


class GoogleSheetsExtractor:
    def __init__(self, client: gspread.Client) -> None:
        self._client = client

    def extract_source(self, source: SourceConfig) -> list[WorksheetRows]:
        spreadsheet = self._client.open_by_url(source.url)
        batches: list[WorksheetRows] = []
        logger.info("Documento abierto: %s", spreadsheet.title)

        for worksheet in spreadsheet.worksheets():
            if not _worksheet_belongs_to_source_month(source, worksheet.title):
                logger.info(
                    "Hoja omitida por no pertenecer al mes configurado: fuente=%s year=%s month=%s hoja=%s",
                    source.name,
                    source.year,
                    source.month,
                    worksheet.title,
                )
                continue

            time.sleep(READ_DELAY_SECONDS)
            rows = _records_from_values(_get_all_values_with_retry(worksheet))
            logger.info("Hoja leida: %s filas=%s", worksheet.title, len(rows))
            if not rows:
                continue

            batches.append(
                WorksheetRows(
                    source=source,
                    document_title=spreadsheet.title,
                    worksheet_title=worksheet.title,
                    rows=rows,
                )
            )

        return batches


def _worksheet_belongs_to_source_month(source: SourceConfig, worksheet_title: str) -> bool:
    return worksheet_title_belongs_to_month(source.year, source.month, worksheet_title)


def _get_all_values_with_retry(worksheet: Any) -> list[list[Any]]:
    for attempt in range(1, MAX_READ_ATTEMPTS + 1):
        try:
            return worksheet.get_all_values()
        except APIError as error:
            if not _is_quota_error(error) or attempt == MAX_READ_ATTEMPTS:
                raise

            wait_seconds = _retry_wait_seconds(error)
            logger.warning(
                "Cuota de lectura excedida al leer hoja=%s. Reintentando en %s segundos (%s/%s)",
                worksheet.title,
                wait_seconds,
                attempt,
                MAX_READ_ATTEMPTS,
            )
            time.sleep(wait_seconds)

    return []


def _is_quota_error(error: APIError) -> bool:
    response = getattr(error, "response", None)
    status_code = getattr(response, "status_code", None)
    return status_code == 429 or "[429]" in str(error)


def _retry_wait_seconds(error: APIError) -> int:
    response = getattr(error, "response", None)
    headers = getattr(response, "headers", {}) or {}
    retry_after = headers.get("Retry-After")
    if retry_after and retry_after.isdigit():
        return max(int(retry_after), QUOTA_RETRY_SECONDS)

    return QUOTA_RETRY_SECONDS


def _records_from_values(values: list[list[Any]]) -> list[dict[str, Any]]:
    if not values:
        return []

    header_index = _find_header_row_index(values)
    headers = _unique_headers(values[header_index])
    records: list[dict[str, Any]] = []

    for values_row in values[header_index + 1 :]:
        if not any(str(value).strip() for value in values_row):
            continue

        row = [
            *values_row,
            *[""] * max(0, len(headers) - len(values_row)),
        ]
        records.append(dict(zip(headers, row[: len(headers)])))

    return records


def _find_header_row_index(values: list[list[Any]]) -> int:
    for index, row in enumerate(values):
        canonical_columns = {
            COLUMN_ALIASES.get(_normalize_header_key(str(cell)))
            for cell in row
            if str(cell).strip()
        }
        canonical_columns.discard(None)

        if {"descripcion", "monto"}.issubset(canonical_columns) and len(canonical_columns) >= 3:
            return index

    return 0


def _normalize_header_key(value: str) -> str:
    value = _repair_mojibake(value)
    without_accents = "".join(
        char
        for char in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(char)
    )
    only_words = re.sub(r"[^a-zA-Z0-9]+", " ", without_accents)
    return re.sub(r"\s+", " ", only_words.strip().lower())


def _repair_mojibake(value: str) -> str:
    if "Ã" not in value and "Â" not in value:
        return value

    repaired = value
    for _ in range(3):
        if "Ã" not in repaired and "Â" not in repaired:
            break

        candidate = None
        for source_encoding in ("cp1252", "latin1"):
            try:
                candidate = repaired.encode(source_encoding).decode("utf-8")
                break
            except UnicodeError:
                continue

        if candidate is None:
            break

        if candidate == repaired:
            break
        repaired = candidate

    return repaired


def _unique_headers(headers: list[Any]) -> list[str]:
    seen: dict[str, int] = {}
    unique_headers: list[str] = []

    for index, header in enumerate(headers, start=1):
        name = str(header).strip() or f"columna {index}"
        seen[name] = seen.get(name, 0) + 1
        unique_headers.append(name if seen[name] == 1 else f"{name} {seen[name]}")

    return unique_headers
