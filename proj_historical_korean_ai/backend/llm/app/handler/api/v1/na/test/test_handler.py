from fastapi import APIRouter

from app.config.database_config.database_config_repository import get_scoped_session
from app.dao.member_dao import MbrMemberDao
from app.handler.api.v1.na.test.test_service import TestService
from app.model.vo.result_vo import ResultVo
from app.tool.log_tool import LogTool

logger = LogTool.get_logger()
router: APIRouter = APIRouter(prefix="/test", tags=["/api/v1/na/test"])
service = TestService(
    member_dao=MbrMemberDao(get_scoped_session=get_scoped_session)
)


@router.get("/log")
async def get_log() -> ResultVo:
    return await service.get_log()


@router.get("/env")
async def get_env() -> ResultVo:
    return await service.get_env()


@router.get("/hello/{name}")
async def get_hello_name(name: str) -> ResultVo:
    return await service.get_hello_name(name)


@router.get("/sleep/asyncio")
async def get_sleep_asyncio() -> ResultVo:
    return await service.get_sleep_asyncio()


@router.get("/sleep/time")
async def get_sleep_time() -> ResultVo:
    return await service.get_sleep_time()


@router.get("/result/mutate")
async def get_result_mutate() -> ResultVo:
    return await service.get_result_mutate()


@router.get("/exception500")
async def get_exception500() -> ResultVo:
    return await service.get_exception500()


@router.get("/members/legacy")
async def get_members_legacy() -> ResultVo:
    return await service.get_members_legacy()


@router.get("/members/engine")
async def get_members_engine() -> ResultVo:
    return await service.get_members_engine()


@router.get("/members/session")
async def get_members_session() -> ResultVo:
    return await service.get_members_session()


@router.get("/members/raw")
async def get_members_raw() -> ResultVo:
    return await service.get_members_raw()


@router.get("/members")
async def get_members() -> ResultVo:
    return await service.get_members_session()


@router.get("/member/{member_id}")
async def get_member_id(member_id: str) -> ResultVo:
    return await service.get_member_id(member_id=member_id)


@router.get("/db/pool")
async def get_db_pool() -> ResultVo:
    return await service.get_db_pool()


@router.get("/async/sleep")
async def get_async_sleep() -> ResultVo:
    return await service.get_async_sleep()


@router.get("/async/sleep2")
async def get_async_sleep() -> ResultVo:
    return await service.get_async_sleep()


@router.get("/db/session")
async def get_db_session() -> ResultVo:
    return await service.get_db_session()


@router.get("/sessions")
async def get_sessions() -> ResultVo:
    return await service.get_sessions()
