from app.dao.chat_dao import ChatDao
from app.config.database_config.database_config_repository import get_scoped_session

from app.model.entity.chat_message_entity import ChatMessageEntity
from app.model.entity.chat_session_entity import ChatSessionEntity

from app.config.authentication_config.jwt_authentication_provider import UserDetailsDto
from app.repository.context_repository import context_repository

from app.model.vo.result_vo import ResultVo

from app.exception.devlab_exception import DevlabException
from app.exception.bad_request_exception import BadRequestException
from app.exception.internal_server_exception import InternalServerException

from app.decoration.transactional import Transactional

from app.config.redis_config.redis_config_repository import redis_config_repository

from app.tool.log_tool import LogTool

from fastapi import Body, Depends

import datetime
import math
from typing import Dict, Any
import uuid
import json


class ChatService:

    __logger = LogTool.get_logger(__qualname__)


    def __init__(self):
        self.__chat_dao = ChatDao(get_scoped_session=get_scoped_session)
        self.get_redis_connection = redis_config_repository.get_redis_connection
        self.check_overlab_task = redis_config_repository.check_overlab_task

    @Transactional()
    async def post_chat_session(
        self,
        request_dto,
        user_details: UserDetailsDto = Depends(context_repository.get_user_details)
    ) -> ResultVo:
        
        # request parsing 
        title = request_dto.get("title")
        if not title:
            raise DevlabException("title은 필수입니다.")

        try:
            query_add = await self.__chat_dao.add_chat_session(
                ChatSessionEntity(
                    member_seq=user_details.seq,
                    title=title,
                    status="active",
                    use_yn="Y"
                )
            )

        except Exception as e:
            self.__logger.error(f"error : {str(e)}")
            raise InternalServerException("채팅 생성 실패")

        if len(query_add) != 1:
            raise DevlabException("채팅 세션 생성 실패")

        return ResultVo(
            success=True,
            data={
                "chat_session_seq": query_add[0].seq
            }
        )

    @Transactional()
    async def get_my_chat_session_list(
        self,
        user_details: UserDetailsDto = Depends(context_repository.get_user_details),
        page: int = 1,
        page_size: int = 20,
    ) -> ResultVo:

        try:
            data_list = await self.__chat_dao.get_chat_session_list(
                member_seq=user_details.seq,
                page=page,
                page_size=page_size
            )

        except Exception as e:
            self.__logger.error(f"error : {str(e)}")
            raise InternalServerException("채팅 조회 실패")

        return ResultVo(
            success=True,
            data={
                "data_list": data_list
            }
        )
    
    @Transactional()
    async def put_chat_session(
        self,
        chat_session_seq: int,
        request_dto: Dict[str, Any] = Body(...)
    ) -> ResultVo:
        
        session = await self.__chat_dao.get_chat_session(chat_session_seq)
        if not session:
            raise DevlabException("세션 없음")
            
        try:
            # 수정 가능한 컬럼만 추출
            update_data = {
                k: v
                for k, v in request_dto.items()
                if k in {"title", "status", "activate_dt"} and v is not None
            }
            if "activate_dt" in update_data:
                update_data["activate_dt"] = datetime.datetime.fromisoformat(
                    update_data["activate_dt"]
                )

            await self.__chat_dao.update_chat_session(
                session_seq=chat_session_seq,
                **update_data
            )

        except Exception as e:
            self.__logger.error(f"error : {str(e)}")
            raise InternalServerException("수정 실패")

        return ResultVo(
            success=True,
            data={}
        )
    
    @Transactional()
    async def delete_chat_session(
        self,
        chat_session_seq: int,
    ) -> ResultVo:

        session = await self.__chat_dao.get_chat_session(chat_session_seq)
        if not session:
            raise DevlabException("세션 없음")
            
        try:
            await self.__chat_dao.update_chat_session(
                session_seq=chat_session_seq,
                use_yn="N"
            )

        except Exception as e:
            self.__logger.error(f"error : {str(e)}")
            raise InternalServerException("삭제 실패")

        return ResultVo(
            success=True,
            data={}
        )
        
    @Transactional()
    async def post_chat_message(
        self,
        request_dto: Dict[str, Any],
        user_details: UserDetailsDto
    ) -> ResultVo:

        chat_session_seq = request_dto.get("chat_session_seq")
        content = request_dto.get("content")
        role = "USER"

        if not chat_session_seq or not content:
            raise DevlabException("필수값 누락")

        session = await self.__chat_dao.get_chat_session(chat_session_seq)
        if not session:
            raise DevlabException("세션 없음")

        if session.member_seq != user_details.seq:
            raise BadRequestException("권한 없음")

        try:
            result = await self.__chat_dao.add_chat_message(
                ChatMessageEntity(
                    chat_session_seq=chat_session_seq,
                    role=role,
                    content=content,
                    reg_dt=datetime.datetime.now(),
                    mod_dt=datetime.datetime.now()
                )
            )

        except Exception as e:
            raise InternalServerException("메시지 생성 실패")

        # task_worker에게 데이터 전송
        service_cd = "TSK_001"
        task_id = str(uuid.uuid4())
        input_message = f"<!rule^.^member_seq={user_details.seq}!>{content}"
        task = {
            "task_id": task_id,
            "task_status": "wait",
            "retry_cnt" : 0,
            "params": {
                "input_message" : input_message,
                "room_name" : str(chat_session_seq),
                "chat_session_seq" : chat_session_seq
            },
        }
        task = json.dumps(task)
        
        try : 
            self.get_redis_connection().lpush(service_cd, task)

        except Exception as e :
            self.__logger.error(f"ChatService.post_chat_message error, service_cd : {service_cd}, task : {task}, error : {str(e)}")
            raise InternalServerException("관리자에게 문의하세요.")

        return ResultVo(
            success=True,
            data={"chat_message_seq": result[0][0] if result else None}
        )

    @Transactional()
    async def get_chat_message_list_by_session(
        self,
        chat_session_seq: int,
        page: int,
        page_size: int
    ) -> ResultVo:

        session = await self.__chat_dao.get_chat_session(chat_session_seq)
        if not session:
            raise DevlabException("세션 없음")

        try:
            data = await self.__chat_dao.get_chat_message_list_by_session(
                chat_session_seq=chat_session_seq,
                page=page,
                page_size=page_size
            )
        except Exception:
            raise InternalServerException("조회 실패")

        return ResultVo(
            success=True,
            data={
                "data_list": [
                    {
                        "seq": m.seq,
                        "role": m.role,
                        "content": m.content,
                        "reg_dt": m.reg_dt
                    }
                    for m in data
                ]
            }
        )

    @Transactional()
    async def put_chat_message(
        self,
        chat_message_seq: int,
        request_dto: Dict[str, Any]
    ) -> ResultVo:
        
        content = request_dto.get("content")
        feedback_type = request_dto.get("feedback_type")
        feedback_comment = request_dto.get("feedback_comment")
        
        feedback_dt = None
        if feedback_type or feedback_comment:
            feedback_dt=datetime.datetime.now()

        try:
            await self.__chat_dao.update_chat_message(
                chat_message_seq=chat_message_seq,
                content=content,
                feedback_type=feedback_type,
                feedback_comment=feedback_comment,
                feedback_dt=feedback_dt
            )

        except Exception:
            raise InternalServerException("수정 실패")

        return ResultVo(success=True, data={})

    # @Transactional()
    # async def delete_chat_message(
    #     self,
    #     chat_message_seq: int,
    #     user_details: UserDetailsDto
    # ) -> ResultVo:

    #     try:
    #         await self.__chat_dao.update_chat_message(
    #             chat_message_seq=chat_message_seq,
    #             use_yn="N"
    #         )

    #     except Exception:
    #         raise InternalServerException("삭제 실패")

    #     return ResultVo(success=True, data={})