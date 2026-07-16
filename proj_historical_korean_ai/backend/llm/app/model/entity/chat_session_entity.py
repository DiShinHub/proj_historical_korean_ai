from sqlalchemy import Column, Integer, TIMESTAMP, String

from app.config.database_config.database_config_repository import Base
from app.base.base_code_enum import BaseCodeEnum


class ChatSessionEntity(Base):
    __tablename__ = "chat_session"
    seq = Column(Integer, primary_key=True)
    member_seq = Column(Integer, nullable=False, index=True)
    title = Column(String(300))
    status = Column(String(20), nullable=False, default="ACTIVE")
    reg_dt = Column(TIMESTAMP(timezone=True))
    mod_dt = Column(TIMESTAMP(timezone=True))
    activate_dt = Column(TIMESTAMP(timezone=True))
    use_yn = Column(String(1), nullable=False, default="Y")
