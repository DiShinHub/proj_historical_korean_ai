import datetime
import time

import bcrypt
from starlette.requests import Request
from starlette.responses import Response

from app.config.authentication_config.authentication_config_repository import AuthenticationConfigRepository
from app.config.authentication_config.jwt_authentication_provider import JWTAuthenticationEnum, AuthenticationException
from app.dao.member_auth_jwt_dao import MbrMemberAuthJwtDao
from app.dao.member_dao import MbrMemberDao
from app.decoration.transactional import Transactional
from app.exception.devlab_exception import DevlabException
from app.handler.api.v1.na.auth.dto.req_post_login_dto import ReqPostLoginDto
from app.model.entity.member_auth_jwt_entity import MemberAuthJwtEntity
from app.model.entity.member_entity import MbrMemberEnums, MemberEntity
from app.model.vo.result_vo import ResultVo
from app.tool.log_tool import LogTool


class AuthService:
    __logger = LogTool.get_logger(__qualname__)

    __authentication_config_repository: AuthenticationConfigRepository
    __member_dao: MbrMemberDao
    __member_auth_jwt_dao: MbrMemberAuthJwtDao

    def __init__(
            self,
            authentication_config_repository: AuthenticationConfigRepository,
            member_dao: MbrMemberDao,
            member_auth_jwt_dao: MbrMemberAuthJwtDao
    ):
        self.__authentication_config_repository = authentication_config_repository
        self.__member_dao = member_dao
        self.__member_auth_jwt_dao = member_auth_jwt_dao

    @Transactional()
    async def post_login(self, request_dto: ReqPostLoginDto, response: Response) -> ResultVo:
        if request_dto is None:
            return ResultVo(success=False)
        query_get_member_for_login: MemberEntity = await self.__member_dao.get_member_for_login(
            member_id=request_dto.member_id
        )
        if query_get_member_for_login is None:
            raise DevlabException("회원을 찾을 수 없습니다.")
        if bcrypt.checkpw(
                request_dto.member_password.encode("utf-8"),
                query_get_member_for_login.member_password.encode("utf-8")
        ) is False:
            raise AuthenticationException()
        if query_get_member_for_login.member_status_cd != MbrMemberEnums.MemberStatus.NORMAL.code:
            raise DevlabException("로그인 할 수 없습니다.\n고객센터에 문의하세요.")
        issued_access_token = self.__authentication_config_repository.issue_token(
            response=response,
            token=self.__authentication_config_repository.generate_token(
                sub=query_get_member_for_login.member_id,
                seq=query_get_member_for_login.seq,
                member_type_cd=query_get_member_for_login.member_type_cd
            )
        )
        issued_refresh_token = self.__authentication_config_repository.issue_token(
            response=response,
            token=self.__authentication_config_repository.generate_token(
                sub=query_get_member_for_login.member_id,
                token_type=JWTAuthenticationEnum.TokenType.REFRESH_TOKEN,
                seq=query_get_member_for_login.seq,
                member_type_cd=query_get_member_for_login.member_type_cd
            ),
            token_type=JWTAuthenticationEnum.TokenType.REFRESH_TOKEN
        )
        refresh_token_payload = self.__authentication_config_repository.resolve_token_payload(
            token=issued_refresh_token,
        )
        param_add_member_auth_jwt = MemberAuthJwtEntity(
            member_seq=query_get_member_for_login.seq,
            member_id=query_get_member_for_login.member_id,
            access_token=issued_access_token,
            refresh_token=issued_refresh_token,
            expiration_dt=datetime.datetime.fromtimestamp(refresh_token_payload.get("exp")),
            reg_member_seq=query_get_member_for_login.seq
        )
        query_add_member_auth_jwt = await self.__member_dao.add_member_auth_jwt(param_add_member_auth_jwt)
        if len(query_add_member_auth_jwt) != 1:
            raise DevlabException("로그인 할 수 없습니다.")
        return ResultVo(success=True)

    @Transactional()
    async def post_refresh(self, request: Request, response: Response) -> ResultVo:
        try:
            access_token = self.__authentication_config_repository.get_token_from_request(
                request=request
            )
            access_token_payload = self.__authentication_config_repository.resolve_token_payload(
                token=access_token,
                options={"verify_exp": False}
            )
        except Exception as e:
            self.__logger.error(f"AuthenticationException = [{e}], Class = [{e.__class__}], Cause = [{e.__cause__}]")
            raise AuthenticationException()
        if access_token_payload.get("exp") >= time.time():
            raise AuthenticationException()
        if JWTAuthenticationEnum.TokenType.ACCESS_TOKEN.value != access_token_payload.get("type"):
            raise AuthenticationException()
        try:
            refresh_token = self.__authentication_config_repository.get_token_from_request(
                request=request,
                token_type=JWTAuthenticationEnum.TokenType.REFRESH_TOKEN
            )
            refresh_token_payload = self.__authentication_config_repository.resolve_token_payload(
                token=refresh_token,
            )
        except Exception as e:
            self.__logger.error(f"AuthenticationException = [{e}], Class = [{e.__class__}], Cause = [{e.__cause__}]")
            raise AuthenticationException()
        if JWTAuthenticationEnum.TokenType.REFRESH_TOKEN.value != refresh_token_payload.get("type"):
            raise AuthenticationException()
        if access_token_payload.get("sub") != refresh_token_payload.get("sub"):
            raise AuthenticationException()
        if access_token_payload.get("seq") != refresh_token_payload.get("seq"):
            raise AuthenticationException()
        if access_token_payload.get("member_type_cd") != refresh_token_payload.get("member_type_cd"):
            raise AuthenticationException()
        query_get_member_auth_jwt = await self.__member_auth_jwt_dao.get_member_auth_jwt(
            member_id=refresh_token_payload.get("sub"),
            seq=refresh_token_payload.get("seq")
        )
        if refresh_token != query_get_member_auth_jwt.refresh_token:
            raise AuthenticationException()
        query_get_member_for_login: MemberEntity = await self.__member_dao.get_member_for_login(
            member_id=refresh_token_payload.get("sub"),
            member_type=MbrMemberEnums.MemberType.ADMIN
        )
        if query_get_member_for_login is None:
            raise DevlabException("회원을 찾을 수 없습니다.")
        if query_get_member_for_login.member_status_cd != MbrMemberEnums.MemberStatus.NORMAL.code:
            raise DevlabException("토큰을 발급할 수 없습니다.\n고객센터에 문의하세요.")

        issued_access_token = self.__authentication_config_repository.issue_token(
            response=response,
            token=self.__authentication_config_repository.generate_token(
                sub=query_get_member_for_login.member_id,
                seq=query_get_member_for_login.seq,
                member_type_cd=query_get_member_for_login.member_type_cd
            )
        )
        issued_refresh_token = self.__authentication_config_repository.issue_token(
            response=response,
            token=self.__authentication_config_repository.generate_token(
                sub=query_get_member_for_login.member_id,
                token_type=JWTAuthenticationEnum.TokenType.REFRESH_TOKEN,
                seq=query_get_member_for_login.seq,
                member_type_cd=query_get_member_for_login.member_type_cd
            ),
            token_type=JWTAuthenticationEnum.TokenType.REFRESH_TOKEN
        )
        refresh_token_payload = self.__authentication_config_repository.resolve_token_payload(
            token=issued_refresh_token,
        )
        param_add_member_auth_jwt = MemberAuthJwtEntity(
            member_seq=query_get_member_for_login.seq,
            member_id=query_get_member_for_login.member_id,
            access_token=issued_access_token,
            refresh_token=issued_refresh_token,
            expiration_dt=datetime.datetime.fromtimestamp(refresh_token_payload.get("exp")),
            reg_member_seq=query_get_member_for_login.seq
        )
        query_add_member_auth_jwt = await self.__member_dao.add_member_auth_jwt(param_add_member_auth_jwt)
        if len(query_add_member_auth_jwt) != 1:
            raise DevlabException("토큰을 발급할 수 없습니다.")
        return ResultVo(success=True)
