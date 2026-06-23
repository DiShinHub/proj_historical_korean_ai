import json
import traceback

from starlette.types import Scope, Receive, Send, ASGIApp

from app.config.authentication_config.jwt_authentication_provider import AuthenticationException
from app.model.vo.result_vo import ResultVo
from app.tool.log_tool import LogTool


class ExceptionMiddleware:
    """ middleware의 예외를 처리한다.

    Memo:
        -

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

        try:
            await self.__app(scope, receive, send)
        except Exception as e:
            self.__logger.error(
                f"ExceptionMiddleware = [{e}], Class = [{e.__class__}], Cause = [{e.__cause__}]\n{traceback.format_exc()}")

            status_code = 500
            body = ResultVo(success=False, message="Internal Server Error")

            if e.__class__ is AuthenticationException:
                status_code = 401
                body = ResultVo(success=False, message="Unauthorized")
            else:
                pass

            await send({
                "type": "http.response.start",
                "status": status_code,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"cache-control", b"no-cache")
                ]
            })
            await send({
                "type": "http.response.body",
                "body": json.dumps(body.dict()).encode("utf-8")
            })
            return

        await self._post_process(scope, receive, send)

    def _pre_process(self, scope: Scope, receive: Receive, send: Send) -> None:
        pass

    async def _post_process(self, scope: Scope, receive: Receive, send: Send) -> None:
        pass
