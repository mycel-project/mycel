from dataclasses import dataclass


@dataclass
class FetchResult:
    html: str
    url: str
    title: str | None
