import re
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

from sales_yuler.domain.sales.field_normalizers import (
    normalize_key,
    normalize_person_name,
    normalize_text,
    normalize_time_text,
)


DEDUP_COLUMNS = [
    "fecha",
    "fuente",
    "documento",
    "hoja",
    "hora",
    "descripcion",
    "monto",
    "cliente",
]


def build_dedup_key(row: Mapping[str, Any]) -> str:
    values = [
        normalize_text(row.get("fecha", "")).casefold(),
        normalize_key(str(row.get("fuente", ""))),
        normalize_text(row.get("documento", "")).casefold(),
        normalize_text(row.get("hoja", "")).casefold(),
        normalize_time_text(row.get("hora", "")),
        normalize_text(row.get("descripcion", "")).casefold(),
        _normalize_money_key(row.get("monto", "")),
        normalize_person_name(row.get("cliente", "")),
    ]
    return "|".join(values)


def filter_new_rows(
    incoming_rows: list[dict[str, Any]],
    existing_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], int]:
    known_keys = {build_dedup_key(row) for row in existing_rows}
    filtered_rows: list[dict[str, Any]] = []
    skipped_duplicates = 0

    for row in incoming_rows:
        dedup_key = build_dedup_key(row)
        if dedup_key in known_keys:
            skipped_duplicates += 1
            continue

        known_keys.add(dedup_key)
        filtered_rows.append(row)

    return filtered_rows, skipped_duplicates


def _normalize_money_key(value: Any) -> str:
    text = str(value).strip()
    if not text:
        return ""

    cleaned = (
        text.replace("S/.", "")
        .replace("s/.", "")
        .replace("S/", "")
        .replace("s/", "")
        .strip()
    )
    cleaned = re.sub(r"\s+", "", cleaned)
    if "," in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    else:
        cleaned = cleaned.replace(",", "")

    try:
        amount = Decimal(cleaned).quantize(Decimal("0.01"))
    except InvalidOperation:
        return normalize_text(text)

    return format(amount, "f")
