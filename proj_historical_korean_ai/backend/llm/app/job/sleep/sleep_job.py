import asyncio
import time
from datetime import datetime

from app.tool.log_tool import LogTool


class SleepJob:
    __logger = LogTool.get_logger(__qualname__)

    def __init__(self):
        pass

    async def task(self):
        self.__logger.debug(f"scheduler called SleepJob: {datetime.now()}")

        start_time = time.time()
        self.__logger.debug(f"sleep start, now = [{start_time}]")

        loop_interval = 5
        loop_count = 0
        while time.time() - start_time < loop_interval:
            loop_count += 1
            # await asyncio.sleep(0.1)
            await asyncio.sleep(0.001)

        self.__logger.debug(
            f"sleep end, now = [{time.time() - start_time}], loop_interval = [{loop_interval}], loop_count = [{loop_count}]")
