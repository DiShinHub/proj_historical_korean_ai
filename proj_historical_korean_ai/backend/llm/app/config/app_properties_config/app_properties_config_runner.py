import os
from pathlib import Path
from typing import Any

from app.base.singleton_meta import SingletonMeta
from app.constant.app_properties import app_properties
from app.enums.app_enum import AppEnum
from app.tool.log_tool import LogTool
from app.tool.properties_tool import PropertiesTool


class AppPropertiesConfigRunner(metaclass=SingletonMeta):
    __logger = LogTool.get_logger(__qualname__)

    __app_properties_location: Path
    __app_properties_local_location: Path

    def __init__(
            self,
            app_properties_location: os.PathLike = Path("properties/app_properties.yaml"),
            app_properties_local_location: os.PathLike = Path("properties/app_properties.yaml.local")
    ):
        self.__logger.info("Initialize Application Properties Config Runner")
        self.__app_properties_location = Path(app_properties_location)
        self.__app_properties_local_location = Path(app_properties_local_location)

    def run(self):
        self.__logger.debug("Run Application Properties Config Start")

        app_properties.ACTIVE_ENV = AppEnum.ActiveEnv(
            os.environ.get("APP_ACTIVE_ENV", AppEnum.ActiveEnv.LOCAL.value)
            if os.environ.get("APP_ACTIVE_ENV", AppEnum.ActiveEnv.LOCAL.value) != ""
            else AppEnum.ActiveEnv.LOCAL.value
        )

        properties = PropertiesTool.get_properties_from_yaml_file(
            yaml_file_path=self.__app_properties_location.__str__())
        properties_local = PropertiesTool.get_properties_from_yaml_file(
            yaml_file_path=self.__app_properties_local_location.__str__())

        if properties is None:
            self.__logger.warning("Application Properties Loading Failed. Use Default Configurations.")
            return

        def get_property(property_key: str, default_value: Any = None):
            return PropertiesTool.get_property_value_with_environment(
                property_key=property_key,
                properties=properties,
                properties_local=properties_local,
                env_str=app_properties.ACTIVE_ENV.value,
                default_value=default_value,
                replace_key_to_os_env_var=True,
                replace_value_to_os_env_var=True
            )

        ##################################################
        # app_properties 주입 시작
        ##################################################

        # system
        app_properties.DEBUG = get_property("debug", app_properties.DEBUG)
        app_properties.APP_NAME = get_property("app.name", app_properties.APP_NAME)
        app_properties.APP_DESCRIPTION = get_property("app.description", app_properties.APP_DESCRIPTION)
        app_properties.APP_VERSION = get_property("app.version", app_properties.APP_VERSION)

        # cors
        app_properties.CORS_ALLOW_ORIGINS = get_property("cors.allow.origins", app_properties.CORS_ALLOW_ORIGINS)

        # metrics
        app_properties.METRICS_PROMETHEUS_USE = get_property("metrics.prometheus.use",
                                                             app_properties.METRICS_PROMETHEUS_USE)

        # scheduler
        app_properties.SCHEDULER_USE = get_property("scheduler.use", app_properties.SCHEDULER_USE)
        app_properties.SCHEDULER_AUTOSTART = get_property("scheduler.autostart", app_properties.SCHEDULER_AUTOSTART)

        ##################################################
        # app_properties 주입 완료
        ##################################################

        self.__logger.debug("Run Application Properties Config Complete")

    def print(self):
        self.__logger.debug(f"===== App Properties =============================")
        for key in app_properties.__fields__.keys():
            self.__logger.debug(f"= {key} = [{app_properties.__getattribute__(key)}]")
        self.__logger.debug(f"==================================================")
