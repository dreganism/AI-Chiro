from fastapi import APIRouter, File, UploadFile, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Report, User
from backend.auth.dependencies import get_current_user
from datetime import datetime
import os
import uuid
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import io

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = "/opt/sjwg-ai-reporter/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(f"{UPLOAD_DIR}/reports", exist_ok=True)

def ocr_file(file_path: str) -> str:
    text = ""
    if file_path.lower().endswith('.pdf'):
        images = convert_from_path(file_path, dpi=300)
        for img in images:
            text += pytesseract.image_to_string(img, lang='eng') + "\n\n"
    else:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img, lang='eng')
    return text.strip()

def generate_report(raw_text: str, report_id: str, db: Session, owner_id: int):
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY", "your-key-here"))
    
    prompt = f"""
You are an expert medical-legal reporter. Generate a professional, structured medical report from this raw OCR text.
Use clear sections: Patient Info, History, Examination, Diagnosis, Plan.
Keep it concise and professional.

Raw text:
{raw_text[:15000]}
"""
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-70b-versatile",
            temperature=0.3,
            max_tokens=2000
        )
        summary = chat_completion.choices[0].message.content
    except:
        summary = "AI summary failed (check GROQ_API_KEY or use local LLM)"

    # Generate beautiful PDF with WeasyPrint
    from weasyprint import HTML
    html = f"""
    <h1>Medical Report - {datetime.now().strftime('%Y-%m-%d')}</h1>
    <h2>AI Summary</h2>
    <pre>{summary}</pre>
    <h2>Raw OCR Text</h2>
    <pre style="font-size:10px">{raw_text[:30000]}</pre>
    """
    pdf_path = f"{UPLOAD_DIR}/reports/report_{report_id}.pdf"
    HTML(string=html).write_pdf(pdf_path)

    # Update DB
    report = db.query(Report).filter(Report.id == report_id).first()
    report.ai_summary = summary
    report.pdf_report = f"/uploads/reports/report_{report_id}.pdf"
    report.status = "completed"
    db.commit()

@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    file_id = str(uuid.uuid4())
    file_path = f"{UPLOAD_DIR}/{file_id}_{file.filename}"
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    report = Report(
        title=file.filename,
        status="processing",
        owner_id=current_user.id
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    background_tasks.add_task(generate_report, file_path, report.id, db, current_user.id)

    return {
        "report_id": report.id,
        "status": "processing",
        "message": "File uploaded. OCR + AI report in progress...",
        "check_status": f"/api/reports/{report.id}"
    }

@router.get("/reports/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    report = db.query(Report).filter(Report.id == report_id, Report.owner_id == user.id).first()
    if not report:
        return JSONResponse(status_code=404, content={"error": "Report not found"})
    return {
        "id": report.id,
        "title": report.title,
        "status": report.status,
        "created_at": report.created_at,
        "download_pdf": report.pdf_report,
        "preview": report.ai_summary[:500] + "..." if report.ai_summary else None
    }
