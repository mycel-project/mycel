from dataclasses import dataclass
from typing import Tuple
from datetime import timedelta


@dataclass
class FsrsConf:
    parameters: Tuple[float, ...] = (
        0.212, 1.2931, 2.3065, 8.2956, 6.4133,
        0.8334, 3.0194, 0.001, 1.8722, 0.1666,
        0.796, 1.4835, 0.0614, 0.2629, 1.6483,
        0.6014, 1.8729, 0.5425, 0.0912, 0.0658,
        0.1542,
    )

    desired_retention: float = 0.9

    learning_steps: Tuple[int, ...] = (60, 600)
    relearning_steps: Tuple[int, ...] = (600,)

    maximum_interval: int = 36500
    enable_fuzzing: bool = True

    def to_fsrs_dict(self) -> dict:
        return {
            "parameters": self.parameters,
            "desired_retention": self.desired_retention,
            "learning_steps": tuple(timedelta(seconds=s) for s in self.learning_steps),
            "relearning_steps": tuple(timedelta(seconds=s) for s in self.relearning_steps),  
            "maximum_interval": self.maximum_interval,
            "enable_fuzzing": self.enable_fuzzing,
        }

    def to_dict(self) -> dict:
        return {
            "parameters": self.parameters,
            "desired_retention": self.desired_retention,
            "learning_steps": self.learning_steps,
            "relearning_steps": self.relearning_steps,
            "maximum_interval": self.maximum_interval,
            "enable_fuzzing": self.enable_fuzzing,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FsrsConf":
        return cls(
            parameters=tuple(data.get("parameters", ())),
            desired_retention=data.get("desired_retention", 0.9),
            learning_steps=tuple(data.get("learning_steps", (60, 600))),
            relearning_steps=tuple(data.get("relearning_steps", (600,))),
            maximum_interval=data.get("maximum_interval", 36500),
            enable_fuzzing=data.get("enable_fuzzing", True),
        )
