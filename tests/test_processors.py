from backend.services.file_processor import allowed_file


def test_allowed_file_helpers():
    assert allowed_file("report.pdf") is True
    assert allowed_file("report.jpeg") is True
    assert allowed_file("report.exe") is False
