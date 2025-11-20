from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_user
from backend.database import get_db
from backend.models import Report, User
from backend.services.file_processor import resolve_upload_root

router = APIRouter(prefix="/reports", tags=["reports"])


def _serialize(report: Report) -> dict:
    preview = (report.ai_summary or "")[:500]
    return {
        "id": report.id,
        "title": report.title,
        "status": report.status,
        "created_at": report.created_at,
        "pdf_report": report.pdf_report,
        "preview": f"{preview}..." if preview else None,
    }


@router.get("/")
def list_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    reports = (
        db.query(Report)
        .filter(Report.owner_id == current_user.id)
        .order_by(Report.created_at.desc())
        .all()
    )
    return [_serialize(report) for report in reports]


@router.get("/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = (
        db.query(Report)
        .filter(Report.id == report_id, Report.owner_id == current_user.id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return {
        "id": report.id,
        "title": report.title,
        "status": report.status,
        "created_at": report.created_at,
        "download_pdf": report.pdf_report,
        "preview": (report.ai_summary or "")[:500],
    }


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = (
        db.query(Report)
        .filter(Report.id == report_id, Report.owner_id == current_user.id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    if report.pdf_report:
        uploads_root = resolve_upload_root()
        relative = Path(report.pdf_report.lstrip("/"))
        relative_parts = list(relative.parts)
        if relative_parts and relative_parts[0] == "uploads":
            relative_parts = relative_parts[1:]
        relative_path = Path(*relative_parts) if relative_parts else Path()
        pdf_path = uploads_root / relative_path
        if pdf_path.exists():
            try:
                pdf_path.unlink()
            except OSError:
                pass

    db.delete(report)
    db.commit()
