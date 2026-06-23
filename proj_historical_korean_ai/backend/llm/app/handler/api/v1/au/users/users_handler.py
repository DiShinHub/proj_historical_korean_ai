from fastapi import APIRouter, Depends

from app.config.authentication_config.jwt_authentication_provider import UserDetailsDto
from app.handler.api.v1.au.users.users_service import UsersService
from app.model.vo.result_vo import ResultVo
from app.repository.context_repository import context_repository
from app.tool.log_tool import LogTool

logger = LogTool.get_logger()
router: APIRouter = APIRouter(prefix="/users", tags=["/api/v1/au/users"])
service = UsersService()


@router.get("/me")
async def get_me(
        user_details: UserDetailsDto = Depends(context_repository.get_user_details)
) -> ResultVo:
    return await service.get_me(user_details)
