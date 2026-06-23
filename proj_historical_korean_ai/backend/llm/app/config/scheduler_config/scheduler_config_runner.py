from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.base import BaseScheduler

from app.base.singleton_meta import SingletonMeta
from app.config.scheduler_config.scheduler_config_repository import scheduler_config_repository
from app.tool.log_tool import LogTool


class SchedulerConfigRunner(metaclass=SingletonMeta):
    __logger = LogTool.get_logger(__qualname__)

    def __init__(self):
        self.__logger.info("Initialize Scheduler Config Runner")

    def run(self, *args, **kwargs) -> BaseScheduler:
        self.__logger.debug("Run Scheduler Config Start")
        scheduler_instance = AsyncIOScheduler(*args, **kwargs)
        self.inject_to_repository(scheduler_instance)
        return scheduler_instance

    def inject_to_repository(self, scheduler_instance) -> None:
        scheduler_config_repository.set_scheduler_instance(scheduler_instance)
