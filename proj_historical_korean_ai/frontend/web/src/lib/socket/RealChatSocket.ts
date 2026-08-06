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

    console.log("[Socket] 연결 시도", this.url);

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

      //
      // 핸들러를 먼저 떼어낸 뒤 닫는다.
      //
      // close() 는 비동기라 onclose(handleClose)가 나중에 발화하는데,
      // 그 사이 다른 화면이 connect() 를 호출하면(예: 채팅 → 사전 페이지 이동)
      // manualClose 가 이미 false 로 돌아가 있어 handleClose 가
      // "예기치 않은 끊김"으로 오인 → this.ws 를 null 로 덮고 재연결을
      // 예약해 버린다(새로 연결한 소켓이 유령이 된다).
      // 수동 종료는 어차피 이후 이벤트가 필요 없으므로 여기서 끊어 둔다.
      //
      this.ws.onopen = null;
      this.ws.onclose = null;
      this.ws.onerror = null;
      this.ws.onmessage = null;

      this.ws.close();

      this.ws = null;

    }

    this.setConnected(false);

    this.setStatus("closed");

  }

  /**
   * Room 구독(Join). 활성 세션의 room_name(=chat_session_seq)에 조인한다.
   * rooms Set 에 저장해 두면 재연결 성공 시(handleOpen) 자동으로 다시 조인된다.
   */
  public subscribe(roomName: string): void {

    if (!roomName) {
      return;
    }

    this.rooms.add(roomName);

    console.log("[Socket] Room Join", roomName);

    this.send({
      command: "join_room",
      room_name: roomName,
    });

  }

  /**
   * Room 구독 해제(Leave). 응답이 끝난 세션의 room 에서 나간다.
   */
  public unsubscribe(roomName: string): void {

    if (!roomName) {
      return;
    }

    this.rooms.delete(roomName);

    console.log("[Socket] Room Leave", roomName);

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
   *
   * 주기적으로 ping 을 보내고, 정해진 시간 안에 pong 이 오지 않으면
   * 죽은 연결로 보고 소켓을 닫는다(→ 자동 재연결).
   *
   * ⚠️ 백엔드 라우터는 모든 command 에 room_name 을 요구하므로
   * ping 에도 현재 구독 중인 room 하나를 실어 보낸다. room_name 이 없으면
   * 서버가 400 을 돌려주고 pong 을 보내지 않아 매 주기 강제 재연결이 발생한다.
   * 구독 중인 room 이 하나도 없으면 확인할 대상이 없으므로 ping 을 건너뛴다.
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

      // 구독 중인 room 중 하나(대표값)를 ping 에 실어 보낸다.
      const roomName = Array.from(this.rooms)[0];
      if (!roomName) {
        return;
      }

      this.send({
        command: "ping",
        room_name: roomName,
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

    // 재연결 시도 끝에 열린 것인지(=재연결 성공) 판단용.
    const wasReconnecting = this.reconnectAttempts > 0;

    this.connecting = false;

    this.reconnectAttempts = 0;

    this.setConnected(true);

    this.setStatus("open");

    if (wasReconnecting) {
      console.log("[Reconnect] 재연결 성공");
    } else {
      console.log("[Socket] 연결됨(open)");
    }

    if (this.reconnectTimer) {

      clearTimeout(this.reconnectTimer);

      this.reconnectTimer = null;

    }

    this.startHeartbeat();

    //
    // reconnect 후 자동 Room 복구:
    // 재연결되면 서버 입장에서는 새 소켓이므로, 이전에 조인했던 room 을
    // 다시 조인해줘야 응답을 계속 받을 수 있다.
    //
    this.rooms.forEach((room) => {

      console.log("[Reconnect] Room 재조인", room);

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

      console.log("[Socket] 연결 종료(manual)");

      this.setStatus("closed");

      return;

    }

    console.warn("[Socket] 연결 끊김 → 재연결 예약");

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