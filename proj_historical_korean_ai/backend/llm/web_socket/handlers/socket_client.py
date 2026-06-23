from web_socket.tool.log_tool import LogTool
from web_socket.config.web_socket_config.web_socket_config_runner import WebSocketConfigRunner

import socket
import threading
import json

class SocketClient():
    
    __logger = LogTool.get_logger(__qualname__)

    def __init__(self, username):

        properties_dict: dict = WebSocketConfigRunner().get_properties()
        self.host = properties_dict.get("host")
        self.port = int(properties_dict.get("port"))
        self.client_socket = None

        self.username = username

    def connect(self):

        # 소켓 생성
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("hk-ai-websocket-compose", self.port))

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

"""
# --- 접속
# docker exec -it hk-ai-websocket-compose bash
# poetry run python /apps/web_socket/handlers/socket_client.py

# --- 사용
사용자 이름을 입력하세요: tester1234
명령을 입력하세요 join/leave [room_name] or exit : join room_test
명령을 입력하세요 join/leave [room_name] or exit : leave room_test
명령을 입력하세요 join/leave [room_name] or exit : exit
"""
if __name__ == "__main__":

    # 사용자 이름 입력
    username = input("사용자 이름을 입력하세요: ")

    socket_client = SocketClient(username)
    socket_client.connect()

    while True:
        try:
            command = input("명령을 입력하세요 join/leave [room_name] or exit : ")
            if command == 'exit':
                socket_client.disconnect()
                break

            # 종목 룸 입장 요청
            elif command.startswith('join'):
                room_name = command.split(' ')[1]
                request = {"command": "join_room", "room_name": room_name}

            # 종목 룸 나가기 요청
            elif command.startswith('leave'):
                room_name = command.split(' ')[1]
                request = {"command": "leave_room", "room_name": room_name}

            socket_client.send_data(json.dumps(request).encode())

        except Exception as ex:
            print(ex)
