from pathlib import Path

import pytest

from sales_yuler.google_client import _load_service_account_info


def test_load_service_account_info_prefers_valid_json_string():
    info = _load_service_account_info(
        service_account_json='{"type":"service_account","client_email":"bot@example.com"}'
    )

    assert info["type"] == "service_account"
    assert info["client_email"] == "bot@example.com"


def test_load_service_account_info_falls_back_to_file_when_json_env_is_invalid(tmp_path: Path):
    credentials_file = tmp_path / "service-account.json"
    credentials_file.write_text(
        '{"type":"service_account","client_email":"bot@example.com"}',
        encoding="utf-8",
    )

    info = _load_service_account_info(
        service_account_json="bot@example.com",
        service_account_file=credentials_file,
    )

    assert info["client_email"] == "bot@example.com"


def test_load_service_account_info_raises_clear_error_for_invalid_json_without_file():
    with pytest.raises(RuntimeError, match="GOOGLE_SERVICE_ACCOUNT_JSON no contiene un JSON valido"):
        _load_service_account_info(service_account_json="bot@example.com")
