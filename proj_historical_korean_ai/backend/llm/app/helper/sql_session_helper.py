from sqlalchemy import Executable, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.repository.context_repository import context_repository
from app.tool.log_tool import LogTool


class SqlSessionHelper:

    @staticmethod
    async def execute(session: AsyncSession | Session, stmt: Executable) -> Result:
        logger = LogTool.get_logger(__name__)
        logger.debug(f"SqlSessionHelper.execute, Use Transactional={context_repository.get_use_transactional()}")
        logger.debug(f"SqlSessionHelper.execute, Sql Session Hash={hash(session)}")
        if context_repository.get_use_transactional():
            return await session.execute(stmt)
        else:
            try:
                async with session.begin():
                    result = await session.execute(stmt)
                    await session.commit()
                    return result
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()
