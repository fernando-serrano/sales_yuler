import logging
import time
from dataclasses import dataclass
from typing import Any

import gspread
from gspread.exceptions import APIError

from sales_yuler.config import SourceConfig


logger = logging.getLogger(__name__)
READ_DELAY_SECONDS = 1.3
MAX_READ_ATTEMPTS = 5
QUOTA_RETRY_SECONDS = 65


@dataclass(frozen=True)
class WorksheetRows:
    source: SourceConfig
    document_title: str
    worksheet_title: str
    rows: list[dict[str, str]]


class GoogleSheetsExtractor:
    def __init__(self, client: gspread.Client) -> None:
        self._client = client

    def extract_source(self, source: SourceConfig) -> list[WorksheetRows]:
        spreadsheet = self._client.open_by_url(source.url)
        batches: list[WorksheetRows] = []
        logger.info("Documento abierto: %s", spreadsheet.title)

        for worksheet in spreadsheet.worksheets():
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

    headers = _unique_headers(values[0])
    records: list[dict[str, Any]] = []

    for values_row in values[1:]:
        if not any(str(value).strip() for value in values_row):
            continue

        row = [
            *values_row,
            *[""] * max(0, len(headers) - len(values_row)),
        ]
        records.append(dict(zip(headers, row[: len(headers)])))

    return records


def _unique_headers(headers: list[Any]) -> list[str]:
    seen: dict[str, int] = {}
    unique_headers: list[str] = []

    for index, header in enumerate(headers, start=1):
        name = str(header).strip() or f"columna {index}"
        seen[name] = seen.get(name, 0) + 1
        unique_headers.append(name if seen[name] == 1 else f"{name} {seen[name]}")

    return unique_headers
