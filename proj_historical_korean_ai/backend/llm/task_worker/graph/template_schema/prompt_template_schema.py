
from typing import TypedDict, Annotated, Any

class PromptTemplateSchema(TypedDict):
    prompt_mode: Annotated[str, ""]
    prompt_template: Annotated[str, ""]
    prompt_template_system: Annotated[str, ""]
    prompt_template_user: Annotated[str, ""]