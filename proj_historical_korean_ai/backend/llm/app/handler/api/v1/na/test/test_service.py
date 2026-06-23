import asyncio
import time

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.future import select
from sqlalchemy.pool import AsyncAdaptedQueuePool

from app.config.database_config.database_config_repository import get_engine, get_session, get_scoped_session
from app.constant.app_properties import app_properties
from app.dao.member_dao import MbrMemberDao
from app.decoration.transactional import Transactional
from app.model.entity.member_entity import MemberEntity
from app.model.vo.result_vo import ResultVo
from app.tool.log_tool import LogTool
from app.tool.sql_tool import SqlTool


class TestService:
    __logger = LogTool.get_logger(__qualname__)

    __member_dao: MbrMemberDao

    def __init__(self, member_dao: MbrMemberDao):
        self.__member_dao = member_dao
        self.session = None

    async def get_log(self) -> ResultVo:
        self.__logger.debug("##### debug")
        self.__logger.info("##### info")
        self.__logger.warning("##### warn")
        self.__logger.error("##### error")
        return ResultVo(success=True)

    async def get_env(self) -> ResultVo:
        return ResultVo(data=app_properties.dict())

    async def get_hello_name(self, name: str) -> ResultVo:
        return ResultVo(success=True, message=f"Hello {name}")

    async def get_sleep_asyncio(self) -> ResultVo:
        await asyncio.sleep(5)
        return ResultVo(success=True)

    async def get_sleep_time(self) -> ResultVo:
        time.sleep(5)
        return ResultVo(success=True)

    async def get_result_mutate(self) -> ResultVo:
        result = ResultVo(success=True)
        self.__logger.info(f"result before mutate = [{result}]")
        result.success = False
        self.__logger.info(f"result after mutate = [{result}]")
        return ResultVo(success=True)

    async def get_exception500(self) -> ResultVo:
        raise Exception("exception message")
        return ResultVo(success=True)

    async def get_members_legacy(self) -> ResultVo:
        # 사용 금지
        session = get_session()
        stmt = select(MemberEntity)
        result = await session.execute(stmt)
        members = result.scalars().fetchall()
        return ResultVo(success=True, data={
            "members": [SqlTool.base_to_dict(item) for item in members]
        })

    async def get_members_engine(self) -> ResultVo:
        stmt = select(MemberEntity)
        async with get_engine().connect() as conn:
            result = await conn.execute(stmt)
        return ResultVo(success=True, data={
            "members": [SqlTool.base_to_dict(MemberEntity(**(item._mapping))) for item in result.fetchall()]
        })

    @Transactional()
    async def get_members_raw(self) -> ResultVo:
        member_list = await self.__member_dao.get_member_list_raw()
        return ResultVo(success=True, data={
            "members": [SqlTool.base_to_dict(item) for item in member_list]
        })

    @Transactional()
    async def get_members_session(self) -> ResultVo:
        # scoped_session = get_scoped_session()
        member_list = await self.__member_dao.get_member_list()
        return ResultVo(success=True, data={
            "members": [SqlTool.base_to_dict(item) for item in member_list]
        })

    @Transactional()
    async def get_member_id(self, member_id: str) -> ResultVo:
        member_by_id = await self.__member_dao.get_member_by_id(member_id=member_id)
        print(vars(member_by_id))
        member_by_seq = await self.__member_dao.get_member_by_member_seq(seq=1)
        print(vars(member_by_seq))
        return ResultVo(success=True, data=dict(member=""))

    async def get_db_pool(self) -> ResultVo:
        async_engine: AsyncEngine = get_engine()
        pool: AsyncAdaptedQueuePool = async_engine.sync_engine.pool
        print(vars(pool))
        return ResultVo(success=True, data=dict(pool=pool.status()))

    async def get_async_sleep(self) -> ResultVo:
        data = await self.wait()
        return ResultVo(
            success=True,
            data=data
        )

    async def wait(self) -> dict:
        start_time = time.time()
        self.__logger.debug(f"sleep start, now = [{start_time}]")

        loop_interval = 5
        loop_count = 0
        while time.time() - start_time < loop_interval:
            loop_count += 1
            # time.sleep(0.1)
            await asyncio.sleep(0.001)

        self.__logger.debug(
            f"sleep end, during_time = [{time.time() - start_time}], loop_interval = [{loop_interval}], loop_count = [{loop_count}]")
        return {
            "start_time": start_time, "during_time": time.time() - start_time, "loop_interval": loop_interval,
            "loop_count": loop_count
        }

    async def get_db_session(self) -> ResultVo:
        session = get_session()
        print(session.begin())

        return ResultVo(success=True)

    async def get_sessions(self) -> ResultVo:
        scoped_session = get_scoped_session()
        registry = scoped_session.registry.registry
        print(registry)
        return ResultVo(success=True, data={"sessions_count": len(registry), "sessions": registry})
