import argparse

from dotenv import load_dotenv

from sales_yuler.config import load_settings, load_sources
from sales_yuler.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Consolida ventas hacia Google Sheets.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Ejecuta el ETL completo.")
    run_parser.add_argument(
        "--mode",
        choices=["replace", "append"],
        default="replace",
        help="replace limpia la hoja destino antes de cargar; append agrega al final.",
    )

    return parser


def main() -> None:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "run":
        settings = load_settings()
        sources = load_sources(settings.sources_config)
        result = run_pipeline(settings=settings, sources=sources, mode=args.mode)
        print(
            f"Proceso terminado: {result.rows_loaded} filas cargadas "
            f"desde {result.sources_processed} fuentes."
        )
