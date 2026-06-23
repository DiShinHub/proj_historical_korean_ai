import json

from app.config.authentication_config.jwt_authentication_provider import UserDetailsDto
from app.handler.api.v1.au.users.dto.res_users_get_me_dto import ResUsersGetMeDto
from app.model.vo.result_vo import ResultVo
from app.tool.log_tool import LogTool


class UsersService:
    __logger = LogTool.get_logger(__qualname__)

    def __init__(self):
        pass

    async def get_me(self, user_details: UserDetailsDto) -> ResultVo:
        return ResultVo(
            success=True,
            data=json.loads(ResUsersGetMeDto(**user_details.model_dump()).model_dump_json())
        )
