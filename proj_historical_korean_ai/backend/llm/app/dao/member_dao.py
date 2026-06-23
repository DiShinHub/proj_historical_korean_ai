from sqlalchemy import select, and_, func, text, case
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import update

from app.helper.sql_session_helper import SqlSessionHelper
from app.model.entity.member_auth_jwt_entity import MemberAuthJwtEntity
from app.model.entity.member_entity import MemberEntity, MbrMemberEnums
from app.model.entity.member_role_entity import MbrMemberRoleEntity

import datetime


class MbrMemberDao:
    __get_scoped_session = None

    def __init__(self, get_scoped_session):
        self.__get_scoped_session = get_scoped_session

    async def add_member(self, member: MemberEntity) -> list[MemberEntity]:
        stmt = (
            insert(MemberEntity)
            .values(
                member_id=member.member_id,
                member_password=member.member_password,
                member_first_name=member.member_first_name,
                member_last_name=member.member_last_name,
                member_email=member.member_email,
                member_phone=member.member_phone,
                member_type_cd=member.member_type_cd,
                member_status_cd=member.member_status_cd,
                reg_dt=datetime.datetime.now(),
                reg_member_seq=member.reg_member_seq,
                mod_dt=datetime.datetime.now(),
                mod_member_seq=member.reg_member_seq,
            )
            .returning(MemberEntity.seq)
        )
        result = await SqlSessionHelper.execute(
            session=self.__get_scoped_session()(),
            stmt=stmt
        )
        return [MemberEntity(**(row._mapping)) for row in result.fetchall()]

    async def add_member_auth_jwt(self, member_auth_jwt: MemberAuthJwtEntity) -> list[MemberAuthJwtEntity]:
        stmt = (
            insert(MemberAuthJwtEntity)
            .values(
                member_seq=member_auth_jwt.member_seq,
                member_id=member_auth_jwt.member_id,
                access_token=member_auth_jwt.access_token,
                refresh_token=member_auth_jwt.refresh_token,
                expiration_dt=member_auth_jwt.expiration_dt,
                reg_dt=func.now(),
                reg_member_seq=member_auth_jwt.reg_member_seq,
                mod_dt=func.now(),
                mod_member_seq=member_auth_jwt.reg_member_seq
            )
            .on_conflict_do_update(
                index_elements=["member_id"],
                set_={
                    "access_token": member_auth_jwt.access_token,
                    "refresh_token": member_auth_jwt.refresh_token,
                    "expiration_dt": member_auth_jwt.expiration_dt,
                    "mod_dt": func.now(),
                    "mod_member_seq": member_auth_jwt.reg_member_seq
                }
            )
            .returning(MemberAuthJwtEntity.seq)
        )
        result = await SqlSessionHelper.execute(
            session=self.__get_scoped_session()(),
            stmt=stmt
        )
        return [MemberAuthJwtEntity(**(row._mapping)) for row in result.fetchall()]
    
    async def get_member_for_login(
            self,
            member_id: str
    ) -> MemberEntity | None:
        stmt = (
            select(
                MemberEntity.seq,
                MemberEntity.member_id,
                MemberEntity.member_password,
                MemberEntity.member_type_cd,
                MemberEntity.member_status_cd,
                MemberEntity.reg_member_seq,
            )
            .where(
                and_(
                    MemberEntity.member_id == member_id
                )
            )
        )
        result = await SqlSessionHelper.execute(
            session=self.__get_scoped_session()(),
            stmt=stmt
        )
        fetch_result = result.fetchone()
        return MemberEntity(**(fetch_result._mapping)) if fetch_result else None
    