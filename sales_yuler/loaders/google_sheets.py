import logging
from typing import Any

import gspread

from sales_yuler.schema import OUTPUT_COLUMNS


logger = logging.getLogger(__name__)


class GoogleSheetsLoader:
    def __init__(self, client: gspread.Client, spreadsheet_id: str, worksheet_name: str) -> None:
        spreadsheet = client.open_by_key(spreadsheet_id)
        self._worksheet = _get_or_create_worksheet(spreadsheet, worksheet_name)

    def load(self, rows: list[dict[str, Any]], mode: str) -> int:
        values = [[row.get(column, "") for column in OUTPUT_COLUMNS] for row in rows]

        if mode == "replace":
            logger.info("Limpiando hoja destino y escribiendo %s filas", len(values))
            self._worksheet.clear()
            self._worksheet.update([OUTPUT_COLUMNS, *values], value_input_option="USER_ENTERED")
            return len(values)

        if not self._worksheet.get_all_values():
            logger.info("Hoja destino vacia; escribiendo encabezados")
            self._worksheet.update([OUTPUT_COLUMNS], value_input_option="USER_ENTERED")

        if values:
            logger.info("Agregando %s filas al final de la hoja destino", len(values))
            self._worksheet.append_rows(values, value_input_option="USER_ENTERED")

        return len(values)


def _get_or_create_worksheet(spreadsheet: gspread.Spreadsheet, title: str) -> gspread.Worksheet:
    try:
        return spreadsheet.worksheet(title)
    except gspread.WorksheetNotFound:
        return spreadsheet.add_worksheet(title=title, rows=1000, cols=len(OUTPUT_COLUMNS))
