from pathlib import Path


def normalize_extension(ext: str) -> str:
    if not ext:
        return ""
    return ext.lower() if ext.startswith(".") else f".{ext.lower()}"
