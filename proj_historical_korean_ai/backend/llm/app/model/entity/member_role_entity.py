from sqlalchemy import Column, Integer, TIMESTAMP, String, UniqueConstraint

from app.config.database_config.database_config_repository import Base


class MbrMemberRoleEntity(Base):
    __tablename__ = "member_role"
    member_role_seq = Column(Integer, primary_key=True)             # pk
    member_role = Column(String(20), nullable=False, index=True)    # 역할
    role_desc = Column(String(500), nullable=True)                  # 역할 디스크립션
    reg_dt = Column(TIMESTAMP(timezone=True))
    reg_member_seq = Column(Integer, nullable=False)
    mod_dt = Column(TIMESTAMP(timezone=True))
    mod_member_seq = Column(Integer, nullable=False)
    __table_args__ = (
        UniqueConstraint("member_role", name="ux_member_role_member_role"),
    )
