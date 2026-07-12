export type SocketStatus =
  | "idle"
  | "connecting"
  | "open"
  | "reconnecting"
  | "closed"
  | "error";

export interface JoinRoomCommand {
  command: "join_room";
  room_name: string;
}

export interface LeaveRoomCommand {
  command: "leave_room";
  room_name: string;
}

export interface EmitRoomCommand {
  command: "emit_room";
  room_name: string;
  client_data?: unknown;
}

export interface PingCommand {
  command: "ping";
}

export type OutboundCommand =
  | JoinRoomCommand
  | LeaveRoomCommand
  | EmitRoomCommand
  | PingCommand;

export interface ServerEnvelope {
  response_code: number;
  message: string;
  command?: string;
  client_data: {
    command?: string;
    room_name?: string;
    llm_response?: LlmResponsePayload;
  } | null;
}

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

export type StatusHandler = (
  status: SocketStatus
) => void;

export interface IChatSocket {
  connect(): void;
  disconnect(): void;

  subscribe(roomName: string): void;
  unsubscribe(roomName: string): void;

  onMessage(handler: RoomMessageHandler): () => void;
  onStatus(handler: StatusHandler): () => void;

  getStatus(): SocketStatus;
}