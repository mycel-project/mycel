from typing import Optional
from pydantic import BaseModel, Field, model_validator


class SettingMeta(BaseModel):
    category: str
    step: int = 1
    unit: Optional[str] = None
    warning: Optional[str] = None
    version: str = "0.1.0"

    def to_json_schema_extra(self) -> dict:
        return self.model_dump(exclude_none=True)

    def to_markdown(self) -> str:
        data = self.model_dump(exclude_none=True)
        return " · ".join(f"**{k}:** {v}" for k, v in data.items())

def meta_field(default, description: str, meta: SettingMeta, **kwargs):
    full_description = f"{description}\n\n{meta.to_markdown()}"
    return Field(
        default=default,
        description=full_description,
        json_schema_extra=meta.to_json_schema_extra(),
        **kwargs,
    )

class UserConf(BaseModel):
    undo_review_max_age: int = meta_field(
        10,
        "Maximum time allowed to undo a review.",
        SettingMeta(category="review", step=5, unit="min", version="0.2.0"),
        ge=0,
        le=60,
    )
    delete_max_age: int = meta_field(
        30,
        "Number of days after which deleted nodes are permanently removed.",
        SettingMeta(
            category="review",
            step=1,
            unit="d",
            warning=(
                "Changing this value will immediately and permanently delete "
                "nodes that have been soft-deleted for longer than the new value."
            ),
            version="0.2.0",
        ),
        ge=0,
        le=90,
    )
    add_extract_to_nav: bool = meta_field(
        True,
        "When extracting, insert it into the navigation history for instant access.",
        SettingMeta(category="review", version="0.2.0"),
    )
    wait_for_due_time: bool = meta_field(
        False,
        "If enabled, nodes due later in the day are never surfaced early, only "
        "nodes whose due time has already passed are reviewed.",
        SettingMeta(category="review", version="0.2.0"),
    )
    ping_frequency: int = meta_field(
        3,
        "When disconnected, application will attempt to reconnect to Mycel at this frequency",
        SettingMeta(category="network", step=1, unit="s", version="0.2.0"),
        ge=1,
        le=60,
    )
    # test_param: str = meta_field(
    #     "default",
    #     "This is a placeholder...",
    #     SettingMeta(category="other"),
    # )
    # test_bool: bool = meta_field(
    #     True,
    #     "Is this a test? yeah!",
    #     SettingMeta(category="other"),
    # )

    @model_validator(mode="before")
    @classmethod
    def clamp_values(cls, data: dict) -> dict:
        if not isinstance(data, dict):
            return data

        for field_name, field_info in cls.model_fields.items():
            if field_name in data and isinstance(data[field_name], (int, float)):
                val = data[field_name]

                f_min = None
                f_max = None

                for m in field_info.metadata:
                    if hasattr(m, 'ge'): f_min = m.ge
                    elif hasattr(m, 'gt'): f_min = m.gt

                    if hasattr(m, 'le'): f_max = m.le
                    elif hasattr(m, 'lt'): f_max = m.lt

                if f_min is not None:
                    val = max(f_min, val)
                if f_max is not None:
                    val = min(f_max, val)

                data[field_name] = val

        return data
