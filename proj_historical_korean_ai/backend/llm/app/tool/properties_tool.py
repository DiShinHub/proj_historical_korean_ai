import copy
import os
import re
from typing import Any

import yaml


class PropertiesTool:

    @staticmethod
    def get_properties_from_yaml_file(yaml_file_path: str, encoding: str = "utf-8") -> dict | None:
        if yaml_file_path is None or len(yaml_file_path) == 0:
            return None
        try:
            with open(yaml_file_path, encoding=encoding) as yaml_file:
                return yaml.load(yaml_file.read(), yaml.FullLoader)
        except Exception as e:
            return None

    @staticmethod
    def get_property_value(
            properties: dict,
            property_key: str | list,
            replace_key_to_os_env_var: bool = False,
            os_env_var_key_prefix: str = "APP_",
            replace_value_to_os_env_var: bool = False
    ):
        if properties is None:
            return None
        try:
            if type(property_key) == str:
                key_arr = property_key.split(".")
            else:
                key_arr = property_key
            if replace_key_to_os_env_var is True:
                os_env_var = PropertiesTool.get_os_env_var(key_arr, os_env_var_key_prefix)
                if os_env_var is not None and os_env_var != "":
                    return os_env_var
            property_value = properties
            for key in key_arr:
                property_value = property_value[key]
            if replace_value_to_os_env_var is True and type(property_value) == str:
                property_value = PropertiesTool.replace_value_to_os_env_var(property_value)
        except (TypeError, KeyError):
            property_value = None
        return property_value

    @staticmethod
    def get_property_values_all(properties: dict | None, property_key: str) -> list | None:
        return_list: list = []
        if properties is None:
            return return_list
        for key, value in properties.items():
            if key == property_key:
                return_list.append(value)
            if type(value) == dict:
                _value = PropertiesTool.get_property_values_all(value, property_key)
                if _value is not None:
                    return_list.extend(_value)
        return return_list

    @staticmethod
    def get_property_value_with_environment(
            property_key: str | list,
            properties: dict | None,
            properties_local: dict | None,
            env_str: str,
            key_common: str = "common",
            key_local: str = "local",
            default_value: Any = None,
            force_replace_to_local: bool = True,
            replace_key_to_os_env_var: bool = False,
            os_env_var_key_prefix: str = "APP_",
            replace_value_to_os_env_var: bool = False
    ) -> Any:
        """ 전달받은 properties 와 properties_local 에서 env 에 맞는 properties 로 병합하여 전달받은 key 에 해당하는 value 를 전달한다.

        Note:
            - 우선순위는 다음과 같다. os env, local, active_env(dev, stg, prd), common
            - properties 의 key 가 os environment variable 에 존재하는 경우 값을 대체한다. (replace_value_to_os_env_var, default: True)
            - properties 의 value 갸 os environment variable 값을 참조하고 있는 경우 값을 대체한다. (replace_value_to_os_env_var, default: True)

        :param property_key:
        :param properties:
        :param properties_local:
        :param env_str:
        :param key_common:
        :param key_local:
        :param default_value:
        :param force_replace_to_local:
        :param replace_key_to_os_env_var:
        :param os_env_var_key_prefix:
        :param replace_value_to_os_env_var:
        :return:
        """
        if (
                property_key is None
                or
                (
                        type(property_key) == str and property_key == ""
                )
                or
                (
                        type(property_key) == list and len(property_key) == 0
                )
        ):
            return None
        if properties is None:
            if default_value is not None:
                return default_value
            else:
                return None
        property_key_arr = list()
        if type(property_key) == str:
            property_key_arr.extend(property_key.split("."))
        elif type(property_key) == list:
            property_key_arr.extend(property_key)
        if replace_key_to_os_env_var:
            os_env_var = PropertiesTool.get_os_env_var(property_key_arr, os_env_var_key_prefix)
            if os_env_var is not None and os_env_var != "":
                return os_env_var
        if (
                properties_local is not None
                and
                (
                        force_replace_to_local
                        or
                        env_str == key_local
                )
        ):
            _property_key_arr = [key_local]
            _property_key_arr.extend(property_key_arr)
            property_local = PropertiesTool.get_property_value(
                properties=properties_local,
                property_key=_property_key_arr,
                replace_key_to_os_env_var=False,
                replace_value_to_os_env_var=replace_value_to_os_env_var
            )
            if property_local is not None:
                return property_local
        if env_str is not None and env_str != "" and env_str != key_local:
            _property_key_arr = [env_str]
            _property_key_arr.extend(property_key_arr)
            property_env = PropertiesTool.get_property_value(
                properties=properties,
                property_key=_property_key_arr,
                replace_key_to_os_env_var=False,
                replace_value_to_os_env_var=replace_value_to_os_env_var
            )
            if property_env is not None:
                return property_env
        _property_key_arr = [key_common]
        _property_key_arr.extend(property_key_arr)
        property_common = PropertiesTool.get_property_value(
            properties=properties,
            property_key=_property_key_arr,
            replace_key_to_os_env_var=False,
            replace_value_to_os_env_var=replace_value_to_os_env_var
        )
        if property_common is not None:
            return property_common
        return default_value

    @staticmethod
    def get_properties_for_environment(
            properties: dict,
            properties_local: dict | None,
            env_str: str,
            key_common: str = "common",
            key_local: str = "local",
            force_replace_to_local: bool = True,
            replace_key_to_os_env_var: bool = False,
            os_env_var_key_prefix: str = "APP_",
            replace_value_to_os_env_var: bool = False
    ) -> dict | None:
        """ 전달받은 properties 와 properties_local 에서 env 에 맞는 properties 로 병합하여 전달한다.

        Note:
            - 우선순위는 다음과 같다. os env, local(force_replace_to_local=True 일때), active_env(dev, stg, prd), common
            - 전달받은 properties 와 properties_local 은 변경되지 않는다.
            - properties 의 key 가 os environment variable 에 존재하는 경우 값을 대체한다. (replace_value_to_os_env_var, default: True)
            - properties 의 value 갸 os environment variable 값을 참조하고 있는 경우 값을 대체한다. (replace_value_to_os_env_var, default: True)

        :param properties:
        :param properties_local:
        :param env_str:
        :param key_common:
        :param key_local:
        :param force_replace_to_local:
        :param replace_key_to_os_env_var:
        :param os_env_var_key_prefix:
        :param replace_value_to_os_env_var:
        :return:
        """
        if properties is None:
            return None
        return_properties = dict()
        properties_common = PropertiesTool.get_property_value(properties, key_common)
        if properties_common is not None:
            return_properties = PropertiesTool.update_properties(
                target_properties=return_properties,
                update_properties=properties_common,
                replace_key_to_os_env_var=replace_key_to_os_env_var,
                os_env_var_key_prefix=os_env_var_key_prefix,
                replace_value_to_os_env_var=replace_value_to_os_env_var
            )
        if (
                env_str is not None
                and
                env_str != ""
                and
                env_str != key_local
        ):
            properties_env = PropertiesTool.get_property_value(properties, env_str)
            if properties_env is not None:
                return_properties = PropertiesTool.update_properties(
                    target_properties=return_properties,
                    update_properties=properties_env,
                    replace_key_to_os_env_var=replace_key_to_os_env_var,
                    os_env_var_key_prefix=os_env_var_key_prefix,
                    replace_value_to_os_env_var=replace_value_to_os_env_var
                )
        if (
                properties_local is not None
                and
                (
                        force_replace_to_local
                        or
                        env_str == key_local
                )
        ):
            properties_local = PropertiesTool.get_property_value(properties_local, key_local)
            if properties_local is not None:
                return_properties = PropertiesTool.update_properties(
                    target_properties=return_properties,
                    update_properties=properties_local,
                    replace_key_to_os_env_var=replace_key_to_os_env_var,
                    os_env_var_key_prefix=os_env_var_key_prefix,
                    replace_value_to_os_env_var=replace_value_to_os_env_var
                )
        return return_properties

    @staticmethod
    def update_properties(
            target_properties: dict,
            update_properties: dict,
            replace_key_to_os_env_var: bool = False,
            os_env_var_key_prefix: str = "APP_",
            replace_value_to_os_env_var: bool = False
    ) -> dict:
        """전달받은 target_properties 에 전달받은 update_properties 을 병합하여 전달한다.

        Note:
            - deepcopy: 전달받은 properties 는 변경되지 않는다.

        :param target_properties:
        :param update_properties:
        :param replace_key_to_os_env_var:
        :param os_env_var_key_prefix:
        :param replace_value_to_os_env_var:
        :return:
        """
        if target_properties is None:
            target_properties = dict()
        if update_properties is None:
            return target_properties
        return_properties = copy.deepcopy(target_properties)
        update_properties_keys = PropertiesTool.get_properties_keys_all(update_properties)
        for key in update_properties_keys:
            return_properties = PropertiesTool.update_property_value(
                properties=return_properties,
                update_key=key,
                update_value=PropertiesTool.get_property_value(
                    properties=update_properties,
                    property_key=key,
                    replace_key_to_os_env_var=replace_key_to_os_env_var,
                    os_env_var_key_prefix=os_env_var_key_prefix,
                    replace_value_to_os_env_var=replace_value_to_os_env_var
                )
            )
        return return_properties

    @staticmethod
    def update_property_value(properties: dict, update_key: str | list, update_value: Any) -> dict:
        """전달받은 properties 에서 update_key 의 값을 update_value 로 대체하여 전달한다.

        Note:
            - deepcopy: 전달받은 properties 는 변경되지 않는다.
            - 배열로 내부 프로세스를 진행한다.

        :param properties:
        :param update_key:
        :param update_value:
        :return:
        """
        if properties is None:
            properties = dict()
        if update_key is None or update_value is None:
            return properties
        return_properties = copy.deepcopy(properties)
        if type(update_key) == str:
            key_arr = update_key.split(".")
        else:
            key_arr = update_key
        _properties_arr = list()
        _properties_arr.append(return_properties)
        for index, key in enumerate(key_arr):
            _properties = _properties_arr[index]
            if key in _properties:
                if len(key_arr) == index + 1:
                    _properties[key] = update_value
                else:
                    if type(_properties[key]) == dict:
                        _properties_arr.append(_properties[key])
                    else:
                        raise Exception("Existing Values Cannot Be Substituted Into dict.")
            else:
                if len(key_arr) == index + 1:
                    _properties[key] = update_value
                else:
                    _properties[key] = {}
                    _properties_arr.append(_properties[key])
        return return_properties

    @staticmethod
    def update_property_value_recursive(properties: dict, update_key: str | list, update_value: Any) -> dict:
        """전달받은 properties 에서 update_key 의 값을 update_value 로 대체하여 전달한다.

        Note:
        - deepcopy: 전달받은 properties 는 변경되지 않는다.
        - 재귀호출로 내부 프로세스를 진행한다.

        :param properties:
        :param update_key:
        :param update_value:
        :return:
        """
        if properties is None:
            properties = dict()
        if update_key is None or update_value is None:
            return properties
        return_properties = copy.deepcopy(properties)
        if type(update_key) == str:
            key_arr = update_key.split(".")
        else:
            key_arr = copy.deepcopy(update_key)
        key = key_arr[0]
        key_arr.pop(0)
        if key in return_properties:
            if len(key_arr) == 0:
                return_properties[key] = update_value
            else:
                if type(return_properties[key]) == dict:
                    return_properties[key] = PropertiesTool.update_property_value_recursive(
                        return_properties[key],
                        key_arr,
                        update_value
                    )
                else:
                    raise Exception("Existing Values Cannot Be Substituted Into dict.")
        else:
            if len(key_arr) == 0:
                return_properties[key] = update_value
            else:
                return_properties[key] = {}
                return_properties[key] = PropertiesTool.update_property_value_recursive(
                    return_properties[key],
                    key_arr,
                    update_value
                )
        return return_properties

    @staticmethod
    def get_properties_keys_all(properties: dict, parents_keys: list = None) -> list:
        """전달받은 properties의 모든 key를 list로 전달한다.

        :param properties:
        :param parents_keys:
        :return:
        """
        if properties is None:
            return list()
        if parents_keys is None:
            parents_keys = list()
        return_list = []
        for key, value in properties.items():
            _keys = copy.deepcopy(parents_keys)
            _keys.append(key)
            if type(value) == dict:
                return_list.extend(
                    PropertiesTool.get_properties_keys_all(value, _keys)
                )
            else:
                return_list.append(_keys)
        return return_list

    @staticmethod
    def replace_key_to_os_env_key(
            property_key: str | list,
            os_env_var_key_prefix: str = "APP_"
    ) -> str:
        """전달받은 key 를 환경변수 key 형태로 변환하여 전달한다.

        :param property_key:
        :param os_env_var_key_prefix:
        :return:
        """
        if type(property_key) == str:
            return os_env_var_key_prefix + property_key.replace(".", "_").upper()
        elif type(property_key) == list:
            return os_env_var_key_prefix + ("_".join(property_key)).upper()
        else:
            return ""

    @staticmethod
    def replace_value_to_os_env_var(target_value: str) -> str:
        """전달받은 값을 환경변수로 대체 하여 전달한다.

        Note:
            - "sample-key=${SAMPLE_VALUE}"
            - "sample-key=${SAMPLE_VALUE:-default-value}"

        Examples: 환경변수에 해당하는 값이 존재하는 경우
        ::
            - environment variable
            export SAMPLE_VALUE=sample-value
            - parameter
            "sample-key=${SAMPLE_VALUE}"
            - return_value
            "sample-key=sample-value"

        Examples: 환경변수에 해당하는 값이 없으나 기본값이 존재하는 경우
        ::
            - environment variable
            export SAMPLE_VALUE=
            - target_value
            "sample-key=${SAMPLE_VALUE:-default-value}"
            - return_value
            "sample-key=default-value"

        Examples: 환경변수에 해당하는 값이 없고 기본값이 없는 경우
        ::
            - environment variable
            export SAMPLE_VALUE=
            - target_value
            "sample-key=${SAMPLE_VALUE}"
            - return_value
            "sample-key="

        Examples: 기본값 구분자가 여러개 존재하는 경우
        ::
            - environment variable
            export SAMPLE_VALUE=
            - target_value
            "sample-key=${SAMPLE_VALUE:-default-value:-default-value2}"
            - return_value
            "sample-key=default-value:-default-value2"

        :param target_value:
        :return:
        """
        pattern_prefix = "${"
        pattern_postfix = "}"
        pattern = re.compile(f"\{pattern_prefix}([\w\.:/-]+){pattern_postfix}")
        results = re.findall(pattern, target_value)
        return_value = target_value
        for result in set(results):
            result_arr = result.split(":-", 1)
            if os.environ.get(result_arr[0]) is not None:
                replace_str = os.environ.get(result_arr[0])
            elif len(result_arr) > 1:
                replace_str = result_arr[1]
            else:
                replace_str = ""
            return_value = return_value.replace(
                pattern_prefix + result + pattern_postfix,
                replace_str
            )
        return return_value

    @staticmethod
    def get_os_env_var(property_key: str | list, os_env_var_key_prefix: str = "APP_") -> str:
        environment_key = PropertiesTool.replace_key_to_os_env_key(property_key, os_env_var_key_prefix)
        return os.environ.get(environment_key)
