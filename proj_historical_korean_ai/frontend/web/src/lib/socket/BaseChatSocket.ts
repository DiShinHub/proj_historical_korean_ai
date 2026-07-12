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
    return [...this.rooms];
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
   * 서버 메시지 전달
   */
  protected dispatchEnvelope(envelope: ServerEnvelope): void {
    const roomName =
      envelope.client_data?.room_name ??
      envelope.client_data?.llm_response?.room_name ??
      "";

    const payload = envelope.client_data?.llm_response ?? {};

    this.messageHandlers.forEach((handler) => {
      handler(roomName, payload, envelope);
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