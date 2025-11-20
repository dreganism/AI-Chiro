from fastapi import HTTPException, status

from backend.services.file_processor import DEFAULT_ALLOWED_EXTENSIONS, allowed_file


def validate_upload(filename: str) -> None:
    if not allowed_file(filename, DEFAULT_ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Please upload a PDF or image.",
        )
