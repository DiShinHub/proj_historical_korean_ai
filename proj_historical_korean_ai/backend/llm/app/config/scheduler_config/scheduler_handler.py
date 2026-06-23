import uuid
from enum import Enum
from typing import Callable

from apscheduler.job import Job
from apscheduler.triggers.cron import CronTrigger

from app.base.singleton_meta import SingletonMeta
from app.config.scheduler_config.scheduler_config_repository import SchedulerConfigRepository


class SchedulerEnum:
    class Task(str, Enum):
        START = "start"
        PAUSE = "pause"
        RESUME = "resume"
        SHUTDOWN = "shutdown"

        def __str__(self) -> str:
            return str(self.value)

    class State(int, Enum):
        STATE_STOPPED = 0
        STATE_RUNNING = 1
        STATE_PAUSED = 2

        def __str__(self) -> str:
            return str(self.value)


class SchedulerHandler(metaclass=SingletonMeta):
    __scheduler_config_repository: SchedulerConfigRepository = None

    def __init__(self, scheduler_config_repository: SchedulerConfigRepository):
        if type(scheduler_config_repository) != SchedulerConfigRepository:
            raise Exception("Scheduler_config_repository Type Must Be SchedulerConfigRepository")
        self.__scheduler_config_repository = scheduler_config_repository

    def handle(self, task: SchedulerEnum.Task, start_with_paused: bool = False) -> None:
        if self.__scheduler_config_repository is None:
            raise Exception("No Scheduler Config Repository Has Been Injected Yet.")
        if task == SchedulerEnum.Task.START:
            self.__scheduler_config_repository.get_scheduler_instance().start(paused=start_with_paused)
        elif task == SchedulerEnum.Task.PAUSE:
            self.__scheduler_config_repository.get_scheduler_instance().pause()
        elif task == SchedulerEnum.Task.RESUME:
            self.__scheduler_config_repository.get_scheduler_instance().resume()
        elif task == SchedulerEnum.Task.SHUTDOWN:
            self.__scheduler_config_repository.get_scheduler_instance().shutdown()

    def add_job_with_interval(
            self,
            job: Callable,
            interval_seconds: int,
            job_id: str = str(uuid.uuid4()),
            job_store: str = "default"
    ) -> Job:
        if self.__scheduler_config_repository is None:
            raise Exception("No Scheduler Config Repository Has Been Injected Yet.")
        if interval_seconds < 1:
            raise Exception("The Minimum Interval Seconds Value Is 1.")
        return self.__scheduler_config_repository.get_scheduler_instance().add_job(
            func=job,
            trigger="interval",
            seconds=interval_seconds,
            id=job_id,
            jobstore=job_store
        )

    def add_job_with_cron(
            self,
            job: Callable,
            cron: CronTrigger,
            job_id: str = str(uuid.uuid4()),
            job_store: str = "default"
    ) -> Job:
        if self.__scheduler_config_repository is None:
            raise Exception("No Scheduler Config Repository Has Been Injected Yet.")
        if cron is None:
            raise Exception("Expression Cannot Be Empty.")
        return self.__scheduler_config_repository.get_scheduler_instance().add_job(
            func=job,
            trigger=cron,
            id=job_id,
            jobstore=job_store
        )

    def get_jobs(self, job_store: str = "default") -> list[Job]:
        if self.__scheduler_config_repository is None:
            raise Exception("No Scheduler Config Repository Has Been Injected Yet.")
        return self.__scheduler_config_repository.get_scheduler_instance().get_jobs(jobstore=job_store)

    def get_job(self, job_id: str, job_store: str = "default") -> Job:
        if self.__scheduler_config_repository is None:
            raise Exception("No Scheduler Config Repository Has Been Injected Yet.")
        if job_id is None or job_id == "":
            raise Exception("Job ID Cannot Be Empty.")
        return self.__scheduler_config_repository.get_scheduler_instance().get_job(job_id=job_id, jobstore=job_store)

    def pause_job(self, job_id: str, job_store: str = "default") -> Job:
        if self.__scheduler_config_repository is None:
            raise Exception("No Scheduler Config Repository Has Been Injected Yet.")
        if job_id is None or job_id == "":
            raise Exception("Job ID Cannot Be Empty.")
        return self.__scheduler_config_repository.get_scheduler_instance().pause_job(job_id=job_id, jobstore=job_store)

    def resume_job(self, job_id: str, job_store: str = "default") -> Job:
        if self.__scheduler_config_repository is None:
            raise Exception("No Scheduler Config Repository Has Been Injected Yet.")
        if job_id is None or job_id == "":
            raise Exception("Job ID Cannot Be Empty.")
        return self.__scheduler_config_repository.get_scheduler_instance().resume_job(job_id=job_id, jobstore=job_store)

    def remove_job(self, job_id: str, job_store: str = "default"):
        if self.__scheduler_config_repository is None:
            raise Exception("No Scheduler Config Repository Has Been Injected Yet.")
        if job_id is None or job_id == "":
            raise Exception("Job ID Cannot Be Empty.")
        self.__scheduler_config_repository.get_scheduler_instance().remove_job(job_id=job_id, jobstore=job_store)

    def remove_all_jobs(self, job_store: str = "default"):
        if self.__scheduler_config_repository is None:
            raise Exception("No Scheduler Config Repository Has Been Injected Yet.")
        self.__scheduler_config_repository.get_scheduler_instance().remove_all_jobs(jobstore=job_store)

    def get_state(self) -> SchedulerEnum.State:
        if self.__scheduler_config_repository is None:
            raise Exception("No Scheduler Config Repository Has Been Injected Yet.")
        return SchedulerEnum.State(self.__scheduler_config_repository.get_scheduler_instance().state)
