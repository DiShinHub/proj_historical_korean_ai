from datetime import datetime, timezone, timedelta
from enum import Enum

import jwt
from starlette.requests import Request
from starlette.responses import Response

from app.base.base_dto import BaseDto
from app.base.singleton_meta import SingletonMeta
from app.tool.cipher_tool import CipherTool
from app.tool.log_tool import LogTool


class AuthenticationException(Exception):
    """ 인증 실패 하였을때 해당 예외가 발생한다. """


class AuthorizationException(Exception):
    """ 인가를 획득하지 못하였을때 해당 예외가 발생한다. """


class JWTNotFoundException(Exception):
    """ 인증토큰을 찾지 못하였을때 해당 예외가 발생한다. """


class JWTAuthenticationEnum:
    class TokenType(str, Enum):
        ACCESS_TOKEN = "access"
        REFRESH_TOKEN = "refresh"


class UserDetailsDto(BaseDto):
    seq: int
    member_id: str
    member_type_cd: str


class JWTAuthenticationProvider(metaclass=SingletonMeta):
    __logger = LogTool.get_logger(__qualname__)

    __SECRET_KEY: str
    __ENCRYPT_USE: bool
    __ENCRYPT_KEY: str
    __ACCESS_TOKEN_NAME: str
    __REFRESH_TOKEN_NAME: str
    __ACCESS_TOKEN_VALIDITY_IN_MILLISECONDS: int
    __REFRESH_TOKEN_VALIDITY_IN_MILLISECONDS: int
    __JWT_ALGORITHMS: str

    def __init__(
            self,
            secret_key: str,
            encrypt_use: bool,
            encrypt_key: str,
            access_token_name: str,
            refresh_token_name: str,
            access_token_validity_in_milliseconds: int,
            refresh_token_validity_in_milliseconds: int,
            jwt_algorithms: str
    ):
        self.__SECRET_KEY = secret_key
        self.__ENCRYPT_USE = encrypt_use
        self.__ENCRYPT_KEY = encrypt_key
        self.__ACCESS_TOKEN_NAME = access_token_name
        self.__REFRESH_TOKEN_NAME = refresh_token_name
        self.__ACCESS_TOKEN_VALIDITY_IN_MILLISECONDS = access_token_validity_in_milliseconds
        self.__REFRESH_TOKEN_VALIDITY_IN_MILLISECONDS = refresh_token_validity_in_milliseconds
        self.__JWT_ALGORITHMS = jwt_algorithms

    def resolve_token_payload(
            self,
            token: str,
            options: dict = {}
    ) -> dict:
        try:
            if self.__ENCRYPT_USE:
                token = self.__decrypt_token(token)
            token_payload = self.__decode_token(token=token, options=options)
        except jwt.InvalidSignatureError as e:
            self.__logger.error(f"InvalidSignatureError = [{e}], Cause = [{e.__cause__}]")
            raise e
        except jwt.ExpiredSignatureError as e:
            self.__logger.error(f"ExpiredSignatureError = [{e}], Cause = [{e.__cause__}]")
            raise e
        except Exception as e:
            self.__logger.error(f"Exception = [{e}], Cause = [{e.__cause__}]")
            raise e
        return token_payload

    def get_token_from_request(
            self,
            request: Request,
            token_type: JWTAuthenticationEnum.TokenType
    ) -> str:
        if token_type == JWTAuthenticationEnum.TokenType.ACCESS_TOKEN:
            header_token_name = self.__ACCESS_TOKEN_NAME
        else:
            header_token_name = self.__REFRESH_TOKEN_NAME
        token = request.headers.get(header_token_name)
        if token is None or token == "":
            raise JWTNotFoundException("Cannot Get Token From Request")
        return token.replace("Bearer ", "")

    def __get_exclude_pattern(self) -> list[str]:
        return []

    def generate_token(
            self,
            sub: str,
            token_type: JWTAuthenticationEnum.TokenType = JWTAuthenticationEnum.TokenType.ACCESS_TOKEN,
            **kwargs: dict
    ) -> str:
        exp = datetime.now(tz=timezone.utc) + timedelta(
            milliseconds=self.__ACCESS_TOKEN_VALIDITY_IN_MILLISECONDS \
                if token_type == JWTAuthenticationEnum.TokenType.ACCESS_TOKEN \
                else self.__REFRESH_TOKEN_VALIDITY_IN_MILLISECONDS
        )
        return self.__encode_token(
            payload={
                "sub": sub,
                "exp": exp,
                "type": token_type.value,
                **kwargs
            }
        )

    def issue_token(
            self,
            response: Response,
            token: str,
            token_type: JWTAuthenticationEnum.TokenType = JWTAuthenticationEnum.TokenType.ACCESS_TOKEN
    ) -> str:
        if token_type == JWTAuthenticationEnum.TokenType.ACCESS_TOKEN:
            token_name = self.__ACCESS_TOKEN_NAME
        else:
            token_name = self.__REFRESH_TOKEN_NAME
        if self.__ENCRYPT_USE is True and self.__ENCRYPT_KEY is not None:
            token = self.__encrypt_token(token)
        response.headers.append(token_name, token)
        return token

    def __encode_token(self, payload: dict) -> str:
        return jwt.encode(payload=payload, key=self.__SECRET_KEY, algorithm=self.__JWT_ALGORITHMS)

    def __decode_token(self, token: str, options: dict) -> dict:
        return jwt.decode(jwt=token, key=self.__SECRET_KEY, algorithms=self.__JWT_ALGORITHMS, options=options)

    def __encrypt_token(self, token: str) -> str:
        return CipherTool.aes_encrypt_str(self.__ENCRYPT_KEY, token)

    def __decrypt_token(self, token: str) -> str:
        return CipherTool.aes_decrypt_str(self.__ENCRYPT_KEY, token)
