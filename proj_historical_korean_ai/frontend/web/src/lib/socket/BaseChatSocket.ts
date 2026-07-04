import type {
  IChatSocket,
  RoomMessageHandler,
  ServerEnvelope,
  SocketStatus,
  StatusHandler,
} from "./types";

/** Shared handler bookkeeping for socket implementations. */
export abstract class BaseChatSocket implements IChatSocket {
  protected rooms = new Set<string>();
  protected status: SocketStatus = "idle";

  private messageHandlers = new Set<RoomMessageHandler>();
  private statusHandlers = new Set<StatusHandler>();

  abstract connect(): void;
  abstract disconnect(): void;
  abstract subscribe(roomName: string): void;
  abstract unsubscribe(roomName: string): void;

  getStatus(): SocketStatus {
    return this.status;
  }

  onMessage(handler: RoomMessageHandler): () => void {
    this.messageHandlers.add(handler);
    return () => this.messageHandlers.delete(handler);
  }

  onStatus(handler: StatusHandler): () => void {
    this.statusHandlers.add(handler);
    handler(this.status); // emit current state immediately
    return () => this.statusHandlers.delete(handler);
  }

  protected setStatus(status: SocketStatus): void {
    if (this.status === status) return;
    this.status = status;
    this.statusHandlers.forEach((h) => h(status));
  }

  /** Route a server envelope to subscribers, resolving the room name. */
  protected dispatchEnvelope(envelope: ServerEnvelope): void {
    const roomName =
      envelope.client_data?.room_name ??
      envelope.client_data?.llm_response?.room_name ??
      "";
    const payload = envelope.client_data?.llm_response ?? {};
    this.messageHandlers.forEach((h) => h(roomName, payload, envelope));
  }
}
