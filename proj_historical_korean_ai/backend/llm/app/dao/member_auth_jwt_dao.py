from sqlalchemy import select, and_

from app.helper.sql_session_helper import SqlSessionHelper
from app.model.entity.member_auth_jwt_entity import MemberAuthJwtEntity
from app.model.entity.member_entity import MemberEntity


class MbrMemberAuthJwtDao:
    ___get_scoped_session = None

    def __init__(self, get_scoped_session):
        self.__get_scoped_session = get_scoped_session

    async def get_member_auth_jwt(
            self,
            seq: int,
            member_id: str,
    ) -> MemberAuthJwtEntity | None:
        stmt = (
            select(
                MemberAuthJwtEntity.seq,
                MemberAuthJwtEntity.member_seq,
                MemberAuthJwtEntity.member_id,
                MemberAuthJwtEntity.access_token,
                MemberAuthJwtEntity.refresh_token,
                MemberAuthJwtEntity.expiration_dt
            )
            .where(
                and_(
                    MemberAuthJwtEntity.seq == seq,
                    MemberAuthJwtEntity.member_id == member_id,
                )
            )
        )
        result = await SqlSessionHelper.execute(
            session=self.__get_scoped_session()(),
            stmt=stmt,
        )
        fetch_result = result.fetchone()
        return MemberAuthJwtEntity(**(fetch_result._mapping)) if fetch_result else None
