/**
 * hk_dictionary 엔티티 필드 메타데이터.
 *
 * 검색(조회) 조건은 정확히 4개만 제공한다: 현대어 / 고어 / 시대 기간 / 검수 여부.
 * 정렬(sort) 조건은 정확히 7개만 제공한다: 번호 / 현대어 / 고어 / 시대 시작일 /
 * 시대 종료일 / 등록일시 / 검수 여부.
 *
 * 현재 백엔드 실제 지원 범위(app/handler/api/v1/au/hk_dictionary 기준):
 *  - 정렬  : `order_by` 가 getattr(Entity, order_by) 로 동적 처리되므로 전 컬럼 가능.
 *  - 필터  : modern_korean(LIKE) + historical_period_start/end_dt(범위) 만 쿼리 파라미터로 지원.
 *  - 목록 응답 필드 : seq / modern_korean / historical_korean /
 *                     historical_period_start_dt / historical_period_end_dt /
 *                     reg_dt / mod_dt / confirmed_yn
 *
 * 고어 / 검수 여부는 서버가 쿼리 파라미터로 받지 않으므로, 응답에 값은 있지만
 * **현재 페이지에 한해서만** 클라이언트에서 거른다(fields.ts 의 `filter` 메타데이터 기준).
 * 백엔드 계약을 바꾸지 않는 한 전체 데이터 기준 검색으로 확장할 수 없다
 * (BACKEND_MODIFICATION_NOTES.md §1 참고).
 */

export type DictionaryFieldKey =
  | "seq"
  | "modern_korean"
  | "historical_korean"
  | "historical_period_start_dt"
  | "historical_period_end_dt"
  | "reg_dt"
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

/** 정렬 셀렉트 박스에 그대로 노출되는 7개 필드(요구사항 §12). */
export const DICTIONARY_FIELDS: DictionaryFieldMeta[] = [
  {
    key: "seq",
    label: "번호",
    type: "number",
    filter: "unavailable",
    inList: true,
    hint: "정렬만 가능 · 검색 조건에서는 제외됨",
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
    filter: "server",
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
    filter: "unavailable",
    inList: true,
    hint: "정렬만 가능 · 검색 조건에서는 제외됨",
  },
  {
    key: "confirmed_yn",
    label: "검수 여부",
    type: "yn",
    filter: "server",
    inList: true,
    hint: "서버 필터 미지원 · 현재 페이지 내에서만 적용",
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

/** 검색 조건 Select 에 노출되는 4개 항목(요구사항 §8). */
export type SearchConditionKey =
  | "modern_korean"
  | "historical_korean"
  | "period"
  | "confirmed_yn";

export interface SearchConditionMeta {
  key: SearchConditionKey;
  label: string;
  support: FilterSupport;
  hint?: string;
}

export const SEARCH_CONDITIONS: SearchConditionMeta[] = [
  {
    key: "modern_korean",
    label: "현대어",
    support: "server",
    hint: "부분 일치 기준 검색",
  },
  {
    key: "historical_korean",
    label: "고어",
    support: "server",
    hint: "부분 일치 기준 검색",
  },
  {
    key: "period",
    label: "시대 기간",
    support: "server",
    hint: "시작일~종료일",
  },
  {
    key: "confirmed_yn",
    label: "검수 여부",
    support: "server",
    hint: "검수/비검수 분류",
  },
];

export function getSearchConditionMeta(
  key: SearchConditionKey
): SearchConditionMeta {
  const found = SEARCH_CONDITIONS.find((c) => c.key === key);
  if (!found) {
    throw new Error(`unknown search condition: ${key}`);
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
