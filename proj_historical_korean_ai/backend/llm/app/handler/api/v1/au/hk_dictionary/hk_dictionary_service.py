import datetime
from typing import Dict, Any

from fastapi import Depends, Body

from app.dao.hk_dictionary_dao import HkDictionaryDao
from app.config.database_config.database_config_repository import get_scoped_session
from app.model.entity.hk_dictionary_entity import HKDictionaryEntity

from app.config.authentication_config.jwt_authentication_provider import UserDetailsDto
from app.repository.context_repository import context_repository

from app.model.vo.result_vo import ResultVo
from app.exception.devlab_exception import DevlabException
from app.exception.internal_server_exception import InternalServerException
from app.decoration.transactional import Transactional

from app.config.redis_config.redis_config_repository import redis_config_repository

from app.tool.log_tool import LogTool

import datetime
import math
from typing import Dict, Any
import uuid
import json



class HkDictionaryService:

    __logger = LogTool.get_logger(__qualname__)

    def __init__(self):
        self.__hk_dictionary_dao = HkDictionaryDao(get_scoped_session=get_scoped_session)
        self.get_redis_connection = redis_config_repository.get_redis_connection

    @Transactional()
    async def post_hk_dictionary(
        self,
        request_dto: Dict[str, Any],
        user_details: UserDetailsDto = Depends(context_repository.get_user_details)
    ) -> ResultVo:

        modern_korean = request_dto.get("modern_korean")
        historical_korean = request_dto.get("historical_korean")
        historical_period_start_dt = request_dto.get("historical_period_start_dt")
        historical_period_end_dt = request_dto.get("historical_period_end_dt")

        if not modern_korean or not historical_korean:
            raise DevlabException("현대어와 고어는 필수 항목입니다.")

        start_dt = (
            datetime.datetime.fromisoformat(historical_period_start_dt)
            if historical_period_start_dt else None
        )
        end_dt = (
            datetime.datetime.fromisoformat(historical_period_end_dt)
            if historical_period_end_dt else None
        )

        try:
            query_add = await self.__hk_dictionary_dao.add_hk_dictionary(
                HKDictionaryEntity(
                    modern_korean=modern_korean,
                    historical_korean=historical_korean,
                    historical_period_start_dt=start_dt,
                    historical_period_end_dt=end_dt,
                    reg_member_seq=user_details.seq,
                    mod_member_seq=user_details.seq,
                    confirmed_yn="Y"
                )
            )

        except Exception as e:
            self.__logger.error(f"error : {str(e)}")
            raise InternalServerException("사전 항목 등록 실패")

        if len(query_add) != 1:
            raise DevlabException("사전 항목 생성 실패")

        return ResultVo(
            success=True,
            data={"seq": query_add[0].seq}
        )

    @Transactional()
    async def get_hk_dictionary(
        self,
        seq: int
    ) -> ResultVo:

        dictionary_item = await self.__hk_dictionary_dao.get_hk_dictionary(seq)
        if not dictionary_item:
            raise DevlabException("사전 항목 없음")

        return ResultVo(
            success=True,
            data={
                "seq": dictionary_item.seq,
                "modern_korean": dictionary_item.modern_korean,
                "historical_korean": dictionary_item.historical_korean,
                "historical_period_start_dt": dictionary_item.historical_period_start_dt,
                "historical_period_end_dt": dictionary_item.historical_period_end_dt,
                "reg_dt": dictionary_item.reg_dt,
                "reg_member_seq": dictionary_item.reg_member_seq,
                "mod_dt": dictionary_item.mod_dt,
                "mod_member_seq": dictionary_item.mod_member_seq,
            }
        )

    @Transactional()
    async def get_hk_dictionary_list(
        self,
        modern_korean: str | None = None,
        historical_period_start_dt: str | None = None,
        historical_period_end_dt: str | None = None,
        order_by: str = "seq",
        order_direction: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> ResultVo:

        start_dt = (
            datetime.datetime.fromisoformat(historical_period_start_dt)
            if historical_period_start_dt else None
        )
        end_dt = (
            datetime.datetime.fromisoformat(historical_period_end_dt)
            if historical_period_end_dt else None
        )

        try:
            total_cnt = await self.__hk_dictionary_dao.get_hk_dictionary_count(
                modern_korean=modern_korean,
                start_dt=start_dt,
                end_dt=end_dt
            )

            data_list = await self.__hk_dictionary_dao.get_hk_dictionary_list(
                modern_korean=modern_korean,
                start_dt=start_dt,
                end_dt=end_dt,
                order_by=order_by,
                order_direction=order_direction,
                page=page,
                page_size=page_size
            )
        except Exception as e:
            self.__logger.error(f"error : {str(e)}")
            raise InternalServerException("사전 목록 조회 실패")

        return ResultVo(
            success=True,
            data={
                "total_cnt": total_cnt,
                "page": page,
                "page_size": page_size,
                "data_list": [
                    {
                        "seq": item.seq,
                        "modern_korean": item.modern_korean,
                        "historical_korean": item.historical_korean,
                        "historical_period_start_dt": item.historical_period_start_dt,
                        "historical_period_end_dt": item.historical_period_end_dt,
                        "reg_dt": item.reg_dt,
                    }
                    for item in data_list
                ]
            }
        )

    @Transactional()
    async def put_hk_dictionary(
        self,
        seq: int,
        request_dto: Dict[str, Any] = Body(...),
        user_details: UserDetailsDto = Depends(context_repository.get_user_details)
    ) -> ResultVo:

        dictionary_item = await self.__hk_dictionary_dao.get_hk_dictionary(seq)
        if not dictionary_item:
            raise DevlabException("사전 항목 없음")

        # 수정 가능한 필드 백리스트 필터링
        allowed_keys = {
            "modern_korean",
            "historical_korean",
            "historical_period_start_dt",
            "historical_period_end_dt",
            "confirmed_yn"
        }
        update_data = {
            k: v for k, v in request_dto.items()
            if k in allowed_keys and v is not None
        }

        # 날짜 타입 변환
        if "historical_period_start_dt" in update_data:
            update_data["historical_period_start_dt"] = datetime.datetime.fromisoformat(
                update_data["historical_period_start_dt"]
            )

        if "historical_period_end_dt" in update_data:
            update_data["historical_period_end_dt"] = datetime.datetime.fromisoformat(
                update_data["historical_period_end_dt"]
            )

        update_data["mod_member_seq"] = user_details.seq

        try:
            await self.__hk_dictionary_dao.update_hk_dictionary(
                seq=seq,
                **update_data
            )
            
        except Exception as e:
            self.__logger.error(f"error : {str(e)}")
            raise InternalServerException("수정 실패")

        return ResultVo(success=True, data={})

    @Transactional()
    async def delete_hk_dictionary(
        self,
        seq: int,
        user_details: UserDetailsDto = Depends(context_repository.get_user_details)
    ) -> ResultVo:

        dictionary_item = await self.__hk_dictionary_dao.get_hk_dictionary(seq)
        if not dictionary_item:
            raise DevlabException("사전 항목 없음")

        try:
            await self.__hk_dictionary_dao.delete_hk_dictionary(
                seq=seq,
                mod_member_seq=user_details.seq
            )
        except Exception as e:
            self.__logger.error(f"error : {str(e)}")
            raise InternalServerException("삭제 실패")

        return ResultVo(success=True, data={})

    @Transactional()
    async def dump_raw_hk_dictionary(
        self,
        request_dto: Dict[str, Any],
        user_details: UserDetailsDto = Depends(context_repository.get_user_details)
    ) -> ResultVo:

        raw_text = request_dto.get("raw_text")
        if not raw_text:
            raise DevlabException("raw_text는 필수 항목입니다.")

        # task_worker에게 데이터 전송
        service_cd = "TSK_002"
        task_id = str(uuid.uuid4())
        input_message = f"<!rule^.^member_seq={user_details.seq}!>{raw_text}"
        task = {
            "task_id": task_id,
            "task_status": "wait",
            "retry_cnt" : 0,
            "params": {
                "input_message" : input_message,
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
        )