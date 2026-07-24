from sqlalchemy import Column, Integer, TIMESTAMP, String, Text

from app.config.database_config.database_config_repository import Base
from app.base.base_code_enum import BaseCodeEnum

class HKDictionaryEntity(Base):
    __tablename__ = "hk_dictionary"
    seq = Column(Integer, primary_key=True, autoincrement=True)
    modern_korean = Column(String(255), nullable=False, index=True)
    historical_korean = Column(String(255), nullable=False)
    historical_period_start_dt = Column(TIMESTAMP(timezone=True), index=True)
    historical_period_end_dt = Column(TIMESTAMP(timezone=True), index=True)
    reg_dt = Column(TIMESTAMP(timezone=True))
    reg_member_seq = Column(Integer, nullable=False)
    mod_dt = Column(TIMESTAMP(timezone=True))
    mod_member_seq = Column(Integer, nullable=False)
    delete_yn = Column(String(1), nullable=False, default="N")