from app.handler.web_socket.web_socket_handler import WebSocketHandler
from app.tool.log_tool import LogTool

from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

router = APIRouter(
    prefix="/websocket"
)

web_socket_handler = WebSocketHandler()

__logger = LogTool.get_logger()



@router.websocket("/ws")
async def websocket_endpoint(
    client_socket: WebSocket,
):  

    await client_socket.accept()

    room_name = None

    while True:

        try:
            # 데이터 분리
            data = await client_socket.receive_json()
            command = data.get("command")
            room_name = data.get("room_name")

            # 예외처리
            if command == None:
                await client_socket.send_json({
                    "response_code":400,
                    "message":"올바른 명령이 지정되지 않았습니다"
                })
                continue

            elif room_name == None:
                await client_socket.send_json({
                    "response_code":400,
                    "message":"room_name을 지정하세요"
                })
                continue

            # 명령어 처리
            if command == "ping":
                await client_socket.send_json({
                    "response_code":200,
                    "command": "pong",
                    "message":"pong"
                })

            elif command == "join_room":
                await web_socket_handler.join_room(room_name, client_socket)

                await client_socket.send_json({
                    "response_code":200,
                    "message":"join success"
                })

            elif command == "leave_room":
                await web_socket_handler.leave_room(room_name, client_socket)
                await client_socket.send_json({
                    "response_code":200,
                    "message":"leave success"
                })

            elif command == "emit_room":
                await web_socket_handler.emit_room(room_name, client_socket, data)

            elif command == "emit_room_connectionless":
                await web_socket_handler.join_room(room_name, client_socket)
                await web_socket_handler.emit_room(room_name, client_socket, data)
                await web_socket_handler.leave_room(room_name, client_socket)

        # handle disconnect
        except WebSocketDisconnect:

            if room_name:
                await web_socket_handler.leave_room(room_name, client_socket)
                __logger.info(f"WebSocketDisconnect : {str(client_socket)} in {room_name}")

            break

        # handle unexpected error, 로깅 후 연결을 강제 close. 서버
        except Exception as e:
            __logger.info(f"websocket_endpoint unexpected error : {str(e)}")

            if room_name:
                try:
                    await web_socket_handler.leave_room(room_name, client_socket)
                    await client_socket.close()
                    __logger.info(f"websocket_endpoint error : {str(client_socket)} in {room_name}")

                except Exception as e:
                    pass
            break