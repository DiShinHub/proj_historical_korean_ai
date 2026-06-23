import os
from pathlib import Path
from typing import Any

from web_socket.base.singleton_meta import SingletonMeta
from web_socket.enums.app_enum import AppEnum
from web_socket.tool.log_tool import LogTool
from web_socket.tool.properties_tool import PropertiesTool


class RedisConfigRunner(metaclass=SingletonMeta):

    def __init__(
            self,
            redis_properties_location: os.PathLike = Path("properties/redis_properties.yaml"),
            redis_properties_local_location: os.PathLike = Path("properties/redis_properties.yaml.local")
    ):
        
        self.logger = LogTool.get_logger(self.__class__.__name__)
        self.logger.debug("Initialize Redis Config Runner")
        self.redis_properties_location: Path = Path(redis_properties_location)
        self.redis_properties_local_location: Path = Path(redis_properties_local_location)
     
    def get_properties(
            self,
            env_str: str = AppEnum.ActiveEnv(
                os.environ.get("APP_ACTIVE_ENV", AppEnum.ActiveEnv.LOCAL.value)
                if os.environ.get("APP_ACTIVE_ENV", AppEnum.ActiveEnv.LOCAL.value) != ""
                else AppEnum.ActiveEnv.LOCAL.value
            ).__str__()
        ):
        
        properties = PropertiesTool.get_properties_from_yaml_file(
            yaml_file_path=self.redis_properties_location.__str__())
        properties_local = PropertiesTool.get_properties_from_yaml_file(
            yaml_file_path=self.redis_properties_local_location.__str__())

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