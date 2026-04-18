from dataclasses import dataclass

@dataclass
class TextSegment:
    before: str
    target: str
    after: str
