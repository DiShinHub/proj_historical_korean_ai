

from app.base.singleton_meta import SingletonMeta
from app.config.redis_config.redis_config_provider import RedisProvider
from app.repository.context_repository import context_repository

class RedisConfigRepository(metaclass=SingletonMeta):
    __provider_instance: RedisProvider = None

    def __init__(self):
        pass

    def set_provider_instance(self, provider_instance: RedisProvider) -> None:
        if self.__provider_instance is not None:
            raise Exception("Provider Instance Has Already Been Injected.")

        self.__provider_instance = provider_instance

    def get_provider_instance(self) -> RedisProvider:
        if self.__provider_instance is None:
            raise Exception("No Provider Has Been Injected Yet.")

        return self.__provider_instance

    def get_redis_connection(self):
        if self.__provider_instance is None:
            raise Exception("No Provider Has Been Injected Yet.")
        
        return self.__provider_instance.get_redis_connection()

    def check_overlab_task(self, service_cd, target_task_id):
        if self.__provider_instance is None:
            raise Exception("No Provider Has Been Injected Yet.")
        
        return self.__provider_instance.check_overlab_task(service_cd, target_task_id)
    
redis_config_repository = RedisConfigRepository()
get_redis_connection = redis_config_repository.get_redis_connection