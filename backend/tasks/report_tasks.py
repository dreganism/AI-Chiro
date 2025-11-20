from __future__ import annotations

from pathlib import Path

from backend.celery_app import celery_app
from backend.database import SessionLocal
from backend.models import Report
from backend.services import export_service, file_processor, report_generator


@celery_app.task(name="backend.tasks.process_report")
def process_report(report_id: int, file_path: str, owner_id: int) -> None:
    path = Path(file_path)
    db = SessionLocal()
    try:
        raw_text = file_processor.extract_text(path)
        summary = report_generator.generate_summary(raw_text)
        report_dir = file_processor.resolve_upload_root() / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = report_dir / f"report_{report_id}.pdf"
        export_service.render_pdf(summary, raw_text, pdf_path)

        report = (
            db.query(Report)
            .filter(Report.id == report_id, Report.owner_id == owner_id)
            .first()
        )
        if report is None:
            return
        report.raw_text = raw_text
        report.ai_summary = summary
        report.pdf_report = f"/uploads/reports/{pdf_path.name}"
        report.status = "completed"
        db.commit()
    except Exception as exc:
        report = db.query(Report).filter(Report.id == report_id).first()
        if report:
            report.status = "failed"
            report.ai_summary = f"Processing failed: {exc}"[:1000]
            db.commit()
    finally:
        db.close()
        if path.exists():
            try:
                path.unlink()
            except OSError:
                pass
