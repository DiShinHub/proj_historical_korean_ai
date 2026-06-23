from apscheduler.triggers.cron import CronTrigger
from fastapi.applications import AppType
from sqlalchemy.ext.asyncio import AsyncEngine

from app.base.singleton_meta import SingletonMeta
from app.config.database_config.database_config_entities_runner import DatabaseConfigEntitiesRunner
from app.config.database_config.database_config_repository import get_engine
from app.config.scheduler_config.scheduler_config_repository import scheduler_config_repository
from app.config.scheduler_config.scheduler_config_runner import SchedulerConfigRunner
from app.config.scheduler_config.scheduler_handler import SchedulerHandler, SchedulerEnum
from app.constant.app_properties import app_properties
from app.tool.class_tool import ClassTool
from app.tool.log_tool import LogTool
from app.tool.pid_tool import PidTool


class EventHandlerConfigRunner(metaclass=SingletonMeta):
    __logger = LogTool.get_logger(__qualname__)
    __app: AppType

    def __init__(
            self,
            app: AppType,
    ):
        self.__logger.info("Initialize Event Handler Config Runner")
        self.__app = app

    def run(self):
        self.__logger.debug("Run Event Handler Config Start")
        self.__app.add_event_handler("startup", self.on_event_startup)
        self.__app.add_event_handler("shutdown", self.on_event_shutdown)

    async def on_event_startup(self):
        PidTool.create_pid_file(file_name="app.pid")
        if app_properties.DATABASE_CONFIG_ENTITIES_USE:
            database_config_entities_runner = DatabaseConfigEntitiesRunner(get_engine())
            if type(get_engine()) is AsyncEngine:
                await database_config_entities_runner.run_async()
            else:
                database_config_entities_runner.run_sync()

        if app_properties.SCHEDULER_USE is True:
            scheduler_config_runner = SchedulerConfigRunner()
            scheduler_config_runner.run()
            scheduler_handler = SchedulerHandler(scheduler_config_repository)
            scheduler_handler.handle(SchedulerEnum.Task.START,
                                     start_with_paused=app_properties.SCHEDULER_AUTOSTART is False)

            scheduler_handler.add_job_with_cron(
                job=ClassTool.get_instance_method(
                    module_name="app.job.sleep.sleep_job",
                    class_name="SleepJob",
                    method_name="task"
                ),
                cron=CronTrigger(year="*", month="*", day="*", hour="*", minute="*", second="*/20",
                                 timezone="Asia/Seoul")
            )

            # scheduler_handler.add_job_with_cron(
            #     job=ClassTool.get_instance_method(
            #         module_name="app.job.cmd.cmd_job",
            #         class_name="CmdJob",
            #         method_name="task"
            #     ),
            #     cron=CronTrigger(year="*", month="*", day="*", hour="*", minute="*/10", second="0", timezone="Asia/Seoul")
            # )

            # scheduler_handler.add_job_with_interval(
            #     job=ClassTool.get_instance_method(
            #         module_name="app.job.sample.sample_job",
            #         class_name="SampleJob",
            #         method_name="task"
            #     ),
            #     interval_seconds=10
            # )

    def on_event_shutdown(self):
        PidTool.remove_pid_file(file_name="app.pid")
