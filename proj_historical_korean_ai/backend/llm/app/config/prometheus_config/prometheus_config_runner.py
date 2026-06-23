from fastapi.applications import AppType
from prometheus_fastapi_instrumentator import PrometheusFastApiInstrumentator

from app.base.singleton_meta import SingletonMeta
from app.constant.app_properties import app_properties
from app.tool.log_tool import LogTool


class PrometheusConfigRunner(metaclass=SingletonMeta):
    __logger = LogTool.get_logger(__qualname__)

    __app: AppType

    def __init__(
            self,
            app: AppType,
    ):
        self.__logger.info("Initialize Prometheus Config Runner")
        self.__app = app

    def run(self):
        self.__logger.debug("Run Prometheus Config Start")
        if app_properties.METRICS_PROMETHEUS_USE:
            PrometheusFastApiInstrumentator(
                should_group_status_codes=True,
                should_ignore_untemplated=True,
                should_respect_env_var=False,
                should_instrument_requests_inprogress=True,
                excluded_handlers=["/api/v1/au/metrics"],
                env_var_name="ENABLE_METRICS",
                inprogress_name="inprogress",
                inprogress_labels=True,
            ).instrument(self.__app).expose(app=self.__app, endpoint="/api/v1/au/metrics", tags=["/api/v1/au/metrics"])
