from typing import TypedDict


class FetchResult(TypedDict):
    html: str
    url: str
    title: str | None
