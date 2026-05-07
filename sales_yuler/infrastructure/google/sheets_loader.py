import logging
from typing import Any

import gspread

from sales_yuler.domain.schema import OUTPUT_COLUMNS
from sales_yuler.infrastructure.google.rate_limit import (
    RequestRateLimiter,
    build_read_rate_limiter,
    build_write_rate_limiter,
)


logger = logging.getLogger(__name__)


class GoogleSheetsLoader:
    def __init__(
        self,
        client: gspread.Client,
        spreadsheet_id: str,
        worksheet_name: str,
        read_rate_limiter: RequestRateLimiter | None = None,
        write_rate_limiter: RequestRateLimiter | None = None,
    ) -> None:
        self._read_rate_limiter = read_rate_limiter or build_read_rate_limiter()
        self._write_rate_limiter = write_rate_limiter or build_write_rate_limiter()
        spreadsheet = _rate_limited_call(self._read_rate_limiter, client.open_by_key, spreadsheet_id)
        self._worksheet = _get_or_create_worksheet(
            spreadsheet,
            worksheet_name,
            read_rate_limiter=self._read_rate_limiter,
            write_rate_limiter=self._write_rate_limiter,
        )

    def load(self, rows: list[dict[str, Any]], mode: str) -> int:
        values = [[row.get(column, "") for column in OUTPUT_COLUMNS] for row in rows]

        if mode == "replace":
            logger.info("Limpiando hoja destino y escribiendo %s filas", len(values))
            _rate_limited_call(self._write_rate_limiter, self._worksheet.clear)
            _rate_limited_call(
                self._write_rate_limiter,
                self._worksheet.update,
                [OUTPUT_COLUMNS, *values],
                value_input_option="USER_ENTERED",
            )
            return len(values)

        if not _worksheet_has_header_row(self._worksheet, self._read_rate_limiter):
            logger.info("Hoja destino vacia; escribiendo encabezados")
            _rate_limited_call(
                self._write_rate_limiter,
                self._worksheet.update,
                [OUTPUT_COLUMNS],
                value_input_option="USER_ENTERED",
            )

        if values:
            logger.info("Agregando %s filas al final de la hoja destino", len(values))
            _rate_limited_call(
                self._write_rate_limiter,
                self._worksheet.append_rows,
                values,
                value_input_option="USER_ENTERED",
            )

        return len(values)


def _get_or_create_worksheet(
    spreadsheet: gspread.Spreadsheet,
    title: str,
    read_rate_limiter: RequestRateLimiter,
    write_rate_limiter: RequestRateLimiter,
) -> gspread.Worksheet:
    try:
        return _rate_limited_call(read_rate_limiter, spreadsheet.worksheet, title)
    except gspread.WorksheetNotFound:
        return _rate_limited_call(
            write_rate_limiter,
            spreadsheet.add_worksheet,
            title=title,
            rows=1000,
            cols=len(OUTPUT_COLUMNS),
        )


def _worksheet_has_header_row(
    worksheet: gspread.Worksheet,
    read_rate_limiter: RequestRateLimiter,
) -> bool:
    return bool(_rate_limited_call(read_rate_limiter, worksheet.row_values, 1))


def _rate_limited_call(rate_limiter: RequestRateLimiter, func, *args, **kwargs):
    rate_limiter.wait_for_slot()
    return func(*args, **kwargs)
