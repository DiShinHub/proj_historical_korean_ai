import { env } from "@/config/env";
import { MockChatSocket } from "./MockChatSocket";
import { RealChatSocket } from "./RealChatSocket";
import type { IChatSocket } from "./types";

let instance: IChatSocket | null = null;

/** Singleton chat socket — mock or real depending on env.useMockSocket. */
export function getChatSocket(): IChatSocket {
  if (!instance) {
    instance = env.useMockSocket
      ? new MockChatSocket()
      : new RealChatSocket(env.wsUrl);
  }
  return instance;
}

export * from "./types";
export { mockBus } from "./mockBus";
