from sqlalchemy import Column, Integer, TIMESTAMP, String, UniqueConstraint

from app.base.base_code_enum import BaseCodeEnum
from app.config.database_config.database_config_repository import Base


class MemberEntity(Base):
    __tablename__ = 'member'
    seq = Column(Integer, primary_key=True)
    member_id = Column(String(100), nullable=False, index=True)
    member_password = Column(String(100), nullable=False)
    member_first_name = Column(String(100), nullable=False, index=True)
    member_last_name = Column(String(100), nullable=False, index=True)
    member_email = Column(String(100), nullable=False, index=True)
    member_phone = Column(String(100), nullable=False, index=True)
    member_type_cd = Column(String(10), nullable=False, index=True)
    member_status_cd = Column(String(10), nullable=False, index=True)
    reg_dt = Column(TIMESTAMP(timezone=True))
    reg_member_seq = Column(Integer, nullable=False)
    mod_dt = Column(TIMESTAMP(timezone=True))
    mod_member_seq = Column(Integer, nullable=False)
    last_login_dt = Column(TIMESTAMP(timezone=True))
    __table_args__ = (
        UniqueConstraint('member_id', 'member_type_cd', name='ux_member_member_id_member_type_cd'),
    )


class MbrMemberEnums:
    class MemberType(BaseCodeEnum):
        ADMIN = ("admin", "MBT111", "관리자")
        USER = ("user", "MBT211", "유저")

        def __init__(self, title: str, code: str, description: str):
            self.title = title
            self.code = code
            self.description = description

    class MemberStatus(BaseCodeEnum):
        NORMAL = ("normal", "MBS111", "정상회원")
        DORMANT = ("dormant", "MBS211", "휴면회원")
        WITHDRAWAL = ("withdrawal", "MBS221", "탈퇴회원")

        def __init__(self, title: str, code: str, description: str):
            self.title = title
            self.code = code
            self.description = description
