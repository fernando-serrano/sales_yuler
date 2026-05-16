import logging
import shutil
from datetime import datetime
from pathlib import Path


MAX_LOG_DIRECTORIES = 10


def create_run_log_dir(
    logs_root: Path = Path("logs"),
    max_directories: int = MAX_LOG_DIRECTORIES,
) -> Path:
    logs_root.mkdir(parents=True, exist_ok=True)
    run_log_dir = _unique_log_dir(logs_root)
    run_log_dir.mkdir()
    _remove_old_log_dirs(logs_root, max_directories=max_directories)
    return run_log_dir


def configure_logging(run_log_dir: Path, console: bool = True) -> Path:
    log_file = run_log_dir / "sales_yuler.log"
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        handler.close()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    if console:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        root_logger.addHandler(stream_handler)

    return log_file


def _unique_log_dir(logs_root: Path) -> Path:
    timestamp = datetime.now().strftime("%d-%m-%Y %H-%M-%S")
    candidate = logs_root / timestamp
    counter = 1

    while candidate.exists():
        candidate = logs_root / f"{timestamp}-{counter:02d}"
        counter += 1

    return candidate


def _remove_old_log_dirs(logs_root: Path, max_directories: int) -> None:
    log_dirs = [path for path in logs_root.iterdir() if path.is_dir()]
    log_dirs.sort(key=lambda path: path.stat().st_ctime)

    for old_dir in log_dirs[:-max_directories]:
        shutil.rmtree(old_dir)
