import os
from pathlib import Path
from typing import Any

from app.base.singleton_meta import SingletonMeta
from app.config.redis_config.redis_config_provider import RedisProvider
from app.config.redis_config.redis_config_repository import redis_config_repository
from app.constant.app_properties import app_properties
from app.tool.log_tool import LogTool
from app.tool.properties_tool import PropertiesTool


class RedisConfigRunner(metaclass=SingletonMeta):
    __logger = LogTool.get_logger(__qualname__)

    def __init__(
            self,
            redis_properties_location: os.PathLike = Path("properties/redis_properties.yaml"),
            redis_properties_local_location: os.PathLike = Path("properties/redis_properties.yaml.local")
    ):
        
        self.__logger = LogTool.get_logger(self.__class__.__name__)
        self.__logger.info("Initialize Redis Config Runner")
        self.redis_properties_location: Path = Path(redis_properties_location)
        self.redis_properties_local_location: Path = Path(redis_properties_local_location)
        
    def run(self):
        self.__logger.debug("Run Redis Config Start")

        properties_dict: dict = self.get_properties()

        redis_host: str = properties_dict.get("redis_host")
        redis_port: str = properties_dict.get("redis_port")
        redis_db: int = properties_dict.get("redis_db")

        if (
            redis_host is None
            or
            redis_port is None
            or
            redis_db is None
        ):
            raise Exception("Could Not Find Right Properties.")

        # 주입부
        self.inject_to_repository(
            redis_host=redis_host,
            redis_port=redis_port,
            redis_db=redis_db,
        )

        self.__logger.debug("Run Redis Config Complete")
     
    def get_properties(
            self,
            redis_properties_location: os.PathLike = Path("properties/redis_properties.yaml"),
            redis_properties_local_location: os.PathLike = Path("properties/redis_properties.yaml.local"),
            env_str: str = "local"
    ):

        redis_properties_location: Path = Path(redis_properties_location)
        redis_properties_local_location: Path = Path(redis_properties_local_location)
        
        properties = PropertiesTool.get_properties_from_yaml_file(
            yaml_file_path=redis_properties_location.__str__())
        properties_local = PropertiesTool.get_properties_from_yaml_file(
            yaml_file_path=redis_properties_local_location.__str__())

        if properties is None:
            raise Exception("Redis Properties Loading Failed. Cancel Run.")

        def get_property(property_key: str, default_value: Any = None):
            return PropertiesTool.get_property_value_with_environment(
                property_key=property_key,
                properties=properties,
                properties_local=properties_local,
                env_str=env_str,
                default_value=default_value,
                replace_key_to_os_env_var=True,
                replace_value_to_os_env_var=True
            )

        redis_host: str = get_property("redis.host")
        redis_port: int = get_property("redis.port")
        redis_db: int = get_property("redis.db")

        return dict(
            redis_host=redis_host,
            redis_port=redis_port,
            redis_db=redis_db,
        )

    def inject_to_repository(
            self,
            redis_host: str,
            redis_port: int,
            redis_db: int,
    ):
        
        redis_config_repository.set_provider_instance(
            provider_instance=RedisProvider(
                redis_host=redis_host,
                redis_port=redis_port,
                redis_db=redis_db,
            )
        )