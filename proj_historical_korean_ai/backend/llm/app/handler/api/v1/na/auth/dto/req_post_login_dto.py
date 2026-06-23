from pydantic import Field

from app.base.base_dto import BaseDto


class ReqPostLoginDto(BaseDto):
    member_id: str = Field(max_length=50)
    member_password: str = Field(max_length=100)
