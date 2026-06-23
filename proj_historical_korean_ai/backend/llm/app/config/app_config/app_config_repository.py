from fastapi.applications import AppType

from app.base.singleton_meta import SingletonMeta


class AppConfigRepository(metaclass=SingletonMeta):
    __app: AppType = None

    def __init__(self):
        pass

    def set_app(self, app: AppType) -> None:
        if self.__app is not None:
            raise Exception("App Has Already Been Injected.")
        self.__app = app

    def get_app(self) -> AppType:
        if self.__app is None:
            raise Exception("No App Has Been Injected Yet.")
        return self.__app


app_config_repository = AppConfigRepository()
