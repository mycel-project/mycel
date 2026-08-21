from src.formats.markdown import MarkdownFormat

FORMATS_REGISTRY = {
    "markdown": MarkdownFormat(),
}

def get_format(format_id: str):
    if format_id not in FORMATS_REGISTRY:
        raise ValueError(f"Unknown content format: {format_id}")
    return FORMATS_REGISTRY[format_id]

