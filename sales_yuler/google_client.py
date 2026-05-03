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
    if service_account_json:
        info = json.loads(service_account_json)
    elif service_account_file:
        info = json.loads(service_account_file.read_text(encoding="utf-8"))
    else:
        raise RuntimeError("No se recibieron credenciales de Google.")

    credentials = Credentials.from_service_account_info(info, scopes=SCOPES)
    return gspread.authorize(credentials)
