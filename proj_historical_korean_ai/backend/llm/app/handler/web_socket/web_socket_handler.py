from app.tool.log_tool import LogTool
from fastapi import WebSocket

class WebSocketHandler:
    
    __logger = LogTool.get_logger(__qualname__)

    def __init__(self):
        self.rooms: dict[str, list[WebSocket]] = {}

    async def join_room(self, room_name: str, client_socket: WebSocket):

        if room_name not in self.rooms:
            self.rooms[room_name] = []

        if client_socket not in self.rooms[room_name]:
            self.rooms[room_name].append(client_socket)

    async def leave_room(self, room_name: str, client_socket: WebSocket):
        
        if room_name in self.rooms and \
            client_socket in self.rooms[room_name]:
            self.rooms[room_name].remove(client_socket)

    async def emit_room(self, room_name: str, client_socket: WebSocket, data: dict):

        # 에밋
        dead = []
        if room_name in self.rooms:
            for client in self.rooms[room_name]:
                if client != client_socket: # 에밋을 수행하는 클라이언트에겐 보내지 않음

                    try:
                        await client.send_json(data)

                    except Exception as e:
                        dead.append(client)
                        self.__logger.info(f"WebSocketHandler.emit_room error, client:{str(client)}, room:{str(room_name)} data:{str(data)}, error:{str(e)}")

        for client in dead:
            self.rooms[room_name].remove(client)
            await client.close()