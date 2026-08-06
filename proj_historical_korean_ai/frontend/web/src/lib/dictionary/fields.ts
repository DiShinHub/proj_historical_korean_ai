/**
 * hk_dictionary 엔티티 필드 메타데이터.
 *
 * 요구사항: delete_yn 을 제외한 모든 Entity Key 에 대해 필터링/정렬을 지원한다.
 *
 * 현재 백엔드 실제 지원 범위(app/dao/hk_dictionary_dao.py 기준):
 *  - 정렬  : `order_by` 가 getattr(Entity, order_by) 로 동적 처리되므로 전 컬럼 가능.
 *  - 필터  : modern_korean(LIKE) + historical_period_start/end_dt(범위) 만 가능.
 *  - 목록 응답 필드 : seq / modern_korean / historical_korean /
 *                     historical_period_start_dt / historical_period_end_dt / reg_dt
 *
 * 그래서 필터는 3단계로 구분한다.
 *  - "server"      : 서버 쿼리 파라미터로 전달된다(전체 데이터 기준 필터).
 *  - "client"      : 서버 미지원이지만 목록 응답에 값이 있어 현재 페이지 한정으로 거를 수 있다.
 *  - "unavailable" : 서버도 미지원이고 목록 응답에도 값이 없어 필터가 불가능하다.
 *
 * "client"/"unavailable" 을 없애려면 백엔드 확장이 필요하다.
 * → BACKEND_MODIFICATION_NOTES.md §1, §2 참고.
 */

export type DictionaryFieldKey =
  | "seq"
  | "modern_korean"
  | "historical_korean"
  | "historical_period_start_dt"
  | "historical_period_end_dt"
  | "reg_dt"
  | "reg_member_seq"
  | "mod_dt"
  | "mod_member_seq"
  | "confirmed_yn";

export type FilterSupport = "server" | "client" | "unavailable";

export type FieldInputType = "number" | "text" | "date-range" | "yn";

export interface DictionaryFieldMeta {
  key: DictionaryFieldKey;
  label: string;
  type: FieldInputType;
  /** 필터 지원 수준 */
  filter: FilterSupport;
  /** 목록 API 응답에 포함되는가 */
  inList: boolean;
  /** 필터 UI 에 노출할 보조 설명 */
  hint?: string;
}

export const DICTIONARY_FIELDS: DictionaryFieldMeta[] = [
  {
    key: "seq",
    label: "번호(seq)",
    type: "number",
    filter: "client",
    inList: true,
    hint: "서버 필터 미지원 · 현재 페이지 내에서만 적용",
  },
  {
    key: "modern_korean",
    label: "현대어",
    type: "text",
    filter: "server",
    inList: true,
    hint: "부분 일치(LIKE)",
  },
  {
    key: "historical_korean",
    label: "고어",
    type: "text",
    filter: "client",
    inList: true,
    hint: "서버 필터 미지원 · 현재 페이지 내에서만 적용",
  },
  {
    key: "historical_period_start_dt",
    label: "시대 시작일",
    type: "date-range",
    filter: "server",
    inList: true,
    hint: "기간 바에서 함께 지정",
  },
  {
    key: "historical_period_end_dt",
    label: "시대 종료일",
    type: "date-range",
    filter: "server",
    inList: true,
    hint: "기간 바에서 함께 지정",
  },
  {
    key: "reg_dt",
    label: "등록일시",
    type: "date-range",
    filter: "client",
    inList: true,
    hint: "서버 필터 미지원 · 현재 페이지 내에서만 적용",
  },
  {
    key: "reg_member_seq",
    label: "등록자",
    type: "number",
    filter: "unavailable",
    inList: false,
    hint: "목록 응답에 없음 · 정렬만 가능",
  },
  {
    key: "mod_dt",
    label: "수정일시",
    type: "date-range",
    filter: "unavailable",
    inList: false,
    hint: "목록 응답에 없음 · 정렬만 가능",
  },
  {
    key: "mod_member_seq",
    label: "수정자",
    type: "number",
    filter: "unavailable",
    inList: false,
    hint: "목록 응답에 없음 · 정렬만 가능",
  },
  {
    key: "confirmed_yn",
    label: "검수여부",
    type: "yn",
    filter: "unavailable",
    inList: false,
    hint: "목록 응답에 없음 · 정렬만 가능",
  },
];

/** 정렬은 전 컬럼 서버 지원. 셀렉트 박스 옵션으로 그대로 쓴다. */
export const SORTABLE_FIELDS = DICTIONARY_FIELDS;

export function getFieldMeta(key: DictionaryFieldKey): DictionaryFieldMeta {
  const found = DICTIONARY_FIELDS.find((f) => f.key === key);
  if (!found) {
    throw new Error(`unknown dictionary field: ${key}`);
  }
  return found;
}

/** 시대 기간 빠른 선택 프리셋. (start, end 는 "YYYY-MM-DD") */
export interface PeriodPreset {
  label: string;
  start: string;
  end: string;
}

export const PERIOD_PRESETS: PeriodPreset[] = [
  { label: "훈민정음~갑오개혁", start: "1446-10-09", end: "1894-12-31" },
  { label: "조선 전기", start: "1392-07-17", end: "1592-04-12" },
  { label: "조선 후기", start: "1592-04-13", end: "1897-10-11" },
  { label: "대한제국", start: "1897-10-12", end: "1910-08-29" },
  { label: "근대 국어", start: "1600-01-01", end: "1894-12-31" },
];
