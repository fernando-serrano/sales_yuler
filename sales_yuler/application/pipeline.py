import logging
from dataclasses import dataclass
from typing import Any

from sales_yuler.domain.sales.transformations import normalize_sales_rows
from sales_yuler.infrastructure.google.client import build_gspread_client
from sales_yuler.infrastructure.google.sheets_extractor import GoogleSheetsExtractor
from sales_yuler.infrastructure.google.sheets_loader import GoogleSheetsLoader
from sales_yuler.infrastructure.settings import Settings, SourceConfig


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PipelineResult:
    rows_loaded: int
    sources_processed: int


def run_pipeline(settings: Settings, sources: list[SourceConfig], mode: str) -> PipelineResult:
    logger.info("Construyendo cliente de Google Sheets")
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
        logger.info("Extrayendo fuente: %s", source.name)
        for batch in extractor.extract_source(source):
            normalized_rows = normalize_sales_rows(batch)
            logger.info(
                "Hoja procesada: fuente=%s documento=%s hoja=%s filas_entrada=%s filas_salida=%s",
                source.name,
                batch.document_title,
                batch.worksheet_title,
                len(batch.rows),
                len(normalized_rows),
            )
            all_rows.extend(normalized_rows)

    assign_record_ids(all_rows)
    logger.info("Cargando %s filas en modo %s", len(all_rows), mode)
    rows_loaded = loader.load(all_rows, mode=mode)
    return PipelineResult(rows_loaded=rows_loaded, sources_processed=len(sources))


def assign_record_ids(rows: list[dict[str, Any]]) -> None:
    for index, row in enumerate(rows, start=1):
        row["id registro"] = index
