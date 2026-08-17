import os
from pathlib import Path
from typing import Any

from task_worker.base.singleton_meta import SingletonMeta
from task_worker.enums.app_enum import AppEnum
from task_worker.tool.log_tool import LogTool
from task_worker.tool.properties_tool import PropertiesTool


class MinioConfigRunner(metaclass=SingletonMeta):

    def __init__(
            self,
            minio_properties_location: os.PathLike = Path("properties/minio_properties.yaml"),
            minio_properties_local_location: os.PathLike = Path("properties/minio_properties.yaml.local")
    ):
        
        self.logger = LogTool.get_logger(self.__class__.__name__)
        self.logger.debug("Initialize Minio Config Runner")
        self.minio_properties_location: Path = Path(minio_properties_location)
        self.minio_properties_local_location: Path = Path(minio_properties_local_location)
     
    def get_properties(
            self,
            env_str: str = AppEnum.ActiveEnv(
                os.environ.get("APP_ACTIVE_ENV", AppEnum.ActiveEnv.LOCAL.value)
                if os.environ.get("APP_ACTIVE_ENV", AppEnum.ActiveEnv.LOCAL.value) != ""
                else AppEnum.ActiveEnv.LOCAL.value
            ).__str__()
        ):
        
        properties = PropertiesTool.get_properties_from_yaml_file(
            yaml_file_path=self.minio_properties_location.__str__())
        properties_local = PropertiesTool.get_properties_from_yaml_file(
            yaml_file_path=self.minio_properties_local_location.__str__())

        if properties is None:
            raise Exception("Minio Properties Loading Failed. Cancel Run.")

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

        minio_external_url: str = get_property("minio.minio_external_url")
        minio_service_port: str = get_property("minio.minio_service_port")
        minio_access_key: str = get_property("minio.minio_access_key")
        minio_secret_key: str = get_property("minio.minio_secret_key")
        minio_bucket: str = get_property("minio.minio_bucket")
        minio_local: str = get_property("minio.minio_local")

        return dict(
            minio_external_url=minio_external_url,
            minio_service_port=minio_service_port,
            minio_access_key=minio_access_key,
            minio_secret_key=minio_secret_key,
            minio_bucket=minio_bucket,
            minio_local=minio_local,
        )