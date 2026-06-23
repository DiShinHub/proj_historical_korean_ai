from app.model.vo.result_vo import ResultVo
from app.tool.log_tool import LogTool


class HealthService:
    __logger = LogTool.get_logger(__qualname__)

    def __init__(self):
        pass

    async def get_index(self) -> ResultVo:
        return ResultVo(success=True)
