from task_worker.tool.log_tool import LogTool
from task_worker.config.web_socket_config.web_socket_config_runner import WebSocketConfigRunner

import asyncio
import json
import websockets


import websockets
import threading
import json

class SocketClientModule():
    
    __logger = LogTool.get_logger(__qualname__)

    def __init__(self, username):

        properties_dict: dict = WebSocketConfigRunner().get_properties()
        self.host = properties_dict.get("host")
        self.port = int(properties_dict.get("port"))
        self.url = f"ws://{self.host}:/websocket/ws"
        self.client_socket = None

        self.username = username

    async def connect(self):

        async with websockets.connect(URL) as ws:

            print("Connected")

        # 소켓 생성
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("hk-ai-websocket-compose", self.port))
        
        # 연결 
        self.send_data(self.username.encode())

        # 메시지 수신을 처리하는 스레드 시작
        receive_thread = threading.Thread(
            target=self.receive_data,
            daemon=True
            )
        
        receive_thread.start()

    def disconnect(self):

        try:
            self.client_socket.shutdown(socket.SHUT_RDWR)

        except Exception:
            pass

        self.client_socket.close()

    def send_data(self, msg):
        self.client_socket.sendall(msg)
    
    def receive_data(self):

        while True:
            try:
                # 서버로부터 데이터 수신
                data = self.client_socket.recv(8192)
                if not data:
                    break

                # 데이터 파싱 (JSON)
                data = json.loads(data.decode())
                self.__logger.info(f"data : {data}")
                    
            except Exception as e:
                print(f"서버와의 통신 오류: {e}")
                break