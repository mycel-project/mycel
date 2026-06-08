import json
from typing import Annotated, Literal, TypeAlias
from pydantic import BaseModel, Field, RootModel, field_validator

Mono: TypeAlias = str
Poly: TypeAlias = dict[str, str]
Structure: TypeAlias = Mono | Poly
Ord: TypeAlias = int                 

class BaseTemplate(BaseModel):
    id: str # slug for default templates, else UUID?
    name: str
    fields: list[str]

class FragmentTemplate(BaseTemplate):
    kind: Literal["fragment"] = "fragment"
    render_config: Mono

class SporeStandardTemplate(BaseTemplate):
    kind: Literal["spore_standard"] = "spore_standard" 
    render_config: dict[Ord, Structure]

class SporeClozeTemplate(BaseTemplate):
    kind: Literal["spore_cloze"] = "spore_cloze"      
    render_config: Structure
    
Template = Annotated[
    FragmentTemplate | SporeStandardTemplate | SporeClozeTemplate, 
    Field(discriminator="kind")
]

def get_default_templates() -> dict[str, Template]:
    return {
        "fragment_basic": FragmentTemplate(
            id="fragment_basic",
            name="Fragment",
            fields=["content"], 
            render_config="{{content}}" 
        ),
        
        "basic": SporeStandardTemplate(
            id="basic",
            name="Basic",
            fields=["recto", "verso"], 
            render_config={
                0: {
                    "front": "{{recto}}", 
                    "back": "{{recto}}\n{{verso}}"
                }
            }
        ),

        "dual": SporeStandardTemplate(
            id="dual",
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
        
        "cloze": SporeClozeTemplate(
            id="cloze",
            name="Texte à trous",
            fields=["content", "extra"],
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
