import argparse
import logging

from dotenv import load_dotenv

from sales_yuler.application.pipeline import run_pipeline
from sales_yuler.infrastructure.settings import load_settings, load_sources
from sales_yuler.logging_config import configure_logging, create_run_log_dir
from sales_yuler.progress import TerminalProgress


logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Consolida ventas hacia Google Sheets.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Ejecuta el ETL completo.")
    run_parser.add_argument(
        "--mode",
        choices=["replace", "append"],
        default="append",
        help="append agrega solo filas nuevas con validacion de duplicados; replace rehace la hoja completa.",
    )
    run_parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Muestra logs en la terminal en lugar de la barra de progreso.",
    )

    return parser


def main() -> None:
    run_log_dir = create_run_log_dir()

    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()
    show_progress = args.command == "run" and not args.no_progress
    log_file = configure_logging(run_log_dir, console=not show_progress)
    logger.info("Log de ejecucion creado en %s", log_file)

    if args.command == "run":
        logger.info("Iniciando ETL con modo %s", args.mode)
        settings = load_settings()
        sources = load_sources(settings.sources_config)
        logger.info("Fuentes habilitadas: %s", len(sources))
        progress = TerminalProgress(total_steps=len(sources) + 2) if show_progress else None
        result = run_pipeline(settings=settings, sources=sources, mode=args.mode, progress=progress)
        logger.info(
            "Proceso terminado: %s filas cargadas desde %s fuentes",
            result.rows_loaded,
            result.sources_processed,
        )
        print(
            f"Proceso terminado: {result.rows_loaded} filas cargadas "
            f"desde {result.sources_processed} fuentes."
        )
