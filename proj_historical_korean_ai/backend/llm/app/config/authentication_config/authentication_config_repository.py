from starlette.requests import Request
from starlette.responses import Response

from app.base.singleton_meta import SingletonMeta
from app.config.authentication_config.jwt_authentication_provider import JWTAuthenticationProvider, \
    JWTAuthenticationEnum


class AuthenticationConfigRepository(metaclass=SingletonMeta):
    __provider_instance: JWTAuthenticationProvider = None

    def __init__(self):
        pass

    def set_provider_instance(self, provider_instance: JWTAuthenticationProvider) -> None:
        if self.__provider_instance is not None:
            raise Exception("Provider Instance Has Already Been Injected.")
        self.__provider_instance = provider_instance

    def resolve_token_payload(
            self,
            token: str,
            options: dict = {}
    ) -> dict:
        return self.__provider_instance.resolve_token_payload(
            token=token,
            options=options
        )

    def get_token_from_request(
            self,
            request: Request,
            token_type: JWTAuthenticationEnum.TokenType = JWTAuthenticationEnum.TokenType.ACCESS_TOKEN,
    ) -> str:
        return self.__provider_instance.get_token_from_request(
            request=request,
            token_type=token_type,
        )

    def generate_token(
            self,
            sub: str,
            token_type: JWTAuthenticationEnum.TokenType = JWTAuthenticationEnum.TokenType.ACCESS_TOKEN,
            **kwargs: dict
    ) -> str:
        return self.__provider_instance.generate_token(
            sub=sub,
            token_type=token_type,
            **kwargs
        )

    def issue_token(
            self,
            response: Response,
            token: str,
            token_type: JWTAuthenticationEnum.TokenType = JWTAuthenticationEnum.TokenType.ACCESS_TOKEN
    ) -> str:
        return self.__provider_instance.issue_token(
            response=response,
            token=token,
            token_type=token_type
        )


authentication_config_repository = AuthenticationConfigRepository()
