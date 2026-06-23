from sqlalchemy import Column, Integer, TIMESTAMP, String, UniqueConstraint

from app.config.database_config.database_config_repository import Base


class MemberAuthJwtEntity(Base):
    __tablename__ = "member_auth_jwt"
    seq = Column(Integer, primary_key=True)
    member_seq = Column(Integer, nullable=False, index=True)
    member_id = Column(String(100), nullable=False, index=True)
    access_token = Column(String(1000), nullable=False)
    refresh_token = Column(String(1000), nullable=False)
    expiration_dt = Column(TIMESTAMP(timezone=True))
    reg_dt = Column(TIMESTAMP(timezone=True))
    reg_member_seq = Column(Integer, nullable=False)
    mod_dt = Column(TIMESTAMP(timezone=True))
    mod_member_seq = Column(Integer, nullable=False)
    __table_args__ = (
        UniqueConstraint("seq", name="ux_member_auth_jwt_member_seq"),
        UniqueConstraint("member_id", name="ux_member_auth_jwt_member_id")
    )
