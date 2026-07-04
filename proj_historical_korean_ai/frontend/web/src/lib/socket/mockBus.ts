// A tiny in-process bus so the mock socket can "hear" prompts that were sent
// through the HTTP layer and reply with a simulated assistant response.
// Used only when env.useMockSocket is true.

export interface MockPromptEvent {
  roomName: string;
  prompt: string;
}

type Listener = (event: MockPromptEvent) => void;

const listeners = new Set<Listener>();

export const mockBus = {
  emitPrompt(roomName: string, prompt: string): void {
    listeners.forEach((l) => l({ roomName, prompt }));
  },
  onPrompt(listener: Listener): () => void {
    listeners.add(listener);
    return () => listeners.delete(listener);
  },
};
