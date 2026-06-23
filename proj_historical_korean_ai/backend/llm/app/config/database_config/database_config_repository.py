import uuid

from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, async_sessionmaker, AsyncEngine
from sqlalchemy.orm import Session, declarative_base, sessionmaker, scoped_session

from app.base.singleton_meta import SingletonMeta
from app.config.database_config.database_config_provider import BaseDatabaseProvider
from app.repository.context_repository import context_repository


class DatabaseConfigRepository(metaclass=SingletonMeta):
    __base = None
    __is_async: bool = None
    __provider_instance: BaseDatabaseProvider = None
    __scoped_session = None

    def __init__(self):
        self.__base = declarative_base()

    def set_provider_instance(self, is_async: bool, provider_instance: BaseDatabaseProvider) -> None:
        if self.__provider_instance is not None:
            raise Exception("Provider Instance Has Already Been Injected.")
        self.__is_async = is_async
        self.__provider_instance = provider_instance
        self.__scoped_session = self.__get_scoped_session()

    def __get_session_maker(self) -> async_sessionmaker | sessionmaker:
        if self.__provider_instance is None:
            raise Exception("No Provider Has Been Injected Yet.")
        return self.__provider_instance.get_session_maker()

    def __get_scope_func(self):
        # return asyncio.current_task()
        # return context_repository.get_request_id()
        # return context_repository.get_request_id() if context_repository.get_use_transactional() else str(uuid.uuid4())
        return (
            context_repository.get_transaction_ids()[len(context_repository.get_transaction_ids()) - 1]
        ) if (
                context_repository.get_use_transactional()
                and context_repository.get_transaction_ids()
                and len(context_repository.get_transaction_ids()) > 0
        ) else (
            context_repository.get_request_id()
        )

    def __get_scoped_session(self) -> Session | scoped_session | AsyncSession | async_scoped_session:
        if self.__is_async is False:
            return scoped_session(
                session_factory=self.__get_session_maker(),
                scopefunc=self.__get_scope_func
            )
        else:
            return async_scoped_session(
                session_factory=self.__get_session_maker(),
                scopefunc=self.__get_scope_func
            )

    def get_provider_instance(self) -> BaseDatabaseProvider:
        if self.__provider_instance is None:
            raise Exception("No Provider Has Been Injected Yet.")
        return self.__provider_instance

    def get_engine(self) -> AsyncEngine | Engine:
        if self.__provider_instance is None:
            raise Exception("No Provider Has Been Injected Yet.")
        return self.__provider_instance.get_engine()

    def get_session(self) -> AsyncSession | Session:
        if self.__provider_instance is None:
            raise Exception("No Provider Has Been Injected Yet.")
        return self.__provider_instance.get_session()

    def get_scoped_session(self) -> AsyncSession | async_scoped_session | Session | sessionmaker:
        if self.__provider_instance is None:
            raise Exception("No Provider Has Been Injected Yet.")
        if self.__scoped_session is None:
            raise Exception("No Scoped Session Has Been Injected Yet.")
        return self.__scoped_session

    def get_base(self):
        return self.__base


database_config_repository = DatabaseConfigRepository()

Base = database_config_repository.get_base()
get_engine = database_config_repository.get_engine
get_session = database_config_repository.get_session
get_scoped_session = database_config_repository.get_scoped_session
