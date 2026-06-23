import time

from starlette.requests import Request
from starlette.types import ASGIApp, Scope, Receive, Send

from app.tool.log_tool import LogTool


class CommonMiddleware:
    __logger = LogTool.get_logger(__qualname__)

    __app: ASGIApp

    def __init__(self, app: ASGIApp) -> None:
        self.__app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.__app(scope, receive, send)
            return

        start_time: time = time.time()
        self.__logger.debug(f"CommonMiddleware start_time = [{start_time}]")

        self._pre_process(scope, receive, send)

        await self.__app(scope, receive, send)

        self._post_process(scope, receive, send)

        end_time = time.time()
        duration_time = round((end_time - start_time) * 1000, 4)
        self.__logger.debug(f"CommonMiddleware end_time = [{start_time}]")
        self.__logger.debug(f"CommonMiddleware durations = [{duration_time}ms]")

    def _pre_process(self, scope: Scope, receive: Receive, send: Send) -> None:
        request: Request = Request(scope)
        self.__logger.debug(f"===== Request Info ===============================")
        self.__logger.debug(f"= scope_type    = [{scope['type']}]")
        self.__logger.debug(f"= url           = [{request.url}]")
        self.__logger.debug(f"= method        = [{scope['method']}]")
        self.__logger.debug(f"= path          = [{scope['path']}]")
        self.__logger.debug(f"= path_params   = [{request.path_params}]")
        self.__logger.debug(f"= query_params  = [{request.query_params}]")
        self.__logger.debug(f"= content_type  = [{request.headers.get('content-type')}]")
        self.__logger.debug(f"==================================================")

    def _post_process(self, scope: Scope, receive: Receive, send: Send) -> None:
        pass
