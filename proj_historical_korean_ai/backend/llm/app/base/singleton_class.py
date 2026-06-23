from abc import ABCMeta


class SingletonClass(metaclass=ABCMeta):
    """
    해당 클래스를 상속시킴으로써 singleton을 구현할 수 있다.
    상속 받는 클래스는 _SingletonClass__constructor 메소드를 구현하여 __init__ 메소드를 대체한다.
    :param _is_singleton
        싱글톤 여부를 지정할 수 있다.
        최초 인스턴스 생성 당시 전달된 값은 변경되지 않는다.
    """
    def __new__(cls, *args, **kwargs):
        _is_singleton: bool = kwargs.get("_is_singleton", True)
        if hasattr(cls, "_is_singleton"):
            _is_singleton = cls._is_singleton
        else:
            cls._is_singleton = _is_singleton
        if not hasattr(cls, "_instance") or _is_singleton is False:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, *args, **kwargs):
        if "_is_singleton" in kwargs:
            del kwargs["_is_singleton"]
        cls = type(self)
        if not hasattr(cls, "_init") or cls._is_singleton is False:
            cls._init = True
            self.__constructor(*args, **kwargs)

    def __constructor(self, *args, **kwargs):
        pass
