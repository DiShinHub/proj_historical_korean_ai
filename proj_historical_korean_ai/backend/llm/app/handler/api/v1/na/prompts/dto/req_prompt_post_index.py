from pydantic import Field, validator
from app.base.base_dto import BaseDto

class ReqPromptPostIndex(BaseDto):
    prompt: str = Field(description="prompt")
    room_name: str = Field(description="room_name")

    