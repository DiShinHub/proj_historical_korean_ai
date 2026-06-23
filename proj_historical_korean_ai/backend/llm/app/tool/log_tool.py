import inspect
import os.path
from logging import Logger, getLogger

from app.tool.path_tool import PathTool


class LogTool:
    LOGGER_PREFIX: str = "app"

    @staticmethod
    def get_logger(class_name: str = "", logger_prefix: str = LOGGER_PREFIX) -> Logger:
        if class_name == "":
            logger_name = ".".join(
                PathTool.get_relative_path_from_project(inspect.stack()[1][1]).lstrip(os.path.sep).replace(".py", "").split(os.path.sep))
        else:
            logger_name = class_name
        logger_name = logger_name if LogTool.LOGGER_PREFIX in logger_name else logger_prefix + "." + logger_name
        return getLogger(logger_name)
