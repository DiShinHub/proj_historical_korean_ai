from abc import ABCMeta, abstractmethod

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker

from app.tool.log_tool import LogTool


class BaseDatabaseProvider(metaclass=ABCMeta):

    @abstractmethod
    def _create_engine(
            self,
            database_id: str,
            database_password: str,
            database_host: str,
            database_port: int,
            database_scheme: str,
            engine_echo: bool = False
    ):
        """ 엔진을 생성한다. """

    @abstractmethod
    def get_engine(self):
        """ 엔진을 얻는다. """

    @abstractmethod
    def get_session(self):
        """ 세션을 얻는다. """

    @abstractmethod
    def get_session_maker(self):
        """ 세션메이커를 얻는다. """

    def generate_database_url(
            self,
            database_protocol: str,
            database_id: str,
            database_password: str,
            database_host: str,
            database_port: int,
            database_scheme: str
    ) -> str:
        return f"{database_protocol}://{database_id}:{database_password}@{database_host}:{database_port}/{database_scheme}"


class SyncDatabaseProvider(BaseDatabaseProvider):
    __logger = LogTool.get_logger(__qualname__)

    def __init__(
            self,
            database_id: str,
            database_password: str,
            database_host: str,
            database_port: int,
            database_scheme: str,
            engine_echo: bool = False
    ):
        self.__logger.info("Initialize Sync Database Provider")
        self._create_engine(
            database_id=database_id,
            database_password=database_password,
            database_host=database_host,
            database_port=database_port,
            database_scheme=database_scheme,
            engine_echo=engine_echo
        )

    def _create_engine(
            self,
            database_id: str,
            database_password: str,
            database_host: str,
            database_port: int,
            database_scheme: str,
            engine_echo: bool = False
    ):
        self.__logger.debug("Create Sync Database Engine")
        self.engine = create_engine(
            self.generate_database_url(
                database_protocol="postgresql+psycopg2",
                database_id=database_id,
                database_password=database_password,
                database_host=database_host,
                database_port=database_port,
                database_scheme=database_scheme
            ),
            pool_size=50,
            pool_recycle=500,
            max_overflow=20,
            echo=engine_echo
        )

    def get_engine(self) -> Engine:
        return self.engine

    def get_session(self) -> Session:
        return Session(bind=self.engine, autoflush=True, autocommit=False)

    def get_session_maker(self) -> sessionmaker:
        # return sessionmaker(bind=self.get_engine(), class_=Session, expire_on_commit=False)
        return sessionmaker(bind=self.get_engine(), class_=Session, autoflush=True, autocommit=False)


class AsyncDatabaseProvider(BaseDatabaseProvider):
    __logger = LogTool.get_logger(__qualname__)

    def __init__(
            self,
            database_id: str,
            database_password: str,
            database_host: str,
            database_port: int,
            database_scheme: str,
            engine_echo: bool = False
    ):
        self.__logger.info("Initialize Async Database Provider")
        self._create_engine(
            database_id=database_id,
            database_password=database_password,
            database_host=database_host,
            database_port=database_port,
            database_scheme=database_scheme,
            engine_echo=engine_echo
        )

    def _create_engine(
            self,
            database_id: str,
            database_password: str,
            database_host: str,
            database_port: int,
            database_scheme: str,
            engine_echo: bool = False
    ):
        self.__logger.debug("Create Async Database Engine")
        self.engine = create_async_engine(
            self.generate_database_url(
                database_protocol="postgresql+asyncpg",
                database_id=database_id,
                database_password=database_password,
                database_host=database_host,
                database_port=database_port,
                database_scheme=database_scheme
            ),
            pool_pre_ping=True,
            pool_size=50,
            pool_recycle=500,
            max_overflow=20,
            echo=engine_echo
        )

    def get_engine(self) -> AsyncEngine:
        return self.engine

    def get_session(self) -> AsyncSession:
        return AsyncSession(bind=self.engine, expire_on_commit=False)

    def get_session_maker(self) -> async_sessionmaker:
        return async_sessionmaker(bind=self.get_engine(), class_=AsyncSession, expire_on_commit=False)
