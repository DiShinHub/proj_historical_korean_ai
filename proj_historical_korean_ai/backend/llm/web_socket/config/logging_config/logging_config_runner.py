import os
from logging import config
from pathlib import Path

from web_socket.base.singleton_meta import SingletonMeta
from web_socket.enums.app_enum import AppEnum
from web_socket.tool.properties_tool import PropertiesTool


class LoggingConfigRunner(metaclass=SingletonMeta):

    def __init__(
            self,
            logging_properties_location: os.PathLike = Path("properties/logging_properties.yaml"),
            logging_properties_local_location: os.PathLike = Path("properties/logging_properties.yaml.local")
    ):
        self.logging_properties_location: Path = Path(logging_properties_location)
        self.logging_properties_local_location: Path = Path(logging_properties_local_location)

    def run(self):

        properties = PropertiesTool.get_properties_from_yaml_file(
            yaml_file_path=self.logging_properties_location.__str__()
        )
        properties_local = PropertiesTool.get_properties_from_yaml_file(
            yaml_file_path=self.logging_properties_local_location.__str__()
        )

        if properties is None:
            print("Logging Properties Loading Failed. Use Default Configurations.")
            return

        active_env: str = AppEnum.ActiveEnv(
            os.environ.get("APP_ACTIVE_ENV", AppEnum.ActiveEnv.LOCAL.value)
            if os.environ.get("APP_ACTIVE_ENV", AppEnum.ActiveEnv.LOCAL.value) != ""
            else AppEnum.ActiveEnv.LOCAL.value
        ).__str__()

        properties = PropertiesTool.get_properties_for_environment(
            properties=properties,
            properties_local=properties_local,
            env_str=active_env,
            replace_value_to_os_env_var=True
        )

        filenames = PropertiesTool.get_property_values_all(
            PropertiesTool.get_property_value(properties=properties, property_key="handlers"),
            "filename"
        )
        for filename in filenames:
            filename_arr = filename.split("/")
            del filename_arr[-1]
            path = '/'.join(filename_arr)
            print(f"Logging Config Runner Need to Make Dir = [{path}] and File = [{filename}]")
            os.makedirs(path, exist_ok=True)

        config.dictConfig(properties)
