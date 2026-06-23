from pydantic import BaseModel
from pydantic.v1 import Field

from app.enums.app_enum import AppEnum


class AppProperties(BaseModel):
    ACTIVE_ENV: AppEnum.ActiveEnv = AppEnum.ActiveEnv.LOCAL
    DATABASE_CONFIG_ENTITIES_USE: bool = False

    ##################################################
    # from properties file
    ##################################################
    # system
    DEBUG: bool = True
    APP_NAME: str = "app_name"
    APP_DESCRIPTION: str = "app_description"
    APP_VERSION: str = "0.1.0"

    # cors
    CORS_ALLOW_ORIGINS: list[str] = Field(default_factory=list)

    # metrics
    METRICS_PROMETHEUS_USE: bool = False

    # scheduler
    SCHEDULER_USE: bool = False
    SCHEDULER_AUTOSTART: bool = False

    ##################################################
    # ///
    ##################################################
    TIMEZONE: str = "Asia/Seoul"


app_properties = AppProperties.model_construct()
