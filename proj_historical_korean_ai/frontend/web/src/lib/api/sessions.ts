import { httpClient, unwrap } from "./client";
import type { ChatSessionDto, ListResult, ResultVo } from "./types";

const BASE = "/api/v1/au/chat/chat_session";

/** GET /au/chat/chat_session/my-list */
export async function listSessions(
  page = 1,
  pageSize = 50
): Promise<ChatSessionDto[]> {
  const res = await httpClient.get<ResultVo<ListResult<ChatSessionDto>>>(
    `${BASE}/my-list`,
    { params: { page, page_size: pageSize } }
  );
  return unwrap(res)?.data_list ?? [];
}

/** POST /au/chat/chat_session -> { chat_session_seq } */
export async function createSession(title: string): Promise<number> {
  const res = await httpClient.post<ResultVo<{ chat_session_seq: number }>>(
    BASE,
    { title }
  );
  return unwrap(res).chat_session_seq;
}

/**
 * PUT /au/chat/chat_session/chat_session_seq/{seq}
 * 수정 가능 필드: title, status("active"|"inactive"), activate_dt(ISO 문자열).
 * (백엔드 put_chat_session 이 이 세 필드만 화이트리스트로 반영한다.)
 */
export async function updateSession(
  seq: number,
  patch: { title?: string; status?: string; activate_dt?: string }
): Promise<void> {
  await httpClient.put(`${BASE}/chat_session_seq/${seq}`, patch);
}

/** DELETE /au/chat/chat_session/chat_session_seq/{seq} (soft delete) */
export async function deleteSession(seq: number): Promise<void> {
  await httpClient.delete(`${BASE}/chat_session_seq/${seq}`);
}
