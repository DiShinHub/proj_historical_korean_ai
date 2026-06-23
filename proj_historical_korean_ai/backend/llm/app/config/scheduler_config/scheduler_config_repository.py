from apscheduler.schedulers.base import BaseScheduler

from app.base.singleton_meta import SingletonMeta


class SchedulerConfigRepository(metaclass=SingletonMeta):
    __scheduler_instance: BaseScheduler = None

    def __init__(self):
        pass

    def set_scheduler_instance(self, scheduler_instance: BaseScheduler):
        if self.__scheduler_instance is not None:
            raise Exception("Scheduler Instance Has Already Been Injected.")
        else:
            self.__scheduler_instance = scheduler_instance

    def get_scheduler_instance(self) -> BaseScheduler:
        if self.__scheduler_instance is None:
            raise Exception("No Scheduler Instance Has Been Injected Yet.")
        return self.__scheduler_instance


scheduler_config_repository = SchedulerConfigRepository()
