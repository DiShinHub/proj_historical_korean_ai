import inspect
from typing import Any


class ClassTool:

    @staticmethod
    def get_class(module_name: str, class_name: str) -> Any:
        if module_name is None or module_name == "":
            return None
        if class_name is None or class_name == "":
            return None
        module = __import__("%s" % (module_name), fromlist=[module_name])
        class_list = inspect.getmembers(module, inspect.isclass)
        if class_list is not None:
            return getattr(module, class_name)
        return None

    @staticmethod
    def get_method(clazz: Any, method_name: str) -> Any:
        if clazz is None:
            return None
        if method_name is None or method_name == "":
            return None
        method_list = inspect.getmembers(clazz, inspect.isfunction)
        if method_list is not None:
            return getattr(clazz, method_name)
        return None

    @staticmethod
    def get_class_method(module_name: str, class_name: str, method_name: str) -> Any:
        clazz = ClassTool.get_class(module_name=module_name, class_name=class_name)
        return ClassTool.get_method(clazz=clazz, method_name=method_name)

    @staticmethod
    def get_instance_method(module_name: str, class_name: str, method_name: str) -> Any:
        clazz = ClassTool.get_class(module_name=module_name, class_name=class_name)
        instance = clazz()
        return ClassTool.get_method(clazz=instance, method_name=method_name)
