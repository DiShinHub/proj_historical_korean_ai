from enum import Enum


class BaseCodeEnum(Enum):
    def __new__(cls, value, *value_aliases, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = value
        for alias in value_aliases:
            cls._value2member_map_[alias] = obj
        return obj

    @classmethod
    def by_code(cls, code):
        return_item = None
        for item in cls.__iter__():
            if item.code == code:
                return_item = item
                break
        return return_item
