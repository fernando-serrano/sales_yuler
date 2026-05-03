from dataclasses import dataclass

import gspread

from sales_yuler.config import SourceConfig


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

        for worksheet in spreadsheet.worksheets():
            rows = worksheet.get_all_records(default_blank="")
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
