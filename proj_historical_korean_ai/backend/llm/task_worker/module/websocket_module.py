from task_worker.config.web_socket_config.web_socket_config_runner import WebSocketConfigRunner
from task_worker.tool.log_tool import LogTool

import asyncio
import threading
import json
import websockets
import time

class WebSocketModule:

    def __init__(self):
        self.__logger = LogTool.get_logger(self.__class__.__name__) 

        properties_dict: dict = WebSocketConfigRunner().get_properties()

        self.host = properties_dict.get("host")
        self.port = int(properties_dict.get("port"))
        self.url = f"ws://hk-ai-compose:28001/websocket/ws"

        self.ws = None

        self.loop = None
        self.thread = None

        self.lock = None

    def start(self):

        if self.thread is not None:
            return

        self.thread = threading.Thread(
            target=self._run_loop,
            daemon=True,
            name="WebSocketLoop"
        )
        self.thread.start()

    def _run_loop(self):

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.lock = asyncio.Lock()

        self.loop.run_until_complete(self.connect())
        self.loop.run_forever()

    async def connect(self):

        async with self.lock:

            for i in range (0, 10):
                try:
                    if self.ws is not None:
                        return

                    self.ws = await websockets.connect(
                        self.url,
                        ping_interval=20,
                        ping_timeout=20,
                    )
                    self.__logger.info(f"WebSocketModule.connected.")

                    return 

                except Exception as e:
                    self.ws = None
                    self.__logger.info(f"WebSocketModule.connect error: retry : {str(i+1)}, {str(e)}")
                    time.sleep(1)

            self.__logger.info(f"WebSocketModule.connect fail")


    async def disconnect(self):

        async with self.lock:

            if self.ws is not None:

                await self.ws.close()
                self.ws = None

                self.__logger.info("WebSocket Closed")

    async def reconnect(self):

        self.__logger.warning("Reconnect WebSocket")

        await self.disconnect()
        await self.connect()

    def send(self, room_name: str, data: dict):

        if self.loop is None:
            raise RuntimeError("WebSocketModule is not started.")

        future = asyncio.run_coroutine_threadsafe(
            self._send(room_name, data),
            self.loop
        )

        return future

    async def _send(self, room_name: str, data: dict):

        payload = {
            "command": "emit_room_connectionless",
            "room_name": room_name,
            **data
        }
        
        try:
            if self.ws is None:
                await self.connect()
            
            await self.ws.send(json.dumps(payload))

        except Exception as e:
            self.__logger.error(f"emit failed : {e}")
            await self.reconnect()
            await self.ws.send(json.dumps(payload))

# single tone
web_socket_module = WebSocketModule()
web_socket_module.start()