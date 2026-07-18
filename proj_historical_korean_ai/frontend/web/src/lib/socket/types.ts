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
  // 백엔드 라우터는 모든 command 에 room_name 을 요구한다(없으면 400).
  // 그래서 하트비트 ping 에도 반드시 room_name 을 실어야 pong 이 돌아온다.
  room_name: string;
}

export type OutboundCommand =
  | JoinRoomCommand
  | LeaveRoomCommand
  | EmitRoomCommand
  | PingCommand;

/**
 * 서버(또는 worker)가 브라우저로 보내는 프레임.
 *
 * ⚠️ 실제 백엔드 동작 기준으로 정의한다.
 * worker가 룸에 emit 하면 서버(web_socket_handler.emit_room)는 worker가 보낸
 * 원본 dict 를 그대로 브라우저에 전달한다. 그래서 브라우저가 받는 실제 프레임은
 * "평평한" 형태다:
 *   { command: "emit_room_connectionless", room_name: "1", llm_response: {...} }
 *
 * 반면 join/leave/ping 같은 명령에 대한 서버 ack 는:
 *   { response_code: 200, message: "join success" }           (join/leave)
 *   { response_code: 200, command: "pong", message: "pong" }  (ping)
 * 처럼 llm_response 가 없는 형태로 온다.
 *
 * 아래 필드는 위 두 형태를 모두 담기 위해 대부분 optional 이다.
 * (client_data 는 과거 계약/목(mock) 하위호환용으로만 남겨둔다.)
 */
export interface ServerEnvelope {
  // ack 프레임에만 존재
  response_code?: number;
  message?: string;
  // "pong" / "emit_room_connectionless" 등
  command?: string;

  // 실제 룸 응답 프레임(평평한 형태)의 필드
  room_name?: string;
  llm_response?: LlmResponsePayload;

  // (하위호환) 과거에 가정했던 래핑 구조
  client_data?: {
    command?: string;
    room_name?: string;
    llm_response?: LlmResponsePayload;
  } | null;
}

/**
 * LLM 응답 페이로드.
 *
 * 최종적으로 백엔드가 확정할 필드는 { text, done?, audio_url?, message_seq? } 이지만,
 * 현재 worker 는 플레이스홀더로 { result, llm_msg } 를 보낸다(LLM 미연동).
 * 프론트는 과도기 동안 text ?? result ?? llm_msg 순으로 방어적으로 읽는다.
 */
export interface LlmResponsePayload {
  // 확정 예정 필드
  text?: string;
  done?: boolean;
  audio_url?: string;
  message_seq?: number;
  room_name?: string;

  // 현재 백엔드 플레이스홀더 필드
  result?: string;
  llm_msg?: string;

  // (참고) 에코되던 필드
  prompt?: string;
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