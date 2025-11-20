from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_user
from backend.database import get_db
from backend.models import Report, User
from backend.services import file_processor, validator
from backend.tasks import report_tasks

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_ROOT = file_processor.resolve_upload_root()
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)


@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validator.validate_upload(file.filename or "")
    content = await file.read()
    stored_path = file_processor.save_bytes(content, file.filename, UPLOAD_ROOT)

    report = Report(title=file.filename, status="processing", owner_id=current_user.id)
    db.add(report)
    db.commit()
    db.refresh(report)

    report_tasks.process_report.delay(report.id, str(stored_path), current_user.id)

    return {
        "report_id": report.id,
        "status": "processing",
        "message": "File uploaded. OCR + AI report in progress...",
        "check_status": f"/api/reports/{report.id}",
    }
