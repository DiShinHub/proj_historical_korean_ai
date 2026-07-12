import os
from pathlib import Path
from typing import Any

from task_worker.base.singleton_meta import SingletonMeta
from task_worker.enums.app_enum import AppEnum
from task_worker.tool.log_tool import LogTool
from task_worker.tool.properties_tool import PropertiesTool


class WebSocketConfigRunner(metaclass=SingletonMeta):
    __logger = LogTool.get_logger(__qualname__)

    __web_socket_properties_location: Path
    __web_socket_properties_local_location: Path

    def __init__(
            self,
            web_socket_properties_location: os.PathLike = Path("properties/web_socket_properties.yaml"),
            web_socket_properties_local_location: os.PathLike = Path("properties/web_socket_properties.yaml.local")
    ):
        self.__logger.info("Initialize Socket Config Runner")
        self.__web_socket_properties_location: Path = Path(web_socket_properties_location)
        self.__web_socket_properties_local_location: Path = Path(web_socket_properties_local_location)

    def get_properties(
            self,
            env_str: str = AppEnum.ActiveEnv(
                os.environ.get("APP_ACTIVE_ENV", AppEnum.ActiveEnv.LOCAL.value)
                if os.environ.get("APP_ACTIVE_ENV", AppEnum.ActiveEnv.LOCAL.value) != ""
                else AppEnum.ActiveEnv.LOCAL.value
            ).__str__()
    ):

        properties = PropertiesTool.get_properties_from_yaml_file(
            yaml_file_path=self.__web_socket_properties_location.__str__())
        properties_local = PropertiesTool.get_properties_from_yaml_file(
            yaml_file_path=self.__web_socket_properties_local_location.__str__())

        if properties is None:
            raise Exception("Database Socket Loading Failed. Cancel Run.")

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

        host: str = get_property("websocket.host")
        port: str = get_property("websocket.port")

        return dict(
            host=host,
            port=port,
        )
