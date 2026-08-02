
from task_worker.tool.log_tool import LogTool
from task_worker.handlers.prompts.prompts_handler import PromptsHandler
from task_worker.handlers.hk_dictionary.hk_dictionary_handler import HKDictionaryService
from task_worker.module.redis_module import RedisModule

import json

RETRY_MAX = 3
class TaskHandler():
    __logger = LogTool.get_logger(__qualname__)

    def __init__(self):
        self.redis = RedisModule()
        self.prompts_handler = PromptsHandler()
        self.hk_dictionary_handler = HKDictionaryService()
        
    def run(self):
        self.__logger.debug(f'task handler startup complete.')
        
        while True:
            try:
                task = self.pop_task("TSK_001")
                if task:
                    self.prompts_handler.handle_prompts(task)

                task = self.pop_task("TSK_002")
                if task:
                    self.hk_dictionary_handler.handle_hk_dictionary_dump_raw(task)
                            
            except Exception as e :
                self.__logger.info(f"e : {e}")
                self.handle_exception(e)     
            
            finally:
                self.task = None
    
    def pop_task(self, service_cd):
        
        task = self.redis.rpop(service_cd)
        if task:
            task = self.redis.convert_bytes_to_dict(task)
            return task
    
    def handle_exception(self, e: Exception):
        
        # TODO 
        return 
        
        # --- 데이터 셋팅
        data = self.task.get("data")
        task_id = self.task.get("task_id")
        retry_cnt = self.task.get("retry_cnt")
        
        slack_user_id = data.get("slack_user_id")
        employee_seq = data.get("employee_seq")
        employee_email = data.get("employee_email")
        slack_text = data.get("slack_text")
        
        # --- 케이스별 애러 처리
        response_msg = None
        status_code = 0
            
        if e.__class__.__name__ == "BadRequestException":
            status_code = 400
            response_msg = f"{str(e)}"

        elif e.__class__.__name__ == "DevlabException":
            status_code = 422
            response_msg = f"관리자에게 문의하세요!"
            
        elif e.__class__.__name__ == "LlmException":
            if retry_cnt < RETRY_MAX:
                service_cd = "TSK_001"
                task = {
                    "task_id": task_id,
                    "task_status": "retry",
                    "retry_cnt" : retry_cnt + 1,
                    "data": {
                        "slack_user_id" : slack_user_id,
                        "employee_seq" : employee_seq,
                        "employee_email" : employee_email,
                        "slack_text" : slack_text,
                    }
                }
                task = json.dumps(task)
                self.redis.lpush(service_cd, task)
                response_msg = None
                self.__logger.info(f"LlmException : {e}, retry : {retry_cnt}")
            
            else: 
                status_code = 500
                response_msg = "에러가 발생했습니다. 관리자 <@U062YU97DK2> 님에게 문의해 주세요."
        
        elif e.__class__.__name__ == "InternalServerException":
            status_code = 500
            response_msg = "에러가 발생했습니다. 관리자 <@U062YU97DK2> 님에게 문의해 주세요."
        
        else:
            status_code = 500
            response_msg = "에러가 발생했습니다. 관리자 <@U062YU97DK2> 님에게 문의해 주세요."
        
        # --- 애러처리 TODO
        pass 
    
        # --- 로깅
        if status_code >= 422:
            self.__logger.info(f"에러 메시지: {e}")
            self.__logger.info(f"에러 타입: {type(e)}")
            self.__logger.info(f"에러 이름: {e.__class__.__name__}")
            
        self.task = None