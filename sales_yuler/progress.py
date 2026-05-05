import shutil
import sys
import time
from dataclasses import dataclass, field
from typing import TextIO


@dataclass
class TerminalProgress:
    total_steps: int
    stream: TextIO = sys.stdout
    width: int = field(default=30)
    started_at: float = field(default_factory=time.monotonic)
    current_step: int = 0
    current_label: str = ""

    def update(self, step: int, label: str) -> None:
        self.current_step = min(max(step, 0), self.total_steps)
        self.current_label = label
        self._render()

    def advance(self, label: str) -> None:
        self.update(self.current_step + 1, label)

    def finish(self, label: str = "Completado") -> None:
        self.update(self.total_steps, label)
        self.stream.write("\n")
        self.stream.flush()

    def _render(self) -> None:
        percent = 100 if self.total_steps == 0 else int((self.current_step / self.total_steps) * 100)
        filled = self.width if self.total_steps == 0 else int((self.current_step / self.total_steps) * self.width)
        bar = "#" * filled + "-" * (self.width - filled)
        elapsed = max(time.monotonic() - self.started_at, 0)
        eta = _format_duration(_estimated_remaining_seconds(elapsed, self.current_step, self.total_steps))
        elapsed_text = _format_duration(elapsed)
        label = _truncate(self.current_label, _label_width())

        self.stream.write(
            f"\r[{bar}] {percent:3d}% | {self.current_step}/{self.total_steps} "
            f"| elapsed {elapsed_text} | ETA {eta} | {label}"
        )
        self.stream.flush()


def _estimated_remaining_seconds(elapsed: float, current_step: int, total_steps: int) -> float | None:
    if current_step <= 0 or total_steps <= 0 or current_step >= total_steps:
        return 0

    seconds_per_step = elapsed / current_step
    return seconds_per_step * (total_steps - current_step)


def _format_duration(seconds: float | None) -> str:
    if seconds is None:
        return "--:--"

    rounded = max(int(seconds), 0)
    minutes, seconds = divmod(rounded, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:d}:{minutes:02d}:{seconds:02d}"

    return f"{minutes:02d}:{seconds:02d}"


def _label_width() -> int:
    terminal_width = shutil.get_terminal_size(fallback=(110, 20)).columns
    return max(20, terminal_width - 80)


def _truncate(value: str, max_width: int) -> str:
    if len(value) <= max_width:
        return value.ljust(max_width)

    return f"{value[: max_width - 3]}..."
