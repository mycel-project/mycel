from pydantic import BaseModel, ConfigDict
from typing import Optional, Tuple

class FsrsConfUpdate(BaseModel):
    parameters: Optional[Tuple[float, ...]] = None
    desired_retention: Optional[float] = None
    learning_steps: Optional[Tuple[int, ...]] = None
    relearning_steps: Optional[Tuple[int, ...]] = None
    maximum_interval: Optional[int] = None
    enable_fuzzing: Optional[bool] = None
    
    model_config = ConfigDict(validate_assignment=True)
