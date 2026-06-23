from abc import ABCMeta
from app.tool.log_tool import LogTool
from app.exception.devlab_exception import DevlabException

import redis
import inspect
import json

class RedisProvider(metaclass=ABCMeta):
    __logger = LogTool.get_logger(__qualname__)

    def __init__(
            self,
            redis_host: str,
            redis_port: int,
            redis_db: int,
    ):
        self.__logger.info("Initialize Redis Provider")
        
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.redis_client = None
        
        self.generate_redis_connection()
        
    def generate_redis_connection(self):
        """
        redis connection 생성

        """
        
        self.__logger.debug("Create Redis connection")
        
        with redis.StrictRedis(host=self.redis_host, 
                               port=self.redis_port,
                               db=self.redis_db) as conn:
            
            self.redis_client = conn
    
    def get_redis_connection(self):
        """
        redis connection 조회

        """
        
        return self.redis_client
    
    def check_overlab_task(self, service_cd, target_task_id):
        """
        target_task_id가 중복 등록인지 확인

        Parameters
        ----------
        service_cd : 서비스 코드 (str)
        target_task_id : 대상 테스크 ID (str)
        """
        
        task_list = self.redis_client.lrange(service_cd, 0, -1)
    
        for task in task_list:
            task = json.loads(task.decode('utf-8'))
            if task.get("task_id") == target_task_id:
                if task.get("task_status") == "wait":
                    raise DevlabException("이미 등록 된 테스크입니다.")
                