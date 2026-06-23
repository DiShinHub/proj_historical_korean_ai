from pydantic import Field

from app.base.base_dto import BaseDto


class ResUsersGetMeDto(BaseDto):
    seq: int = Field(alias="memberSeq")
    member_id: str = Field(alias="memberId")
    member_type_cd: str = Field(alias="memberTypeCd")

    class Config:
        populate_by_name = True
        by_alias = True
