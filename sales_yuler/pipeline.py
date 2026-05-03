from dataclasses import dataclass

from sales_yuler.config import Settings, SourceConfig
from sales_yuler.extractors import GoogleSheetsExtractor
from sales_yuler.google_client import build_gspread_client
from sales_yuler.loaders import GoogleSheetsLoader
from sales_yuler.transformers import normalize_sales_rows


@dataclass(frozen=True)
class PipelineResult:
    rows_loaded: int
    sources_processed: int


def run_pipeline(settings: Settings, sources: list[SourceConfig], mode: str) -> PipelineResult:
    client = build_gspread_client(
        service_account_json=settings.google_service_account_json,
        service_account_file=settings.google_service_account_file,
    )
    extractor = GoogleSheetsExtractor(client)
    loader = GoogleSheetsLoader(
        client=client,
        spreadsheet_id=settings.target_spreadsheet_id,
        worksheet_name=settings.target_worksheet_name,
    )

    all_rows = []
    for source in sources:
        for batch in extractor.extract_source(source):
            all_rows.extend(normalize_sales_rows(batch))

    rows_loaded = loader.load(all_rows, mode=mode)
    return PipelineResult(rows_loaded=rows_loaded, sources_processed=len(sources))
