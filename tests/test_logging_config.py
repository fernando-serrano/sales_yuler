import os
import shutil
from pathlib import Path

from sales_yuler.logging_config import create_run_log_dir


def test_create_run_log_dir_keeps_only_ten_directories():
    logs_test_root = Path(__file__).parent / "logs_test"
    logs_root = logs_test_root / "logs"
    shutil.rmtree(logs_test_root, ignore_errors=True)
    created_dirs = []

    try:
        for index in range(11):
            run_dir = create_run_log_dir(logs_root=logs_root, max_directories=10)
            created_dirs.append(run_dir)
            os.utime(run_dir, (index, index))

        log_dirs = sorted(path.name for path in logs_root.iterdir() if path.is_dir())

        assert len(log_dirs) == 10
        assert not created_dirs[0].exists()
    finally:
        shutil.rmtree(logs_test_root, ignore_errors=True)
