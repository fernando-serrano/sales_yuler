import logging
from dataclasses import dataclass
from typing import Any, Protocol

from sales_yuler.domain.dates import build_processing_window, source_month_intersects_window
from sales_yuler.domain.sales.deduplication import filter_new_rows
from sales_yuler.domain.sales.transformations import normalize_sales_rows
from sales_yuler.infrastructure.google.client import build_gspread_client
from sales_yuler.infrastructure.google.rate_limit import build_read_rate_limiter, build_write_rate_limiter
from sales_yuler.infrastructure.google.sheets_extractor import GoogleSheetsExtractor
from sales_yuler.infrastructure.google.sheets_loader import GoogleSheetsLoader
from sales_yuler.infrastructure.settings import Settings, SourceConfig


logger = logging.getLogger(__name__)


class ProgressReporter(Protocol):
    def update(self, step: int, label: str) -> None: ...

    def advance(self, label: str) -> None: ...

    def finish(self, label: str = "Completado") -> None: ...


@dataclass(frozen=True)
class PipelineResult:
    rows_loaded: int
    sources_processed: int


def run_pipeline(
    settings: Settings,
    sources: list[SourceConfig],
    mode: str,
    progress: ProgressReporter | None = None,
) -> PipelineResult:
    if progress:
        progress.update(0, "Conectando con Google Sheets")

    logger.info("Construyendo cliente de Google Sheets")
    client = build_gspread_client(
        service_account_json=settings.google_service_account_json,
        service_account_file=settings.google_service_account_file,
    )
    read_rate_limiter = build_read_rate_limiter()
    write_rate_limiter = build_write_rate_limiter()
    extractor = GoogleSheetsExtractor(client, rate_limiter=read_rate_limiter)
    loader = GoogleSheetsLoader(
        client=client,
        spreadsheet_id=settings.target_spreadsheet_id,
        worksheet_name=settings.target_worksheet_name,
        read_rate_limiter=read_rate_limiter,
        write_rate_limiter=write_rate_limiter,
    )

    window_start, window_end = build_processing_window(
        end_date=settings.processing_date,
        lookback_days=settings.lookback_days,
    )
    eligible_sources = [
        source
        for source in sources
        if source_month_intersects_window(
            source.year,
            source.month,
            start_date=window_start,
            end_date=window_end,
        )
    ]
    logger.info(
        "Ventana de procesamiento: desde=%s hasta=%s fuentes_elegibles=%s fuentes_totales=%s",
        window_start,
        window_end,
        len(eligible_sources),
        len(sources),
    )
    if progress:
        progress.update(1, f"Fuentes elegibles: {len(eligible_sources)}")

    all_rows = []
    for source_index, source in enumerate(eligible_sources, start=1):
        if progress:
            progress.update(source_index + 1, f"Extrayendo {source.name}")

        logger.info("Extrayendo fuente: %s", source.name)
        for batch in extractor.extract_source_with_window(
            source=source,
            start_date=window_start,
            end_date=window_end,
        ):
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

        if progress:
            progress.update(source_index + 1, f"Procesada {source.name}")

    if progress:
        progress.update(len(eligible_sources) + 1, "Preparando carga")

    rows_to_load = all_rows
    if mode == "append":
        existing_rows = loader.read_existing_rows()
        rows_to_load, duplicates_skipped = filter_new_rows(all_rows, existing_rows)
        next_record_id = loader.next_record_id()
        assign_record_ids(rows_to_load, start=next_record_id + 1)
        logger.info(
            "Append idempotente: filas_entrada=%s duplicados_omitidos=%s filas_nuevas=%s",
            len(all_rows),
            duplicates_skipped,
            len(rows_to_load),
        )
    else:
        assign_record_ids(rows_to_load)

    logger.info("Cargando %s filas en modo %s", len(rows_to_load), mode)
    rows_loaded = loader.load(rows_to_load, mode=mode)
    if progress:
        progress.finish(f"Completado: {rows_loaded} filas")

    return PipelineResult(rows_loaded=rows_loaded, sources_processed=len(eligible_sources))


def assign_record_ids(rows: list[dict[str, Any]], start: int = 1) -> None:
    for index, row in enumerate(rows, start=start):
        row["id registro"] = index
