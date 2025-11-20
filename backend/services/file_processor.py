from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Iterable

import pytesseract
from pdf2image import convert_from_path
from PIL import Image

from backend.utils.validators import normalize_extension

DEFAULT_ALLOWED_EXTENSIONS: tuple[str, ...] = (".pdf", ".png", ".jpg", ".jpeg")


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def build_upload_path(filename: str, upload_dir: Path) -> Path:
    ensure_directory(upload_dir)
    safe_name = Path(filename).name
    token = uuid.uuid4().hex
    return upload_dir / f"{token}_{safe_name}"


def save_bytes(content: bytes, filename: str, upload_dir: Path) -> Path:
    destination = build_upload_path(filename, upload_dir)
    with destination.open("wb") as buffer:
        buffer.write(content)
    return destination


def extract_text(file_path: Path) -> str:
    normalized = normalize_extension(file_path.suffix)
    if normalized == ".pdf":
        return _extract_pdf_text(file_path)
    return _extract_image_text(file_path)


def _extract_pdf_text(file_path: Path) -> str:
    text_chunks: list[str] = []
    images = convert_from_path(str(file_path), dpi=300)
    for image in images:
        text_chunks.append(pytesseract.image_to_string(image, lang="eng"))
    return "\n\n".join(chunk.strip() for chunk in text_chunks if chunk.strip())


def _extract_image_text(file_path: Path) -> str:
    with Image.open(file_path) as img:
        return pytesseract.image_to_string(img, lang="eng").strip()


def allowed_file(filename: str, allowed_extensions: Iterable[str] | None = None) -> bool:
    allowed = tuple(ext.lower() for ext in (allowed_extensions or DEFAULT_ALLOWED_EXTENSIONS))
    return normalize_extension(Path(filename).suffix) in allowed


def resolve_upload_root() -> Path:
    return Path(os.getenv("UPLOAD_DIR", "/opt/sjwg-ai-reporter/uploads"))
