import os
from pathlib import Path
from typing import Any

from web_socket.base.singleton_meta import SingletonMeta
from web_socket.enums.app_enum import AppEnum
from web_socket.tool.log_tool import LogTool
from web_socket.tool.properties_tool import PropertiesTool


class DatabaseConfigRunner(metaclass=SingletonMeta):
    __logger = LogTool.get_logger(__qualname__)

    __database_properties_location: Path
    __database_properties_local_location: Path

    def __init__(
            self,
            database_properties_location: os.PathLike = Path("properties/database_properties.yaml"),
            database_properties_local_location: os.PathLike = Path("properties/database_properties.yaml.local")
    ):
        self.__logger.info("Initialize Database Config Runner")
        self.__database_properties_location: Path = Path(database_properties_location)
        self.__database_properties_local_location: Path = Path(database_properties_local_location)

    def get_properties(
            self,
            env_str: str = AppEnum.ActiveEnv(
                os.environ.get("APP_ACTIVE_ENV", AppEnum.ActiveEnv.LOCAL.value)
                if os.environ.get("APP_ACTIVE_ENV", AppEnum.ActiveEnv.LOCAL.value) != ""
                else AppEnum.ActiveEnv.LOCAL.value
            ).__str__()
    ):

        properties = PropertiesTool.get_properties_from_yaml_file(
            yaml_file_path=self.__database_properties_location.__str__())
        properties_local = PropertiesTool.get_properties_from_yaml_file(
            yaml_file_path=self.__database_properties_local_location.__str__())

        if properties is None:
            raise Exception("Database Properties Loading Failed. Cancel Run.")

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

        database_id: str = get_property("database.id")
        database_password: str = get_property("database.password")
        database_host: str = get_property("database.host")
        database_port: int = get_property("database.port")
        database_scheme: str = get_property("database.scheme")

        return dict(
            database_id=database_id,
            database_password=database_password,
            database_host=database_host,
            database_port=database_port,
            database_scheme=database_scheme
        )
