/**
 * 고어 사전(hk_dictionary) 전용 날짜 유틸.
 *
 * ⚠️ 왜 Date 객체를 쓰지 않는가
 * 이 화면이 다루는 날짜는 1446-10-09 같은 "역사 시기"다.
 * `new Date("1446-10-09T00:00:00+09:00").toISOString()` 은 UTC 로 변환되면서
 * 1446-10-08 로 하루가 밀린다. 화면 표시/입력값 복원에서 날짜가 틀어지므로
 * 문자열을 정규식으로 직접 잘라 쓴다(타임존 변환을 아예 일으키지 않는다).
 */

/** 백엔드가 예시로 사용하는 고정 오프셋(KST). */
export const KST_OFFSET = "+09:00";

/** "YYYY-MM-DD" 형태인지 검사. */
export function isDateInput(value: string | null | undefined): value is string {
  return !!value && /^\d{4}-\d{2}-\d{2}$/.test(value);
}

/**
 * 기간 시작일 → ISO.
 * UI 는 연-월-일만 받고 시각(00:00:00)은 여기서 자동으로 채운다.
 *   "1446-10-09" → "1446-10-09T00:00:00+09:00"
 */
export function toPeriodStartIso(date: string): string | undefined {
  if (!isDateInput(date)) return undefined;
  return `${date}T00:00:00${KST_OFFSET}`;
}

/**
 * 기간 종료일 → ISO.
 * UI 는 연-월-일만 받고 시각(23:59:59)은 여기서 자동으로 채운다.
 *   "1894-12-31" → "1894-12-31T23:59:59+09:00"
 */
export function toPeriodEndIso(date: string): string | undefined {
  if (!isDateInput(date)) return undefined;
  return `${date}T23:59:59${KST_OFFSET}`;
}

/**
 * /dump 전용 시작일 포맷.
 *
 * ⚠️ CRUD 엔드포인트(ISO+오프셋)와 /dump(공백 구분·오프셋 없음)의 포맷이 다르다.
 *    백엔드 예시 스펙을 그대로 따른다. (BACKEND_MODIFICATION_NOTES.md §5 참고)
 *   "1418-01-01" → "1418-01-01 00:00:00"
 */
export function toDumpStart(date: string): string | undefined {
  if (!isDateInput(date)) return undefined;
  return `${date} 00:00:00`;
}

/** /dump 전용 종료일 포맷. "1618-12-31" → "1618-12-31 23:59:59" */
export function toDumpEnd(date: string): string | undefined {
  if (!isDateInput(date)) return undefined;
  return `${date} 23:59:59`;
}

/** 서버 ISO 문자열 → `<input type="date">` 용 "YYYY-MM-DD". 실패 시 "". */
export function toDateInputValue(iso: string | null | undefined): string {
  if (!iso) return "";
  const matched = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso);
  return matched ? matched[0] : "";
}

/** 서버 ISO 문자열 → 화면 표시용 "YYYY-MM-DD". 값이 없으면 "-". */
export function formatDate(iso: string | null | undefined): string {
  const date = toDateInputValue(iso);
  return date || "-";
}

/** 서버 ISO 문자열 → 화면 표시용 "YYYY-MM-DD HH:mm:ss". 값이 없으면 "-". */
export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return "-";
  const matched = /^(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}:\d{2})/.exec(iso);
  if (!matched) return toDateInputValue(iso) || "-";
  return `${matched[1]} ${matched[2]}`;
}

/**
 * 기간 두 개를 "1446-10-09 ~ 1894-12-31" 형태로 합친다.
 * 한쪽만 있으면 그쪽만 표시한다.
 */
export function formatPeriod(
  start: string | null | undefined,
  end: string | null | undefined
): string {
  const s = toDateInputValue(start);
  const e = toDateInputValue(end);
  if (!s && !e) return "-";
  return `${s || "…"} ~ ${e || "…"}`;
}

/**
 * "YYYY-MM-DD" 문자열은 사전식 비교가 곧 날짜 비교다.
 * (자릿수가 고정이므로 별도 파싱이 필요 없다.)
 */
export function isDateInRange(
  value: string,
  from: string,
  to: string
): boolean {
  if (from && (!value || value < from)) return false;
  if (to && (!value || value > to)) return false;
  return true;
}

/** 현재 시각을 "HH:mm:ss" 로. (작업 로그 타임스탬프용) */
export function nowClock(): string {
  const now = new Date();
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(
    now.getSeconds()
  )}`;
}
