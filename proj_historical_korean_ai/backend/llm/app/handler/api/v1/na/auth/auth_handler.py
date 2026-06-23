from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import Response

from app.config.authentication_config.authentication_config_repository import authentication_config_repository
from app.config.database_config.database_config_repository import get_scoped_session
from app.dao.member_auth_jwt_dao import MbrMemberAuthJwtDao
from app.dao.member_dao import MbrMemberDao
from app.handler.api.v1.na.auth.auth_service import AuthService
from app.handler.api.v1.na.auth.dto.req_post_login_dto import ReqPostLoginDto
from app.model.vo.result_vo import ResultVo
from app.tool.log_tool import LogTool

logger = LogTool.get_logger()
router: APIRouter = APIRouter(prefix="/auth", tags=["/api/v1/na/auth"])
service = AuthService(
    authentication_config_repository=authentication_config_repository,
    member_dao=MbrMemberDao(get_scoped_session=get_scoped_session),
    member_auth_jwt_dao=MbrMemberAuthJwtDao(get_scoped_session=get_scoped_session),
)


@router.post("/login")
async def post_login(request_dto: ReqPostLoginDto, response: Response) -> ResultVo:
    return await service.post_login(request_dto, response)


@router.post("/refresh")
async def post_refresh(request: Request, response: Response) -> ResultVo:
    return await service.post_refresh(request, response)
