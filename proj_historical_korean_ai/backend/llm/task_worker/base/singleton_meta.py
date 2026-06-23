class SingletonMeta(type):
    """
    해당 클래스를 metaclass로 지정함으로써 singleton을 구현할 수 있다.
    :param _is_singleton
        싱글톤 여부를 지정할 수 있다.
        최초 인스턴스 생성 당시 전달된 값은 변경되지 않는다.
    """
    _singleton_instances = {}
    _no_singleton_classes = list()

    def __call__(cls, *args, **kwargs):
        _is_singleton: bool = kwargs.get("_is_singleton", True)
        if "_is_singleton" in kwargs:
            del kwargs["_is_singleton"]
        if cls in cls._singleton_instances:
            return cls._singleton_instances[cls]
        instance = super(SingletonMeta, cls).__call__(*args, **kwargs)
        if cls not in cls._no_singleton_classes:
            if _is_singleton is True:
                cls._singleton_instances[cls] = instance
            else:
                cls._no_singleton_classes.append(cls)
        return instance
