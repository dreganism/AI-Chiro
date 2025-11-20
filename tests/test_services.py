import pytest

from backend.services.validator import validate_upload
from backend.utils.formatters import truncate_text


def test_truncate_text():
    assert truncate_text("hello", 10) == "hello"
    assert truncate_text("abcdefghij", 5) == "ab..."


def test_validate_upload_accepts_known_types():
    validate_upload("scan.pdf")
    validate_upload("image.PNG")


def test_validate_upload_rejects_unknown_types():
    with pytest.raises(Exception):
        validate_upload("malware.exe")
