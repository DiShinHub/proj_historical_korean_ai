import { env } from "@/config/env";
import { RealChatSocket } from "./RealChatSocket";
import type { IChatSocket } from "./types";

let socketInstance: IChatSocket | null = null;

export function getChatSocket(): IChatSocket {
  if (!socketInstance) {
    socketInstance = new RealChatSocket(env.wsUrl)
  }

  return socketInstance;
}

export * from "./types";