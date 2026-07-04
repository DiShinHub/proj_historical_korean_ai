import { BaseChatSocket } from "./BaseChatSocket";
import type { OutboundCommand, ServerEnvelope } from "./types";

const MAX_BACKOFF_MS = 15_000;
const BASE_BACKOFF_MS = 500;

/**
 * WebSocket client for the (assumed) browser-facing bridge — see checkpoint #1.
 *
 * Responsibilities required by the brief §4.1:
 *  - subscribe/unsubscribe to a room (session) channel
 *  - auto-reconnect with exponential backoff
 *  - re-subscribe all rooms after a reconnect
 *  - clean teardown on disconnect
 */
export class RealChatSocket extends BaseChatSocket {
  private ws: WebSocket | null = null;
  private manualClose = false;
  private retries = 0;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(private readonly url: string) {
    super();
  }

  connect(): void {
    if (typeof window === "undefined") return; // SSR guard
    if (
      this.ws &&
      (this.ws.readyState === WebSocket.OPEN ||
        this.ws.readyState === WebSocket.CONNECTING)
    ) {
      return;
    }
    this.manualClose = false;
    this.setStatus(this.retries > 0 ? "reconnecting" : "connecting");

    try {
      this.ws = new WebSocket(this.url);
    } catch {
      this.scheduleReconnect();
      return;
    }

    this.ws.onopen = () => {
      this.retries = 0;
      this.setStatus("open");
      // Re-subscribe every room after (re)connect.
      this.rooms.forEach((room) =>
        this.send({ command: "join_room", room_name: room })
      );
    };

    this.ws.onmessage = (event) => {
      let envelope: ServerEnvelope;
      try {
        envelope = JSON.parse(event.data);
      } catch {
        return; // ignore non-JSON frames (e.g. handshake acks)
      }
      this.dispatchEnvelope(envelope);
    };

    this.ws.onerror = () => {
      this.setStatus("error");
    };

    this.ws.onclose = () => {
      this.ws = null;
      if (this.manualClose) {
        this.setStatus("closed");
        return;
      }
      this.scheduleReconnect();
    };
  }

  disconnect(): void {
    this.manualClose = true;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.rooms.clear();
    this.ws?.close();
    this.ws = null;
    this.setStatus("closed");
  }

  subscribe(roomName: string): void {
    if (!roomName) return;
    this.rooms.add(roomName);
    this.send({ command: "join_room", room_name: roomName });
  }

  unsubscribe(roomName: string): void {
    if (!roomName) return;
    this.rooms.delete(roomName);
    this.send({ command: "leave_room", room_name: roomName });
  }

  private send(command: OutboundCommand): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(command));
    }
    // If not open yet, onopen re-subscribes from `this.rooms`.
  }

  private scheduleReconnect(): void {
    if (this.manualClose) return;
    this.setStatus("reconnecting");
    const delay = Math.min(
      BASE_BACKOFF_MS * 2 ** this.retries,
      MAX_BACKOFF_MS
    );
    this.retries += 1;
    this.reconnectTimer = setTimeout(() => this.connect(), delay);
  }
}
