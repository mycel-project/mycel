from pydantic import BaseModel, model_validator, Field


class UserConf(BaseModel):
    undo_review_max_age: int = Field(
        default=10,
        ge=0,
        le=60,
        description="Maximum time allowed to undo a review.",
        json_schema_extra={
            "category": "review",
            "step": 5,
            "unit": "min"
        }
    )
    delete_max_age: int = Field(
        default=30,
        ge=0,
        le=90,
        description="Number of days after which deleted nodes are permanently removed.",
        json_schema_extra={
            "category": "review",
            "step": 1,
            "unit": "d",
            "warning": "Changing this value will immediately and permanently delete nodes that have been soft-deleted for longer than the new value."
        }
    )
    ping_frequency: int = Field(
        default=3,
        ge=1,
        le=60,
        description="When disconnected, application will attempt to reconnect to Mycel at this frequency",
        json_schema_extra={
            "category": "network",
            "step": 1,
            "unit": "s"
        }
    )
    # test_param: str = Field(
    #     default="default",
    #     description="This is a placeholder...",
    #     json_schema_extra={
    #         "category": "other",
    #     }
    # )
    # test_bool: bool = Field(
    #     default=True,
    #     description="Is this a test? yeah!",
    #     json_schema_extra={
    #         "category": "other",
    #     }
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
