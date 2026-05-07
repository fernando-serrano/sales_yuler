import json
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]


def build_gspread_client(
    service_account_json: str | None = None,
    service_account_file: Path | None = None,
) -> gspread.Client:
    info = _load_service_account_info(
        service_account_json=service_account_json,
        service_account_file=service_account_file,
    )

    credentials = Credentials.from_service_account_info(info, scopes=SCOPES)
    return gspread.authorize(credentials)


def _load_service_account_info(
    service_account_json: str | None = None,
    service_account_file: Path | None = None,
) -> dict:
    json_error: json.JSONDecodeError | None = None

    if service_account_json:
        try:
            return json.loads(service_account_json)
        except json.JSONDecodeError as exc:
            json_error = exc

    if service_account_file:
        return json.loads(service_account_file.read_text(encoding="utf-8"))

    if json_error:
        raise RuntimeError(
            "GOOGLE_SERVICE_ACCOUNT_JSON no contiene un JSON valido y no se configuro "
            "GOOGLE_SERVICE_ACCOUNT_FILE como respaldo."
        ) from json_error

    raise RuntimeError("No se recibieron credenciales de Google.")
