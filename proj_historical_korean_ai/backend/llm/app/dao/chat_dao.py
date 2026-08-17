from sqlalchemy import select, and_, update, func
from sqlalchemy.dialects.postgresql import insert

import datetime

from app.helper.sql_session_helper import SqlSessionHelper
from app.model.entity.chat_session_entity import ChatSessionEntity
from app.model.entity.chat_message_entity import ChatMessageEntity


class ChatDao:

    __get_scoped_session = None

    def __init__(self, get_scoped_session):
        self.__get_scoped_session = get_scoped_session

    ############################################################
    # Session
    ############################################################
    async def add_chat_session(
        self,
        chat_session: ChatSessionEntity
    ) -> list[ChatSessionEntity]:

        stmt = (
            insert(ChatSessionEntity)
            .values(
                member_seq=chat_session.member_seq,
                title=chat_session.title,
                status=chat_session.status,
                reg_dt=datetime.datetime.now(),
                mod_dt=datetime.datetime.now(),
                activate_dt=datetime.datetime.now(),
                use_yn="Y"
            )
            .returning(ChatSessionEntity.seq)
        )

        result = await SqlSessionHelper.execute(
            session=self.__get_scoped_session()(),
            stmt=stmt
        )
        return result.fetchall()

    async def get_chat_session(
        self,
        chat_session_seq: int
    ) -> ChatSessionEntity | None:

        stmt = (
            select(ChatSessionEntity)
            .where(
                and_(
                    ChatSessionEntity.seq == chat_session_seq,
                    ChatSessionEntity.use_yn == "Y"
                )
            )
        )
        result = await SqlSessionHelper.execute(
            session=self.__get_scoped_session()(),
            stmt=stmt
        )
        return result.scalar_one_or_none()

    async def get_chat_session_list(
        self,
        member_seq: int,
        page: int = 1,
        page_size: int = 20,
    ) -> list[ChatSessionEntity]:

        offset = (page - 1) * page_size

        stmt = (
            select(ChatSessionEntity)
            .where(
                and_(
                    ChatSessionEntity.member_seq == member_seq,
                    ChatSessionEntity.use_yn == "Y",
                )
            )
            .order_by(
                ChatSessionEntity.activate_dt.desc(),
                ChatSessionEntity.seq.desc(),
            )
            .offset(offset)
            .limit(page_size)
        )

        result = await SqlSessionHelper.execute(
            session=self.__get_scoped_session()(),
            stmt=stmt
        )

        data_list = [
            {
                "seq": e.seq,
                "title": e.title,
                "member_seq": e.member_seq,
                "reg_dt": e.reg_dt,
            }
            for e in result.scalars().all()
        ]
        return data_list

    async def update_chat_session(
        self,
        session_seq: int,
        **kwargs
    ):
        update_values = {
            key: value
            for key, value in kwargs.items()
            if value is not None
        }

        update_values["mod_dt"] = func.now()

        stmt = (
            update(ChatSessionEntity)
            .where(ChatSessionEntity.seq == session_seq)
            .values(**update_values)
        )

        await SqlSessionHelper.execute(
            session=self.__get_scoped_session()(),
            stmt=stmt
        )
        
    async def add_chat_message(self, entity: ChatMessageEntity):
        stmt = (
            insert(ChatMessageEntity)
            .values(
                chat_session_seq=entity.chat_session_seq,
                model_name=entity.model_name,
                role=entity.role,
                content=entity.content,        # list[str] (text[])
                ipa=entity.ipa,                # list[str] (text[])
                audio_path=entity.audio_path,  # list[str] (text[])
                response_time_ms=entity.response_time_ms,
                feedback_type=entity.feedback_type,
                feedback_comment=entity.feedback_comment,
                feedback_dt=entity.feedback_dt,
                reg_dt=datetime.datetime.now(),
                mod_dt=datetime.datetime.now(),
            )
            .returning(ChatMessageEntity.seq)
        )

        result = await SqlSessionHelper.execute(
            session=self.__get_scoped_session()(),
            stmt=stmt
        )
        return result.fetchall()

    async def get_chat_message_list_by_session(
        self,
        chat_session_seq: int,
        page: int,
        page_size: int
    ):
        offset = (page - 1) * page_size

        stmt = (
            select(ChatMessageEntity)
            .where(ChatMessageEntity.chat_session_seq == chat_session_seq)
            .order_by(ChatMessageEntity.seq.asc())
            .offset(offset)
            .limit(page_size)
        )
        result = await SqlSessionHelper.execute(
            session=self.__get_scoped_session()(),
            stmt=stmt
        )
        return result.scalars().all()

    async def update_chat_message(
        self,
        chat_message_seq: int,
        **kwargs
    ):
        update_values = {
            k: v for k, v in kwargs.items()
            if v is not None
        }

        update_values["mod_dt"] = func.now()

        stmt = (
            update(ChatMessageEntity)
            .where(ChatMessageEntity.seq == chat_message_seq)
            .values(**update_values)
        )

        await SqlSessionHelper.execute(
            session=self.__get_scoped_session()(),
            stmt=stmt
        )