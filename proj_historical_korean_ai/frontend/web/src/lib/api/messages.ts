import { httpClient, unwrap } from "./client";
import type { ChatMessageDto, ListResult, ResultVo } from "./types";

const BASE = "/api/v1/au/chat/chat_message";

/** GET /au/chat/chat_message/list?chat_session_seq= */
export async function listMessages(
  sessionSeq: number,
  page = 1,
  pageSize = 100
): Promise<ChatMessageDto[]> {
  const res = await httpClient.get<ResultVo<ListResult<ChatMessageDto>>>(
    `${BASE}/list`,
    { params: { chat_session_seq: sessionSeq, page, page_size: pageSize } }
  );
  return unwrap(res)?.data_list ?? [];
}

/** POST /au/chat/chat_message -> { chat_message_seq }. Role is forced to USER. */
export async function createMessage(
  sessionSeq: number,
  content: string
): Promise<number | null> {
  const res = await httpClient.post<ResultVo<{ chat_message_seq: number | null }>>(
    BASE,
    { chat_session_seq: sessionSeq, content }
  );
  return unwrap(res)?.chat_message_seq ?? null;
}

/** PUT /au/chat/chat_message/chat_message_seq/{seq} */
export async function updateMessage(
  seq: number,
  patch: { content?: string; feedback_type?: string; feedback_comment?: string }
): Promise<void> {
  await httpClient.put(`${BASE}/chat_message_seq/${seq}`, patch);
}
