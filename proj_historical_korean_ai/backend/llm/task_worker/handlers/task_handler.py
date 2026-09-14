
from task_worker.tool.log_tool import LogTool
from task_worker.handlers.prompts.prompts_handler import PromptsHandler
from task_worker.handlers.hk_dictionary.hk_dictionary_handler import HKDictionaryService
from task_worker.module.redis_module import RedisModule

import time

RETRY_MAX = 3
class TaskHandler():
    __logger = LogTool.get_logger(__qualname__)

    def __init__(self):
        self.redis = RedisModule()
        self.prompts_handler = PromptsHandler()
        self.hk_dictionary_handler = HKDictionaryService()
        
    def run(self):
        
        while True:
            try:
                task = self.pop_task("TSK_001")
                if task:
                    self.prompts_handler.handle_prompts(task)

                task = self.pop_task("TSK_002")
                if task:
                    self.hk_dictionary_handler.handle_hk_dictionary_dump_raw(task)

                time.sleep(0.1)
                            
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