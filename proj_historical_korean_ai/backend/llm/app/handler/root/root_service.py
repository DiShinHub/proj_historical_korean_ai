from starlette.requests import Request

from app.model.vo.result_vo import ResultVo
from app.tool.log_tool import LogTool


class RootService:
    __logger = LogTool.get_logger(__qualname__)

    def __init__(self):
        pass

    def get_index(self, request: Request) -> ResultVo:
        self.__logger.debug("Access Root Handler")
        return ResultVo(success=True)
