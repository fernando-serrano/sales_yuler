import re
import unicodedata
from datetime import date, time
from typing import Any

from sales_yuler.date_utils import format_date_ddmmyyyy


_NOISE_ONLY_RE = re.compile(r"^[\s#*._\-\\/|]+$")
_NOISE_TOKEN_RE = re.compile(r"(?<!\w)[#*._\-\\/|]{2,}(?!\w)")


def normalize_text(value: Any) -> str:
    text = _repair_mojibake(str(value or "")).strip()
    if not text:
        return ""

    if _NOISE_ONLY_RE.fullmatch(text):
        return ""

    cleaned = _NOISE_TOKEN_RE.sub(" ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ._-/#*|\\")
    if not cleaned or _NOISE_ONLY_RE.fullmatch(cleaned):
        return ""

    return cleaned


def normalize_person_name(value: Any) -> str:
    text = normalize_text(value)
    return text.upper() if text else ""


def normalize_identifier_text(value: Any) -> str:
    text = normalize_text(value)
    if not text:
        return ""

    digits = re.sub(r"\D+", "", text)
    return digits


def normalize_phone_text(value: Any) -> str:
    return normalize_identifier_text(value)


def normalize_payment_method(value: Any) -> str:
    text = normalize_text(value)
    if not text:
        return ""

    compact = re.sub(r"[^A-Za-z0-9]+", "", text).upper()
    if compact in {"POS", "POSS"}:
        return "POS"

    return text.upper()


def normalize_time_text(value: Any) -> str:
    text = normalize_text(value).lower()
    if not text:
        return ""

    normalized = (
        text.replace(".", ":")
        .replace(" a. m.", " am")
        .replace(" p. m.", " pm")
        .replace(" a.m.", " am")
        .replace(" p.m.", " pm")
        .replace(" am", "am")
        .replace(" pm", "pm")
    )
    normalized = re.sub(r"\s+", "", normalized)

    parsed = _parse_time_text(normalized)
    return parsed.strftime("%H:%M:%S") if parsed else ""


def normalize_date_text(value: date | None) -> str:
    return format_date_ddmmyyyy(value)


def _parse_time_text(value: str) -> time | None:
    for fmt in ("%H:%M:%S", "%H:%M", "%I:%M:%S%p", "%I:%M%p", "%H%M%S", "%H%M"):
        try:
            return time.fromisoformat(value) if fmt == "%H:%M:%S" else _parse_time_with_format(value, fmt)
        except ValueError:
            continue

    return None


def _parse_time_with_format(value: str, fmt: str) -> time:
    from datetime import datetime

    return datetime.strptime(value, fmt).time()


def _repair_mojibake(value: str) -> str:
    if "Ã" not in value and "Â" not in value:
        return value

    try:
        return value.encode("latin1").decode("utf-8")
    except UnicodeError:
        return value


def normalize_key(value: str) -> str:
    value = _repair_mojibake(value)
    without_accents = "".join(
        char
        for char in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(char)
    )
    only_words = re.sub(r"[^a-zA-Z0-9]+", " ", without_accents)
    return re.sub(r"\s+", " ", only_words.strip().lower())
