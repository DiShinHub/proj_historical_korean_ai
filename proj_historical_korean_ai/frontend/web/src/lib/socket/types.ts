// Socket contract types.
//
// The current backend "socket" is a raw TCP server (checkpoint #1) that a
// browser cannot reach. These types describe the JSON protocol it speaks; a
// browser-facing WebSocket/SSE bridge is expected to relay the same shapes.

export type SocketStatus =
  | "idle"
  | "connecting"
  | "open"
  | "reconnecting"
  | "closed"
  | "error";

// ---- Outbound: client -> server ----
export interface JoinRoomCommand {
  command: "join_room";
  room_name: string;
}
export interface LeaveRoomCommand {
  command: "leave_room";
  room_name: string;
}
export type OutboundCommand = JoinRoomCommand | LeaveRoomCommand;

// ---- Inbound: server -> client (socket_server.send_msg) ----
export interface ServerEnvelope {
  message: string;
  response_code: number; // 200 ok, 400 error
  client_data: {
    command?: string;
    room_name?: string;
    llm_response?: LlmResponsePayload;
  } | null;
}

/**
 * The assistant payload carried in `client_data.llm_response`.
 *
 * Today the worker only echoes `{ prompt, room_name }` (checkpoint #2).
 * `text` / `audio_url` / `done` are the intended future fields the frontend
 * is already built to consume:
 *  - `text`  : a chunk of assistant output to append (delta).
 *  - `done`  : false while streaming, true/absent on the final message.
 */
export interface LlmResponsePayload {
  prompt?: string;
  room_name?: string;
  text?: string;
  audio_url?: string;
  message_seq?: number;
  done?: boolean;
}

export type RoomMessageHandler = (
  roomName: string,
  payload: LlmResponsePayload,
  envelope: ServerEnvelope
) => void;

export type StatusHandler = (status: SocketStatus) => void;

/** Transport-agnostic socket interface shared by the real and mock clients. */
export interface IChatSocket {
  connect(): void;
  disconnect(): void;
  subscribe(roomName: string): void;
  unsubscribe(roomName: string): void;
  onMessage(handler: RoomMessageHandler): () => void;
  onStatus(handler: StatusHandler): () => void;
  getStatus(): SocketStatus;
}
