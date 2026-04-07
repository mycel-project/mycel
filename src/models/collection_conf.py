from dataclasses import dataclass

@dataclass
class CollectionConf:
    theme: str

    def to_dict(self) -> dict:
        return {
            "theme": self.theme
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CollectionConf":
        return cls(
            theme=data.get("theme", "")
        )
