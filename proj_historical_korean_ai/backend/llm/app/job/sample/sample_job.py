from datetime import datetime

from app.tool.log_tool import LogTool


class SampleJob:
    __logger = LogTool.get_logger(__qualname__)

    def __init__(self):
        pass

    async def task(self):
        self.__logger.debug(f"scheduler called SampleJob: {datetime.now()}")
