from sqlalchemy import Column, Integer, TIMESTAMP, String, Text

from app.config.database_config.database_config_repository import Base
from app.base.base_code_enum import BaseCodeEnum

class ChatMessageEntity(Base):
    __tablename__ = "chat_message"
    seq = Column(Integer, primary_key=True)
    chat_session_seq = Column(Integer, nullable=False, index=True)
    model_name = Column(String(100))
    role = Column(String(20), nullable=False, index=True)
    content = Column(Text)
    response_time_ms = Column(Integer)
    feedback_type = Column(String(20))
    feedback_comment = Column(Text)
    feedback_dt = Column(TIMESTAMP(timezone=True))
    reg_dt = Column(TIMESTAMP(timezone=True))
    mod_dt = Column(TIMESTAMP(timezone=True))
