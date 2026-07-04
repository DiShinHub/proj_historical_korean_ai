import { httpClient } from "./client";
import type { ResultVo } from "./types";

/**
 * POST /na/prompts/ — enqueues the LLM task (Redis list "LBS_001").
 * Returns an immediate ack only; the assistant result is delivered
 * asynchronously via the socket, keyed by `room_name`.
 *
 * Convention (see backend checkpoint #4): room_name === chat_session_seq.
 */
export async function sendPrompt(
  prompt: string,
  roomName: string
): Promise<void> {
  await httpClient.post<ResultVo>("/api/v1/na/prompts/", {
    prompt,
    room_name: roomName,
  });
}
