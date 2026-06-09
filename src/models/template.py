from enum import Enum
import json
from typing import Annotated, Literal, TypeAlias
from pydantic import BaseModel, Field, RootModel, field_validator

Mono: TypeAlias = str
Poly: TypeAlias = dict[str, str]
Structure: TypeAlias = Mono | Poly
Slot: TypeAlias = int

class DefaultTemplate(str, Enum):
    FRAGMENT_BASIC = "fragment_basic"
    SPORE_BASIC = "spore_basic"
    SPORE_DUAL = "spore_dual"
    SPORE_CLOZE = "spore_cloze"

class BaseTemplate(BaseModel):
    id: str # slug for default templates, else UUID?
    name: str
    fields: list[str]

class FragmentTemplate(BaseTemplate):
    kind: Literal["fragment"] = "fragment"
    render_config: Mono

class SporeStandardTemplate(BaseTemplate):
    kind: Literal["spore_standard"] = "spore_standard" 
    render_config: dict[Slot, Structure]

class SporeClozeTemplate(BaseTemplate):
    kind: Literal["spore_cloze"] = "spore_cloze"      
    render_config: Structure
    
Template = Annotated[
    FragmentTemplate | SporeStandardTemplate | SporeClozeTemplate, 
    Field(discriminator="kind")
]

def get_default_templates() -> dict[str, Template]:
    return {
        DefaultTemplate.FRAGMENT_BASIC: FragmentTemplate(
            id=DefaultTemplate.FRAGMENT_BASIC,
            name="Fragment",
            fields=["content"], 
            render_config="{{content}}" 
        ),
        
        DefaultTemplate.SPORE_BASIC : SporeStandardTemplate(
            id=DefaultTemplate.SPORE_BASIC,
            name="Basic",
            fields=["recto", "verso"], 
            render_config={
                0: {
                    "front": "{{recto}}", 
                    "back": "{{recto}}\n{{verso}}"
                }
            }
        ),
        DefaultTemplate.SPORE_DUAL: SporeStandardTemplate(
            id=DefaultTemplate.SPORE_DUAL,
            name="Dual",
            fields=["recto", "verso"], 
            render_config={
                0: {
                    "front": "{{recto}}", 
                    "back": "{{recto}}\n{{verso}}"
                },
                1: {
                    "front": "{{verso}}", 
                    "back": "{{verso}}\n{{recto}}"
                }
            }
        ),
        DefaultTemplate.SPORE_CLOZE: SporeClozeTemplate(
            id=DefaultTemplate.SPORE_CLOZE,
            name="Texte à trous",
            fields=["cloze", "extra"],
            render_config={
                "front": "{{cloze:content}}",
                "back": "{{cloze:content}}" # same but revealed when building cloze render logic
            }
        )
    }

class Templates(RootModel[dict[str, Template]]):
    root: dict[str, Template] = Field(default_factory=get_default_templates)

    @field_validator("root", mode="before")
    @classmethod
    def parse_json_string(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v
