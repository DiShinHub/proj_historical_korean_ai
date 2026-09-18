import { httpClient, unwrap } from "./client";
import type { ResultVo } from "./types";

/**
 * 고어 사전(hk_dictionary) API 클라이언트.
 *
 * 백엔드 라우터: app/handler/api/v1/au/hk_dictionary/hk_dictionary_handler.py
 *   POST   /api/v1/au/hk_dictionary          등록      → { seq }
 *   GET    /api/v1/au/hk_dictionary/{seq}    단건 조회
 *   GET    /api/v1/au/hk_dictionary          목록 조회 (검색/정렬/페이징)
 *   PUT    /api/v1/au/hk_dictionary/{seq}    수정
 *   DELETE /api/v1/au/hk_dictionary/{seq}    삭제 (Soft Delete: delete_yn='Y')
 *   POST   /api/v1/au/hk_dictionary/dump     원문 일괄 적재(비동기 · 소켓으로 결과 통보)
 *   PUT    /api/v1/au/hk_dictionary/confirms 일괄 검수(confirmed_yn 일괄 반영)
 *
 * ⚠️ /dump 를 제외한 나머지는 응답이 동기적으로 확정된다.
 *    /dump 는 Redis 큐(TSK_002)에 태스크만 밀어 넣고 즉시 success 를 반환하며,
 *    실제 처리 결과는 WebSocket room 으로 브로드캐스트된다.
 */

const BASE = "/api/v1/au/hk_dictionary";

/** 목록/단건 응답 아이템. 목록 응답에는 일부 필드가 빠져 있어 optional 로 둔다. */
export interface HkDictionaryDto {
  seq: number;
  modern_korean: string;
  historical_korean: string;
  historical_period_start_dt: string | null;
  historical_period_end_dt: string | null;
  reg_dt?: string | null;
  /** 단건 조회에서만 내려온다. */
  reg_member_seq?: number | null;
  mod_dt?: string | null;
  mod_member_seq?: number | null;
  /** 현재 백엔드는 목록/단건 모두에서 내려주지 않는다(노트 §2). */
  confirmed_yn?: string | null;
}

export interface HkDictionaryListResult {
  total_cnt: number;
  page: number;
  page_size: number;
  data_list: HkDictionaryDto[];
}

export interface HkDictionaryListQuery {
  /** 현대어 부분 일치 */
  modern_korean?: string;
  historical_korean?: string;
  /** ISO(+09:00) 문자열 */
  historical_period_start_dt?: string;
  historical_period_end_dt?: string;
  confirmed_yn?: string;
  order_by?: string;
  order_direction?: "asc" | "desc";
  page?: number;
  page_size?: number;
}

export interface HkDictionaryWritePayload {
  modern_korean: string;
  historical_korean: string;
  historical_period_start_dt?: string;
  historical_period_end_dt?: string;
  /** PUT 에서만 반영된다(POST 는 서버가 'Y' 로 강제). */
  confirmed_yn?: string;
}

export interface HkDictionaryDumpPayload {
  raw_text: string;
  historical_period_start_dt?: string;
  historical_period_end_dt?: string;
  /** 결과를 브로드캐스트할 소켓 room. 전 사용자 공용 room 을 쓴다. */
  room_name: string;
}

/** GET /au/hk_dictionary */
export async function listDictionary(
  query: HkDictionaryListQuery
): Promise<HkDictionaryListResult> {
  const res = await httpClient.get<ResultVo<HkDictionaryListResult>>(BASE, {
    // undefined 값은 axios 가 쿼리스트링에서 자동으로 제외한다.
    params: {
      modern_korean: query.modern_korean || undefined,
      historical_korean: query.historical_korean || undefined,
      historical_period_start_dt: query.historical_period_start_dt || undefined,
      historical_period_end_dt: query.historical_period_end_dt || undefined,
      confirmed_yn: query.confirmed_yn || undefined,
      order_by: query.order_by ?? "seq",
      order_direction: query.order_direction ?? "desc",
      page: query.page ?? 1,
      page_size: query.page_size ?? 20,
    },
  });

  const data = unwrap(res);
  return {
    total_cnt: data?.total_cnt ?? 0,
    page: data?.page ?? query.page ?? 1,
    page_size: data?.page_size ?? query.page_size ?? 20,
    data_list: data?.data_list ?? [],
  };
}

/** GET /au/hk_dictionary/{seq} */
export async function getDictionary(seq: number): Promise<HkDictionaryDto> {
  const res = await httpClient.get<ResultVo<HkDictionaryDto>>(`${BASE}/hk_dictionary-seq/${seq}`);
  return unwrap(res);
}

/** POST /au/hk_dictionary → 생성된 seq */
export async function createDictionary(
  payload: HkDictionaryWritePayload
): Promise<number> {
  const res = await httpClient.post<ResultVo<{ seq: number }>>(BASE, payload);
  return unwrap(res)?.seq;
}

/**
 * PUT /au/hk_dictionary/{seq}
 * 백엔드는 null/undefined 가 아닌 화이트리스트 필드만 반영한다.
 */
export async function updateDictionary(
  seq: number,
  payload: HkDictionaryWritePayload
): Promise<void> {
  await httpClient.put<ResultVo>(`${BASE}/hk_dictionary-seq/${seq}`, payload);
}

/** DELETE /au/hk_dictionary/{seq} — Soft Delete(delete_yn='Y') */
export async function deleteDictionary(seq: number): Promise<void> {
  await httpClient.delete<ResultVo>(`${BASE}/hk_dictionary-seq/${seq}`);
}

/**
 * POST /au/hk_dictionary/dump
 *
 * 큐 적재까지만 동기 응답. 실제 적재 건수/성공 여부는
 * room_name 으로 지정한 소켓 room 에 { result, llm_msg, items_cnt } 로 통보된다.
 */
export async function dumpRawDictionary(
  payload: HkDictionaryDumpPayload
): Promise<void> {
  await httpClient.post<ResultVo>(`${BASE}/dump`, payload);
}

export interface HkDictionaryConfirmsPayload {
  seqs: number[];
  /** 기본값 'Y'(백엔드가 미전달 시 채움). 명시적으로 'N' 을 보낼 수도 있다. */
  confirmed_yn?: "Y" | "N";
}

/**
 * PUT /au/hk_dictionary/confirms — 여러 항목의 confirmed_yn 을 한 번에 반영.
 * 백엔드 계약(hk_dictionary_service.confirms_hk_dictionary): { seqs, confirmed_yn }
 */
export async function confirmDictionaries(
  payload: HkDictionaryConfirmsPayload
): Promise<void> {
  await httpClient.put<ResultVo>(`${BASE}/confirms`, payload);
}

// ────────────────────────────────────────────────────────────────────────────
// 파일 일괄 업로드 (프론트 전용 · 백엔드 미구현)
// ────────────────────────────────────────────────────────────────────────────

/** 파일 업로드 API 가 아직 없다는 것을 호출부가 구분할 수 있게 하는 에러 타입. */
export class BackendNotImplementedError extends Error {
  readonly endpoint: string;

  constructor(endpoint: string) {
    super(`백엔드 API 미구현: ${endpoint}`);
    this.name = "BackendNotImplementedError";
    this.endpoint = endpoint;
  }
}

/** 프론트가 기대하는 파일 업로드 엔드포인트(제안). 노트 §4 참고. */
export const DICTIONARY_UPLOAD_ENDPOINT = `${BASE}/dump/file`;

export interface HkDictionaryFileUploadPayload {
  files: File[];
  historical_period_start_dt?: string;
  historical_period_end_dt?: string;
  room_name: string;
}

/**
 * POST /au/hk_dictionary/dump/file (multipart/form-data) — **미구현 스텁**.
 *
 * 백엔드가 아직 없으므로 실제 요청을 보내지 않고 즉시 실패시킨다.
 * (요구사항 4-B "파일 업로드는 프론트만 구현")
 * 백엔드가 준비되면 아래 주석 블록의 구현으로 교체하면 된다.
 */
export async function uploadDictionaryFiles(
  payload: HkDictionaryFileUploadPayload
): Promise<never> {
  // ── 백엔드 준비 후 사용할 실제 구현 ──────────────────────────────
  // const form = new FormData();
  // payload.files.forEach((file) => form.append("files", file));
  // if (payload.historical_period_start_dt)
  //   form.append("historical_period_start_dt", payload.historical_period_start_dt);
  // if (payload.historical_period_end_dt)
  //   form.append("historical_period_end_dt", payload.historical_period_end_dt);
  // form.append("room_name", payload.room_name);
  // await httpClient.post<ResultVo>(DICTIONARY_UPLOAD_ENDPOINT, form, {
  //   headers: { "Content-Type": "multipart/form-data" },
  // });
  // ────────────────────────────────────────────────────────────────
  throw new BackendNotImplementedError(DICTIONARY_UPLOAD_ENDPOINT);
}
