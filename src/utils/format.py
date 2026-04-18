import re

def ensure_double_newline_left(text: str) -> str:
    return re.sub(r"\n{0,2}$", "\n\n", text)

def ensure_double_newline_right(text: str) -> str:
    return re.sub(r"^\n{0,2}", "\n\n", text)
