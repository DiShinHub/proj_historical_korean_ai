// Shared API DTOs. Field names/casing mirror the backend exactly.

/** Standard response envelope (app/model/vo/result_vo.py). */
export interface ResultVo<T = unknown> {
  success: boolean;
  message: string | null;
  data: T | null;
}

export interface ListResult<T> {
  data_list: T[];
}

/** GET /au/chat/chat_session/my-list item (snake_case). */
export interface ChatSessionDto {
  seq: number;
  title: string;
  member_seq: number;
  reg_dt: string;
}

export type MessageRole = "USER" | "ASSISTANT" | (string & {});

/** GET /au/chat/chat_message/list item (snake_case). */
export interface ChatMessageDto {
  seq: number;
  role: MessageRole;
  content: string;
  reg_dt: string;
}

/** GET /au/users/me (camelCase, by_alias). */
export interface MeDto {
  memberSeq: number;
  memberId: string;
  memberTypeCd: string;
}

export interface ApiError {
  status?: number;
  message: string;
  data?: unknown;
}
