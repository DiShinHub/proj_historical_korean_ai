from fastapi import FastAPI, HTTPException
from fastapi.applications import AppType
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, DatabaseError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.base.singleton_meta import SingletonMeta
from app.config.app_config.app_config_repository import app_config_repository
from app.config.app_properties_config.app_properties_config_runner import AppPropertiesConfigRunner
from app.config.authentication_config.authentication_config_runner import AuthenticationConfigRunner
from app.config.authentication_config.jwt_authentication_provider import AuthenticationException, AuthorizationException
from app.config.database_config.database_config_runner import DatabaseConfigRunner
from app.config.redis_config.redis_config_runner import RedisConfigRunner
from app.config.event_handler_config.event_handler_config_runner import EventHandlerConfigRunner
from app.config.logging_config.logging_config_runner import LoggingConfigRunner
from app.config.prometheus_config.prometheus_config_runner import PrometheusConfigRunner
from app.constant.app_properties import app_properties

from app.exception.no_content_exception import NoContentException 
from app.exception.bad_request_exception import BadRequestException 
from app.exception.not_found_exception import NotFoundException
from app.exception.devlab_exception import DevlabException 
from app.exception.no_access_exception import NoAccessException 

from app.handler import router
from app.middleware.authentication_middleware import AuthenticationMiddleware
from app.middleware.common_middleware import CommonMiddleware
from app.middleware.exception_middleware import ExceptionMiddleware
from app.middleware.request_id_middleware import RequestIdMiddleware
from app.model.vo.result_vo import ResultVo, ResultExceptionVo
from app.provider.exception_handler_provider import default_exception_handler

from app.handler.web_socket.web_socket_router import router as websocket_router
from app.tool.log_tool import LogTool


class AppConfigRunner(metaclass=SingletonMeta):
    __logger = LogTool.get_logger(__qualname__)

    def __init__(self):
        self.config_logger()
        self.__logger.info("Initialize Application Config Runner")

    def __call__(self, *args, **kwargs):
        self.run()
        return app_config_repository.get_app()

    def run(self):
        self.__logger.debug("Run Application Config Start")

        # Pre Config
        self.pre_config_app_properties()
        self.pre_config_database()
        self.pre_config_authentication()
        self.pre_config_redis()
        
        # Generate App
        fastapi_app = self.generate_fastapi_app()

        # App Config
        self.config_app_middleware(app=fastapi_app)
        self.config_exception_middleware(app=fastapi_app)
        self.config_app_cors(app=fastapi_app)
        self.config_app_api_router(app=fastapi_app)
        self.config_app_exception_handler(app=fastapi_app)
        self.config_app_prometheus(app=fastapi_app)
        self.config_app_event_handler(app=fastapi_app)

        # 
        self.config_app_web_socket_router(app=fastapi_app)
        
        # Inject To Repository
        self.inject_to_repository(app=fastapi_app)

    def config_logger(self):
        logging_config_runner = LoggingConfigRunner(_is_singleton=True)
        logging_config_runner.run()

    def pre_config_app_properties(self):
        app_properties_config_runner = AppPropertiesConfigRunner(_is_singleton=True)
        app_properties_config_runner.run()
        app_properties_config_runner.print()

    def pre_config_database(self):
        database_config_runner = DatabaseConfigRunner(_is_singleton=True)
        database_config_runner.run(is_async=True)

    def pre_config_redis(self):
        redis_config_runner = RedisConfigRunner(_is_singleton=True)
        redis_config_runner.run()

    def pre_config_authentication(self):
        authentication_config_runner = AuthenticationConfigRunner(_is_singleton=True)
        authentication_config_runner.run()

    def generate_fastapi_app(self) -> AppType:
        return FastAPI(
            debug=app_properties.DEBUG,
            title=app_properties.APP_NAME,
            description=app_properties.APP_DESCRIPTION,
            version=app_properties.APP_VERSION,
            responses={
                200: {"model": ResultVo},
                # 400: {"model": ResultExceptionVo},
                422: {"model": ResultExceptionVo},
            },
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json",
        )

    def config_app_cors(self, app: AppType):
        if app_properties.CORS_ALLOW_ORIGINS:
            app.add_middleware(
                CORSMiddleware,
                allow_origins=app_properties.CORS_ALLOW_ORIGINS,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
                expose_headers=["Authorization", "Authorization-Refresh"],
            )

    def config_exception_middleware(self, app: AppType):
        app.add_middleware(ExceptionMiddleware)

    def config_app_middleware(self, app: AppType):
        app.add_middleware(CommonMiddleware)
        app.add_middleware(AuthenticationMiddleware)
        app.add_middleware(RequestIdMiddleware)

    def config_app_api_router(self, app: AppType):
        app.include_router(router)

    def config_app_web_socket_router(self, app: AppType):
        app.include_router(websocket_router)

    def config_app_exception_handler(self, app: AppType):
        default_exception_list = [
            Exception,
            StarletteHTTPException,
            HTTPException,
            RequestValidationError,
            ValidationError,
            DatabaseError,
            IntegrityError,
            FileNotFoundError,
            ConnectionError,
            TimeoutError,
            TypeError,
            NoContentException,
            BadRequestException,
            AuthenticationException,
            AuthorizationException,
            NotFoundException,
            NoAccessException,
            DevlabException,
        ]

        for item in default_exception_list:
            app.add_exception_handler(item, default_exception_handler)

    def config_app_prometheus(self, app: AppType):
        prometheus_config_runner = PrometheusConfigRunner(_is_singleton=True, app=app)
        prometheus_config_runner.run()

    def config_app_event_handler(self, app: AppType):
        event_handler_config_runner = EventHandlerConfigRunner(_is_singleton=True, app=app)
        event_handler_config_runner.run()

    def inject_to_repository(self, app: AppType):
        app_config_repository.set_app(app)
