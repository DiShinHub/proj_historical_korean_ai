import os
from pathlib import Path
from typing import Any

from app.base.base_dto import BaseDto
from app.base.singleton_meta import SingletonMeta
from app.config.authentication_config.authentication_config_repository import authentication_config_repository
from app.config.authentication_config.jwt_authentication_provider import JWTAuthenticationProvider
from app.constant.app_properties import app_properties
from app.tool.log_tool import LogTool
from app.tool.properties_tool import PropertiesTool


class AuthenticationConfigProperties(BaseDto):
    secret_key: str
    encrypt_use: bool
    encrypt_key: str
    access_token_name: str
    refresh_token_name: str
    access_token_validity_in_milliseconds: int
    refresh_token_validity_in_milliseconds: int
    jwt_algorithms: str


class AuthenticationConfigRunner(metaclass=SingletonMeta):
    __logger = LogTool.get_logger(__qualname__)

    __authentication_properties_location: Path
    __authentication_properties_local_location: Path

    def __init__(
            self,
            authentication_properties_location: os.PathLike = Path("properties/authentication_properties.yaml"),
            authentication_properties_local_location: os.PathLike = Path(
                "properties/authentication_properties.yaml.local")
    ):
        self.__logger.info("Initialize Authentication Config Runner")
        self.__authentication_properties_location = Path(authentication_properties_location)
        self.__authentication_properties_local_location = Path(authentication_properties_local_location)

    def run(self):
        self.__logger.debug("Run Authentication Config Start")

        properties: AuthenticationConfigProperties = self.get_properties()
        self.inject_to_repository(properties)

        self.__logger.debug("Run Authentication Config Complete")

    def get_properties(
            self,
            env_str: str = app_properties.ACTIVE_ENV.value
    ) -> AuthenticationConfigProperties:
        properties = PropertiesTool.get_properties_from_yaml_file(
            yaml_file_path=self.__authentication_properties_location.__str__())
        properties_local = PropertiesTool.get_properties_from_yaml_file(
            yaml_file_path=self.__authentication_properties_local_location.__str__())

        if properties is None:
            raise Exception("Authentication Properties Loading Failed. Cancel Run.")

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

        properties_dict: dict = dict()

        properties_dict["secret_key"] = get_property("secret.key")
        properties_dict["encrypt_use"] = get_property("encrypt.use", False)
        properties_dict["encrypt_key"] = get_property("encrypt.key", "THISISSECRETKEYFORDEVLAB-PROJECT")
        properties_dict["access_token_name"] = get_property("access_token.name", "Authorization")
        properties_dict["refresh_token_name"] = get_property("refresh_token.name", "Authorization-Refresh")
        properties_dict["access_token_validity_in_milliseconds"] = \
            get_property("access_token.validity_in_milliseconds", 1000 * 60 * 30)
        properties_dict["refresh_token_validity_in_milliseconds"] = \
            get_property("refresh_token.validity_in_milliseconds", 1000 * 60 * 60)
        properties_dict["jwt_algorithms"] = get_property("jwt.algorithms", "HS512")

        return AuthenticationConfigProperties.model_validate(properties_dict)

    def inject_to_repository(self, properties: AuthenticationConfigProperties):
        authentication_config_repository.set_provider_instance(
            JWTAuthenticationProvider(
                secret_key=properties.secret_key,
                encrypt_use=properties.encrypt_use,
                encrypt_key=properties.encrypt_key,
                access_token_name=properties.access_token_name,
                refresh_token_name=properties.refresh_token_name,
                access_token_validity_in_milliseconds=properties.access_token_validity_in_milliseconds,
                refresh_token_validity_in_milliseconds=properties.refresh_token_validity_in_milliseconds,
                jwt_algorithms=properties.jwt_algorithms
            )
        )
