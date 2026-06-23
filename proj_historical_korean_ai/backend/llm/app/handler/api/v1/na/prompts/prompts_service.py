import json

from app.handler.api.v1.na.prompts.dto.req_prompt_post_index import ReqPromptPostIndex
from app.exception.internal_server_exception import InternalServerException
from app.model.vo.result_vo import ResultVo
from app.tool.log_tool import LogTool

from app.config.redis_config.redis_config_repository import RedisConfigRepository

import uuid
import json
import inspect

class LlmBridgesService:
    __logger = LogTool.get_logger(__qualname__)

    def __init__(self,
            redis_config_repository: RedisConfigRepository
        ):
        self.get_redis_connection = redis_config_repository.get_redis_connection
        self.check_overlab_task = redis_config_repository.check_overlab_task
    
    async def index(
        self,
        params: ReqPromptPostIndex,
        ) -> ResultVo:
        
        # 테스크 셋팅
        service_cd = "LBS_001"
        task_id = str(uuid.uuid4())
        task = {
            "task_id": task_id,
            "task_status": "wait",
            "retry_cnt" : 0,
            "params": {
                "prompt" : params.prompt,
                "room_name" : params.room_name,
            },
        }
        task = json.dumps(task)
        
        # 큐에 적재
        try : 
            self.get_redis_connection().lpush(service_cd, task)

        except Exception as e :
            self.__logger.error(f"def : {inspect.currentframe().f_code.co_name}, params : {params}, service_cd : {service_cd}, task : {task}, error : {str(e)}")
            raise InternalServerException("관리자에게 문의하세요.")
        
        return ResultVo(
            success=True,
            message="",
            data={}
        )
