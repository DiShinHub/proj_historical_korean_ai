import re

from starlette.requests import Request
from starlette.types import Scope, Receive, Send, ASGIApp

from app.config.authentication_config.authentication_config_repository import authentication_config_repository
from app.config.authentication_config.jwt_authentication_provider import UserDetailsDto, AuthenticationException, \
    JWTAuthenticationEnum
from app.repository.context_repository import context_repository
from app.tool.log_tool import LogTool


class AuthenticationMiddleware:
    __logger = LogTool.get_logger(__qualname__)

    __app: ASGIApp
    __auth_url_pattern: re.Pattern[str]

    def __init__(self, app: ASGIApp) -> None:
        self.__app = app
        self.__auth_url_pattern = re.compile("^/api/[^/]*/au")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.__app(scope, receive, send)
            return

        self._pre_process(scope, receive, send)

        await self.__app(scope, receive, send)

        self._post_process(scope, receive, send)

    def _pre_process(self, scope: Scope, receive: Receive, send: Send) -> None:
        path = scope["path"]
        if self.__auth_url_pattern.match(path) is not None:
            self.__logger.debug(f"AuthMiddleware._pre_process Need Authentication Path = [{path}]")
            try:
                payload: dict = authentication_config_repository.resolve_token_payload(
                    token=authentication_config_repository.get_token_from_request(
                        request=Request(scope)
                    )
                )
                if JWTAuthenticationEnum.TokenType.ACCESS_TOKEN.value != payload.get("type"):
                    raise AuthenticationException()
                elif not payload.get("sub") or not payload.get("seq") or not payload.get("member_type_cd"):
                    raise AuthenticationException()
                user_details: UserDetailsDto = UserDetailsDto(
                    member_id=payload.get("sub"),
                    seq=payload.get("seq"),
                    member_type_cd=payload.get("member_type_cd")
                )
                context_repository.set_user_details(user_details)
            except Exception as e:
                self.__logger.error(f"AuthenticationException = [{e}], Class = [{e.__class__}], Cause = [{e.__cause__}]")
                raise AuthenticationException()

    def _post_process(self, scope: Scope, receive: Receive, send: Send) -> None:
        pass
