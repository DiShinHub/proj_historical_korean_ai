from web_socket.tool.log_tool import LogTool
from web_socket.config.web_socket_config.web_socket_config_runner import WebSocketConfigRunner

import socket
import threading
import json


class SocketServer():
    """
    유저의 활성회 된 세션만 소켓 연결 유지
    세션당 룸 1개 
    에밋을 수행하는 클라이언트는 비연결 유지형
    """
    
    __logger = LogTool.get_logger(__qualname__)

    def __init__(self):

        self.host = None
        self.port = None
        self.server_socket = None
        self.rooms = {}

    def run(self):

        properties_dict: dict = WebSocketConfigRunner().get_properties()
        self.host = properties_dict.get("host")
        self.port = int(properties_dict.get("port"))

        # 소켓생성, 로컬 호스트와 포트에 바인딩
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("hk-ai-websocket-compose", self.port))

        # 클라이언트 연결 대기
        self.listen_connect()

    def listen_connect(self):

        self.server_socket.listen()
        self.__logger.info(f"소켓 서버가 클라이언트 요청을 대기 중입니다")

        while True:
            try:
                # 클라이언트 연결 수락
                client_socket, client_address = self.server_socket.accept()
                self.__logger.info(f"{client_address}가 연결되었습니다.")

                # 클라이언트로부터 사용자 이름 수신
                username = client_socket.recv(1024).decode()

                # 클라이언트를 처리하는 스레드 시작
                client_handler = threading.Thread(target=self.handle_client, args=(client_socket, username))
                client_handler.start()
                
            except Exception as e:
                self.__logger.info(f"리스너 오류 : {e}")
                break

    def handle_client(self, client_socket, username):

        try:
            client_data = None
            room_name = None
            command = None

            while True:
                # --- 데이터 수신 및 예외처리
                client_data = client_socket.recv(8192)
                if not client_data:
                    break
                
                client_data = json.loads(client_data.decode('utf-8'))
                room_name = client_data.get("room_name")
                command = client_data.get("command")
                
                if command == None:
                    self.send_msg(
                        message=f"올바른 명령이 지정되지 않았습니다",
                        response_code=400,
                        client_socket=client_socket
                    )
                
                elif room_name == None:
                    self.send_msg(
                        message=f"room_name을 지정하세요",
                        response_code=400,
                        client_socket=client_socket
                    )

                else:
                    # case 1 : 룸에 입장 요청
                    if command == "join_room":
                        self.join_room(room_name, username, client_socket)

                    # case 2 : 룸에서 나가기 요청
                    elif command == "leave_room":
                        self.leave_room(room_name, username, client_socket)

                    elif command == "emit_to_room":
                        self.emit_to_room(room_name, username, client_socket, client_data)

                    elif command == "emit_to_room_connectionless":
                        self.join_room(room_name, username, client_socket)
                        self.emit_to_room(room_name, username, client_socket, client_data)
                        self.leave_room(room_name, username, client_socket)

                    elif command == "emit_to_client":
                        # TODO : 필요시 개발
                        pass
            
        except Exception as e:
            self.__logger.info(client_data)
            self.__logger.info(f"클라이언트와의 통신 오류 : {e}")

        finally:
            self.disconnect(username, room_name, client_socket)

    def join_room(self, room_name, username, client_socket):

        if room_name not in self.rooms:
            self.rooms[room_name] = []

        self.rooms[room_name].append(client_socket)

        self.send_msg(
            message=f"'{username}'이 '{room_name}'에 입장하였습니다",
            response_code=200,
            client_socket=client_socket
        )
    
    def leave_room(self, room_name, username, client_socket):
        
        if room_name in self.rooms and client_socket in self.rooms[room_name]:
            self.rooms[room_name].remove(client_socket)
            
            self.send_msg(
                message=f"'{username}'이 '{room_name}'을 떠났습니다",
                response_code=200,
                client_socket=client_socket
            )
            
        else:
            self.send_msg(
                message=f"'{username}'은 '{room_name}'에 없습니다.",
                response_code=400,
                client_socket=client_socket
            )

    def emit_to_room(self,room_name, username, client_socket, client_data):

        # 입장 처리
        self.join_room(room_name, username, client_socket)

        # 에밋
        if room_name in self.rooms:
            for client in self.rooms[room_name]:
                if client != client_socket: # 에밋을 수행하는 클라이언트에겐 보내지 않음
                    self.send_msg(
                        message=f"테스크 처리에 성공하였습니다",
                        response_code=200,
                        client_socket=client_socket,
                        client_data=client_data,
                    )
    
        # 퇴장 처리
        self.leave_room(room_name, username, client_socket)
    
    def send_msg(self, message, response_code, client_socket, client_data=None):

        response = {
            "message": message,
            "response_code": response_code,
            "client_data": client_data,
        }
        self.__logger.info(f"response : {response}")


        client_socket.send(json.dumps(response).encode())
        self.__logger.info(message)

    def disconnect(self, username, room_name, client_socket):

        self.leave_room(room_name, username, client_socket)
        client_socket.close()
        self.__logger.info(f"{username}의 연결이 종료되었습니다.")





            