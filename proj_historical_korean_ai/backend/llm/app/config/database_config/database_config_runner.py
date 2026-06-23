import os
from pathlib import Path
from typing import Any

from app.base.singleton_meta import SingletonMeta
from app.config.database_config.database_config_provider import SyncDatabaseProvider, \
    AsyncDatabaseProvider
from app.config.database_config.database_config_repository import database_config_repository
from app.constant.app_properties import app_properties
from app.tool.log_tool import LogTool
from app.tool.properties_tool import PropertiesTool


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

    def run(
            self,
            is_async: bool,
            engine_echo: bool = False
    ) -> None:
        self.__logger.debug("Run Database Config Start")

        properties_dict: dict = self.get_properties()

        database_id: str = properties_dict.get("database_id")
        database_password: str = properties_dict.get("database_password")
        database_host: str = properties_dict.get("database_host")
        database_port: int = properties_dict.get("database_port")
        database_scheme: str = properties_dict.get("database_scheme")

        if (
                database_id is None
                or
                database_password is None
                or
                database_host is None
                or
                database_port is None
                or
                database_scheme is None
        ):
            raise Exception("Could Not Find Right Properties.")

        # 주입부는 추후 변경하여도 좋다.
        self.inject_to_repository(
            is_async=is_async,
            database_id=database_id,
            database_password=database_password,
            database_host=database_host,
            database_port=database_port,
            database_scheme=database_scheme,
            engine_echo=engine_echo
        )

        self.__logger.debug("Run Database Config Complete")

    def get_properties(
            self,
            env_str: str = app_properties.ACTIVE_ENV.value
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

    def inject_to_repository(
            self,
            is_async: bool,
            database_id: str,
            database_password: str,
            database_host: str,
            database_port: int,
            database_scheme: str,
            engine_echo: bool
    ):
        if is_async is False:
            database_provider = SyncDatabaseProvider
        else:
            database_provider = AsyncDatabaseProvider

        database_config_repository.set_provider_instance(
            is_async=is_async,
            provider_instance=database_provider(
                database_id=database_id,
                database_password=database_password,
                database_host=database_host,
                database_port=database_port,
                database_scheme=database_scheme,
                engine_echo=engine_echo,
            )
        )
