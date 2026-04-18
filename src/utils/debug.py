def preview_extract(s: str, n: int = 20) -> str:
    if not s:
        return "<empty>"

    if len(s) <= 2 * n:
        return s

    return f"{s[:n]}...{s[-n:]} (len={len(s)})"
