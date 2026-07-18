import type {
  IChatSocket,
  RoomMessageHandler,
  ServerEnvelope,
  SocketStatus,
  StatusHandler,
} from "./types";

/**
 * Base WebSocket implementation.
 *
 * 역할
 *  - Room 목록 관리
 *  - Socket 상태 관리
 *  - Message Event 관리
 *  - Status Event 관리
 *
 * 실제 WebSocket 연결은 RealChatSocket에서 담당한다.
 */
export abstract class BaseChatSocket implements IChatSocket {
  /**
   * 현재 Join 되어있는 Room 목록
   * reconnect 성공 시 자동 재구독에 사용된다.
   */
  protected readonly rooms = new Set<string>();

  /**
   * 현재 Socket 상태
   */
  protected status: SocketStatus = "idle";

  /**
   * 실제 연결 여부
   */
  protected connected = false;

  /**
   * Message Listener
   */
  private readonly messageHandlers = new Set<RoomMessageHandler>();

  /**
   * Status Listener
   */
  private readonly statusHandlers = new Set<StatusHandler>();

  abstract connect(): void;

  abstract disconnect(): void;

  abstract subscribe(roomName: string): void;

  abstract unsubscribe(roomName: string): void;

  /**
   * 현재 Socket 상태 반환
   */
  getStatus(): SocketStatus {
    return this.status;
  }

  /**
   * 현재 연결 여부
   */
  isConnected(): boolean {
    return this.connected;
  }

  /**
   * 현재 Join 되어있는 Room 목록
   */
  getSubscribedRooms(): string[] {
    return Array.from(this.rooms);
  }

  /**
   * Message Event 등록
   */
  onMessage(handler: RoomMessageHandler): () => void {
    this.messageHandlers.add(handler);

    return () => {
      this.messageHandlers.delete(handler);
    };
  }

  /**
   * Status Event 등록
   */
  onStatus(handler: StatusHandler): () => void {
    this.statusHandlers.add(handler);

    // 현재 상태 즉시 전달
    handler(this.status);

    return () => {
      this.statusHandlers.delete(handler);
    };
  }

  /**
   * 상태 변경
   */
  protected setStatus(status: SocketStatus): void {
    if (this.status === status) {
      return;
    }

    this.status = status;

    this.statusHandlers.forEach((handler) => {
      handler(status);
    });
  }

  /**
   * 연결 상태 변경
   */
  protected setConnected(connected: boolean): void {
    this.connected = connected;
  }

  /**
   * 서버 프레임을 정규화해서 Message Listener 로 전달한다.
   *
   * [소켓 이벤트 흐름]
   *  worker emit → 서버가 원본 dict 전달 → 브라우저 onmessage → 이 함수
   *
   * 실제 룸 응답 프레임은 평평한 형태다:
   *   { command, room_name, llm_response: {...} }
   * 반면 join/leave/400 같은 ack 프레임에는 llm_response 가 없다.
   * → llm_response 가 없는 프레임(순수 ack/에러)은 채팅 흐름과 무관하므로
   *   Listener 로 전달하지 않고 여기서 무시한다.
   */
  protected dispatchEnvelope(envelope: ServerEnvelope): void {
    // 평평한 프레임(우선) → 과거 래핑 구조(하위호환) 순으로 room_name/payload 를 찾는다.
    const roomName =
      envelope.room_name ??
      envelope.llm_response?.room_name ??
      envelope.client_data?.room_name ??
      envelope.client_data?.llm_response?.room_name ??
      "";

    const payload =
      envelope.llm_response ?? envelope.client_data?.llm_response;

    // llm_response 도 없고 room_name 도 없으면 join/leave/ping 등의 단순 ack →
    // 채팅 화면과 무관하므로 무시한다(오류 처리하지 않는다).
    if (!payload && !roomName) {
      return;
    }

    console.log("[Socket] 응답 수신", roomName, payload ?? envelope);

    this.messageHandlers.forEach((handler) => {
      handler(roomName, payload ?? {}, envelope);
    });
  }

  /**
   * 모든 Listener 제거
   */
  protected clearListeners(): void {
    this.messageHandlers.clear();
    this.statusHandlers.clear();
  }
}