import io

from fastapi import status

from backend.models import Report, User
from backend.tasks import report_tasks


def _register_and_login(client, password="Very$ecure123"):
    client.post(
        "/api/auth/register",
        data={"email": "user@example.com", "password": password},
    )
    login = client.post(
        "/api/auth/login",
        data={"email": "user@example.com", "password": password},
    )
    token = login.json()["access_token"]
    return token


def test_register_and_login_lists_reports(client):
    token = _register_and_login(client)

    reports = client.get(
        "/api/reports",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert reports.status_code == status.HTTP_200_OK
    assert reports.json() == []


def test_reports_require_auth(client):
    response = client.get("/api/reports")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_upload_enqueues_celery_task(monkeypatch, client):
    token = _register_and_login(client)
    captured = {}

    def fake_delay(report_id, file_path, owner_id):
        captured.update({"report_id": report_id, "file_path": file_path, "owner_id": owner_id})

    monkeypatch.setattr(report_tasks.process_report, "delay", fake_delay)

    response = client.post(
        "/api/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("scan.pdf", io.BytesIO(b"fake pdf"), "application/pdf")},
    )

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert captured["report_id"] == 1
    assert captured["file_path"].endswith("scan.pdf")


def test_report_detail_and_delete_flow(client, db_session):
    token = _register_and_login(client)
    user = db_session.query(User).filter_by(email="user@example.com").first()
    report = Report(title="scan.pdf", owner_id=user.id, status="completed", pdf_report="/uploads/reports/r.pdf")
    db_session.add(report)
    db_session.commit()

    detail = client.get(
        f"/api/reports/{report.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert detail.status_code == status.HTTP_200_OK
    assert detail.json()["title"] == "scan.pdf"

    delete = client.delete(
        f"/api/reports/{report.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete.status_code == status.HTTP_204_NO_CONTENT
    assert db_session.query(Report).filter_by(id=report.id).first() is None
