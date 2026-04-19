import re

CLOZE_PATTERN = re.compile(r"\{\{c\d+::([^}:]+)(?:::([^}]*))?\}\}")

def transform_cloze(text: str, replacer) -> str:
    return CLOZE_PATTERN.sub(replacer, text)

def cloze_to_ellipsis(text: str) -> str:
    return transform_cloze(text, lambda _: "...")

def cloze_to_plain(text: str) -> str:
    return transform_cloze(text, lambda m: m.group(1))

def cloze_with_wrapper(text: str, prefix: str, suffix: str) -> str:
    return transform_cloze(
        text,
        lambda m: f"{prefix}{m.group(1)}{suffix}"
    )
