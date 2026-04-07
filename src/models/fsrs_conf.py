from dataclasses import dataclass

@dataclass
class FsrsConf:
    params: str

    def to_dict(self) -> dict:
        return {
            "params": self.params
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FsrsConf":
        return cls(
            params=data.get("params", "")
        )
