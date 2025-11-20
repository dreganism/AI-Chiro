def truncate_text(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    suffix = "..."
    return value[: max(0, limit - len(suffix))] + suffix
