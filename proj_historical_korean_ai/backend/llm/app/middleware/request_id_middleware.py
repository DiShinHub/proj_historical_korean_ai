from starlette.types import Scope, Receive, Send, ASGIApp

from app.repository.context_repository import context_repository
from app.tool.log_tool import LogTool


class RequestIdMiddleware:
    """ request_id 를 생성한다.

    Memo:
        - ContextRepository 에서 호출할 수 있다.

        - Logging 에 사용되는 경우: 이곳에서 주입된 contextvars request_id 는 RequestIdLoggingFilter, logger_properties.yml에 사용된다.

        - SqlAlchemy 에 사용되는 경우: 이곳에서 주입된 contextvars request_id 는 DatabaseConfigProvider.get_scope_func 을 override
        하고 각 서비스에서 세션 사용 및 Transactional 데코레이터에서 scoped_session 을 remove 하는데 사용된다.

    """
    __logger = LogTool.get_logger(__qualname__)
    
    __app: ASGIApp

    def __init__(self, app: ASGIApp) -> None:
        self.__app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.__app(scope, receive, send)
            return

        self._pre_process(scope, receive, send)

        await self.__app(scope, receive, send)

        await self._post_process(scope, receive, send)

    def _pre_process(self, scope: Scope, receive: Receive, send: Send) -> None:
        context_repository.set_request_id()

    async def _post_process(self, scope: Scope, receive: Receive, send: Send) -> None:
        pass
