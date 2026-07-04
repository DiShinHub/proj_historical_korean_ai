import { BaseChatSocket } from "./BaseChatSocket";
import { mockBus, type MockPromptEvent } from "./mockBus";
import type { ServerEnvelope } from "./types";

/**
 * Development-only socket. Simulates the full async loop the backend cannot yet
 * deliver (checkpoints #1 & #2): listens for prompts sent through the HTTP
 * layer and streams back a canned historical-Korean-translation response so the
 * optimistic -> typing -> progressive-render UX can be exercised end to end.
 */
export class MockChatSocket extends BaseChatSocket {
  private unbind: (() => void) | null = null;
  private timers = new Set<ReturnType<typeof setTimeout>>();

  connect(): void {
    if (this.unbind) return;
    this.setStatus("open");
    this.unbind = mockBus.onPrompt((e) => this.handlePrompt(e));
  }

  disconnect(): void {
    this.unbind?.();
    this.unbind = null;
    this.timers.forEach(clearTimeout);
    this.timers.clear();
    this.rooms.clear();
    this.setStatus("closed");
  }

  subscribe(roomName: string): void {
    if (roomName) this.rooms.add(roomName);
  }

  unsubscribe(roomName: string): void {
    this.rooms.delete(roomName);
  }

  private handlePrompt({ roomName, prompt }: MockPromptEvent): void {
    if (!this.rooms.has(roomName)) return;

    const reply = buildMockReply(prompt);
    const chunks = chunkText(reply);

    // Stream chunks with small delays, then a final "done" frame.
    let elapsed = 500;
    chunks.forEach((chunk, i) => {
      elapsed += 120 + chunk.length * 12;
      this.after(elapsed, () =>
        this.emit(roomName, { text: chunk, done: false })
      );
      if (i === chunks.length - 1) {
        this.after(elapsed + 150, () => this.emit(roomName, { done: true }));
      }
    });
  }

  private emit(
    roomName: string,
    llm: { text?: string; done?: boolean; audio_url?: string }
  ): void {
    const envelope: ServerEnvelope = {
      message: "테스크 처리에 성공하였습니다",
      response_code: 200,
      client_data: {
        command: "emit_to_room_connectionless",
        room_name: roomName,
        llm_response: { room_name: roomName, ...llm },
      },
    };
    this.dispatchEnvelope(envelope);
  }

  private after(ms: number, fn: () => void): void {
    const t = setTimeout(() => {
      this.timers.delete(t);
      fn();
    }, ms);
    this.timers.add(t);
  }
}

function chunkText(text: string): string[] {
  // Split into word-ish chunks to mimic token streaming.
  return text.match(/(\S+\s*|\n)/g) ?? [text];
}

function buildMockReply(prompt: string): string {
  const quoted = prompt.trim().slice(0, 40);
  return [
    `## 번역 결과`,
    ``,
    `입력하신 **"${quoted}"** 을(를) 중세 국어 표기로 옮기면 다음과 같습니다.`,
    ``,
    `> 平安ᄒᆞ신잇가?`,
    ``,
    `### 형태소 분석`,
    ``,
    "| 현대어 | 중세국어 | 비고 |",
    "| --- | --- | --- |",
    "| 안녕 | 平安(평안) | 한자어 차용 |",
    "| 하십니까 | ᄒᆞ신잇가 | 객체 높임 |",
    ``,
    "```text",
    "平安ᄒᆞ신잇가?",
    "```",
    ``,
    `_※ 본 응답은 개발용 목(mock)입니다. 실제 LLM 연동은 백엔드 체크포인트 #2 참고._`,
  ].join("\n");
}
