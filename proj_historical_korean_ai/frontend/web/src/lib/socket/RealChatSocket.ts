import { BaseChatSocket } from "./BaseChatSocket";
import type {
  OutboundCommand,
  ServerEnvelope,
} from "./types";

/*TODO : ENV 로 분리 */
const BASE_BACKOFF_MS = 1000;
const MAX_BACKOFF_MS = 30000;
const HEARTBEAT_INTERVAL = 30000;
const HEARTBEAT_TIMEOUT = 10000;


export class RealChatSocket extends BaseChatSocket {

  private ws: WebSocket | null = null;

  private manualClose = false;

  private reconnectAttempts = 0;

  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  private heartbeatTimer: ReturnType<typeof setInterval> | null = null;

  private pongTimeoutTimer: ReturnType<typeof setTimeout> | null = null;

  private connecting = false;

  constructor(
    private readonly url: string
  ) {
    super();

    if (typeof window !== "undefined") {

      window.addEventListener(
        "online",
        this.handleOnline
      );

      window.addEventListener(
        "offline",
        this.handleOffline
      );

    }
  }

  public connect(): void {

    if (typeof window === "undefined") {
      return;
    }

    if (this.connecting) {
      return;
    }

    if (
      this.ws &&
      (
        this.ws.readyState === WebSocket.OPEN ||
        this.ws.readyState === WebSocket.CONNECTING
      )
    ) {
      return;
    }

    this.connecting = true;

    this.manualClose = false;

    this.setStatus(
      this.reconnectAttempts > 0
        ? "reconnecting"
        : "connecting"
    );

    try {

      this.ws = new WebSocket(this.url);

      this.registerSocketEvents();

    } catch (err) {

      this.connecting = false;

      this.scheduleReconnect();

    }

  }

  public disconnect(): void {

    this.manualClose = true;

    this.connecting = false;

    this.stopHeartbeat();

    if (this.reconnectTimer) {

      clearTimeout(this.reconnectTimer);

      this.reconnectTimer = null;

    }

    if (this.ws) {

      this.ws.close();

      this.ws = null;

    }

    this.setConnected(false);

    this.setStatus("closed");

  }

  public subscribe(roomName: string): void {

    if (!roomName) {
      return;
    }

    this.rooms.add(roomName);

    this.send({
      command: "join_room",
      room_name: roomName,
    });

  }

  public unsubscribe(roomName: string): void {

    if (!roomName) {
      return;
    }

    this.rooms.delete(roomName);

    this.send({
      command: "leave_room",
      room_name: roomName,
    });

  }

  /**
   * Socket Event 등록
   */
  private registerSocketEvents(): void {

    if (!this.ws) {
      return;
    }

    this.ws.onopen = this.handleOpen;

    this.ws.onclose = this.handleClose;

    this.ws.onerror = this.handleError;

    this.ws.onmessage = this.handleMessage;

  }

  /**
   * reconnect
   */
  private scheduleReconnect(): void {

    if (this.manualClose) {
      return;
    }

    if (this.reconnectTimer) {
      return;
    }

    this.setStatus("reconnecting");

    const delay = Math.min(
      BASE_BACKOFF_MS * Math.pow(2, this.reconnectAttempts),
      MAX_BACKOFF_MS
    );

    this.reconnectAttempts++;

    this.reconnectTimer = setTimeout(() => {

      this.reconnectTimer = null;

      this.connect();

    }, delay);

  }

  /**
   * heartbeat 시작
   */
  private startHeartbeat(): void {

    this.stopHeartbeat();

    this.heartbeatTimer = setInterval(() => {

      if (!this.ws) {
        return;
      }

      if (this.ws.readyState !== WebSocket.OPEN) {
        return;
      }

      this.send({
        command: "ping"
      });

      if (this.pongTimeoutTimer) {

        clearTimeout(
          this.pongTimeoutTimer
        );

      }

      this.pongTimeoutTimer = setTimeout(() => {

        console.warn(
          "[Socket] heartbeat timeout"
        );

        this.ws?.close();

      }, HEARTBEAT_TIMEOUT);

    }, HEARTBEAT_INTERVAL);

  }

  /**
   * heartbeat 종료
   */
  private stopHeartbeat(): void {

    if (this.heartbeatTimer) {

      clearInterval(
        this.heartbeatTimer
      );

      this.heartbeatTimer = null;

    }

    if (this.pongTimeoutTimer) {

      clearTimeout(
        this.pongTimeoutTimer
      );

      this.pongTimeoutTimer = null;

    }

  }

  /**
   * 브라우저 Online
   */
  private handleOnline = () => {

    if (!this.connected) {

      this.connect();

    }

  };

  /**
   * 브라우저 Offline
   */
  private handleOffline = () => {

    this.setStatus("closed");

  };

  /**
   * Socket Open
   */
  private handleOpen = (): void => {

    this.connecting = false;

    this.reconnectAttempts = 0;

    this.setConnected(true);

    this.setStatus("open");

    if (this.reconnectTimer) {

      clearTimeout(this.reconnectTimer);

      this.reconnectTimer = null;

    }

    this.startHeartbeat();

    //
    // reconnect 후 자동 Room 복구
    //
    this.rooms.forEach((room) => {

      this.send({
        command: "join_room",
        room_name: room,
      });

    });

  };

  /**
   * Socket Close
   */
  private handleClose = (): void => {

    this.connecting = false;

    this.setConnected(false);

    this.stopHeartbeat();

    this.ws = null;

    if (this.manualClose) {

      this.setStatus("closed");

      return;

    }

    this.scheduleReconnect();

  };

  /**
   * Socket Error
   */
  private handleError = (): void => {

    this.connecting = false;

    this.setStatus("error");

  };

  /**
   * Socket Message
   */
  private handleMessage = (
    event: MessageEvent
  ): void => {

    let envelope: ServerEnvelope;

    try {

      envelope = JSON.parse(
        event.data
      );

    } catch {

      return;

    }

    //
    // Heartbeat 응답
    //
    if (
      envelope.command === "pong" ||
      envelope.message === "pong"
    ) {

      if (this.pongTimeoutTimer) {

        clearTimeout(
          this.pongTimeoutTimer
        );

        this.pongTimeoutTimer = null;

      }

      return;

    }

    //
    // 일반 메시지
    //
    this.dispatchEnvelope(
      envelope
    );

  };

  /**
   * Socket Send
   */
  private send(
    command: OutboundCommand
  ): void {

    if (!this.ws) {
      return;
    }

    if (
      this.ws.readyState !==
      WebSocket.OPEN
    ) {
      return;
    }

    try {

      this.ws.send(
        JSON.stringify(command)
      );

    } catch (err) {

      console.error(
        "[Socket] send failed",
        err
      );

    }

  }

  
}