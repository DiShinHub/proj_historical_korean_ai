import { useEffect, useState } from "react";
import styles from "@/styles/Dictionary.module.css";
import DateRangeBar from "./DateRangeBar";
import FilterSupportBadge from "./FilterSupportBadge";
import { getFieldMeta, SORTABLE_FIELDS } from "@/lib/dictionary/fields";
import type {
  DictionaryFilterState,
  DictionarySortState,
} from "@/hooks/useDictionaryList";
import type { DictionaryFieldKey } from "@/lib/dictionary/fields";

interface DictionaryFiltersProps {
  filters: DictionaryFilterState;
  sort: DictionarySortState;
  loading: boolean;
  onApply: (next: DictionaryFilterState) => void;
  onReset: () => void;
  onSortChange: (next: DictionarySortState) => void;
}

/**
 * 조회 필터 패널.
 *
 * delete_yn 을 제외한 전 Entity Key 를 노출하되,
 * 각 항목이 서버 검색인지 / 페이지 내 필터인지 / 필터 불가인지
 * 배지로 명확히 구분해 보여준다(fields.ts 메타데이터 기준).
 */
export default function DictionaryFilters({
  filters,
  sort,
  loading,
  onApply,
  onReset,
  onSortChange,
}: DictionaryFiltersProps) {
  // 입력 중인 값(draft)과 실제 적용된 값(filters)을 분리한다.
  const [draft, setDraft] = useState<DictionaryFilterState>(filters);

  // 외부에서 초기화(resetFilters)되면 draft 도 맞춘다.
  useEffect(() => {
    setDraft(filters);
  }, [filters]);

  const patch = (part: Partial<DictionaryFilterState>) =>
    setDraft((prev) => ({ ...prev, ...part }));

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    onApply(draft);
  };

  const periodMeta = getFieldMeta("historical_period_start_dt");

  return (
    <form className={styles.panel} onSubmit={submit}>
      <div className={styles.panelHead}>
        <span className={styles.panelTitle}>조회 조건</span>
      </div>

      <div className={styles.panelBody}>
        <div className={styles.filterGrid}>
          {/* seq — 서버 미지원(페이지 내) */}
          <div className={styles.field}>
            <div className={styles.fieldLabelRow}>
              <label className={styles.fieldLabel} htmlFor="f-seq">
                {getFieldMeta("seq").label}
              </label>
              <FilterSupportBadge support="client" />
            </div>
            <input
              id="f-seq"
              className={styles.input}
              value={draft.seq}
              inputMode="numeric"
              placeholder="예: 12"
              onChange={(e) =>
                patch({ seq: e.target.value.replace(/[^0-9]/g, "") })
              }
            />
          </div>

          {/* modern_korean — 서버 LIKE */}
          <div className={styles.field}>
            <div className={styles.fieldLabelRow}>
              <label className={styles.fieldLabel} htmlFor="f-modern">
                {getFieldMeta("modern_korean").label}
              </label>
              <FilterSupportBadge support="server" />
            </div>
            <input
              id="f-modern"
              className={styles.input}
              value={draft.modern_korean}
              placeholder="부분 일치 검색 (예: 사랑)"
              onChange={(e) => patch({ modern_korean: e.target.value })}
            />
          </div>

          {/* historical_korean — 서버 미지원(페이지 내) */}
          <div className={styles.field}>
            <div className={styles.fieldLabelRow}>
              <label className={styles.fieldLabel} htmlFor="f-historical">
                {getFieldMeta("historical_korean").label}
              </label>
              <FilterSupportBadge support="client" />
            </div>
            <input
              id="f-historical"
              className={styles.input}
              value={draft.historical_korean}
              placeholder="부분 일치 (예: 괴다)"
              onChange={(e) => patch({ historical_korean: e.target.value })}
            />
          </div>

          {/* historical_period_start_dt ~ historical_period_end_dt — 기간 바 */}
          <div className={`${styles.field} ${styles.fieldWide}`}>
            <div className={styles.fieldLabelRow}>
              <span className={styles.fieldLabel}>시대 기간</span>
              <FilterSupportBadge support="server" />
              <span className={styles.fieldHint}>
                historical_period_start_dt ≥ 시작일 · historical_period_end_dt ≤
                종료일
              </span>
            </div>
            <DateRangeBar
              start={draft.periodStart}
              end={draft.periodEnd}
              onChange={(periodStart, periodEnd) =>
                patch({ periodStart, periodEnd })
              }
            />
            <span className={styles.fieldHint}>{periodMeta.hint}</span>
          </div>

          {/* reg_dt — 서버 미지원(페이지 내) */}
          <div className={`${styles.field} ${styles.fieldWide}`}>
            <div className={styles.fieldLabelRow}>
              <span className={styles.fieldLabel}>
                {getFieldMeta("reg_dt").label}
              </span>
              <FilterSupportBadge support="client" />
            </div>
            <DateRangeBar
              start={draft.regDtFrom}
              end={draft.regDtTo}
              showPresets={false}
              showTimeHint={false}
              onChange={(regDtFrom, regDtTo) => patch({ regDtFrom, regDtTo })}
            />
          </div>

          {/* 필터 불가 필드들 — 정렬만 가능하다는 것을 명시적으로 노출 */}
          <DisabledFilterField fieldKey="reg_member_seq" placeholder="회원 번호" />
          <DisabledFilterField fieldKey="mod_member_seq" placeholder="회원 번호" />
          <DisabledFilterField fieldKey="mod_dt" placeholder="YYYY-MM-DD" />
          <DisabledFilterField fieldKey="confirmed_yn" placeholder="Y / N" />

          {/* 정렬 — 전 필드 서버 지원 */}
          <div className={styles.field}>
            <div className={styles.fieldLabelRow}>
              <label className={styles.fieldLabel} htmlFor="f-order-by">
                정렬 기준
              </label>
              <FilterSupportBadge support="server" />
            </div>
            <select
              id="f-order-by"
              className={styles.select}
              value={sort.orderBy}
              onChange={(e) =>
                onSortChange({
                  ...sort,
                  orderBy: e.target.value as DictionaryFieldKey,
                })
              }
            >
              {SORTABLE_FIELDS.map((field) => (
                <option key={field.key} value={field.key}>
                  {field.label}
                </option>
              ))}
            </select>
          </div>

          <div className={styles.field}>
            <div className={styles.fieldLabelRow}>
              <label className={styles.fieldLabel} htmlFor="f-order-dir">
                정렬 방향
              </label>
            </div>
            <select
              id="f-order-dir"
              className={styles.select}
              value={sort.orderDirection}
              onChange={(e) =>
                onSortChange({
                  ...sort,
                  orderDirection: e.target.value as "asc" | "desc",
                })
              }
            >
              <option value="asc">오름차순 (ASC)</option>
              <option value="desc">내림차순 (DESC)</option>
            </select>
          </div>
        </div>

        <div className={styles.actionRow} style={{ marginTop: 16, marginBottom: 0 }}>
          <button
            type="submit"
            className={`${styles.btn} ${styles.btnPrimary}`}
            disabled={loading}
          >
            {loading ? "조회 중…" : "조회"}
          </button>
          <button
            type="button"
            className={styles.btn}
            onClick={onReset}
            disabled={loading}
          >
            초기화
          </button>
        </div>
      </div>
    </form>
  );
}

/** 백엔드 미지원으로 입력이 막힌 필터 필드. */
function DisabledFilterField({
  fieldKey,
  placeholder,
}: {
  fieldKey: DictionaryFieldKey;
  placeholder: string;
}) {
  const meta = getFieldMeta(fieldKey);

  return (
    <div className={styles.field}>
      <div className={styles.fieldLabelRow}>
        <span className={styles.fieldLabel}>{meta.label}</span>
        <FilterSupportBadge support="unavailable" />
      </div>
      <input
        className={styles.input}
        value=""
        placeholder={placeholder}
        disabled
        readOnly
      />
      <span className={styles.fieldHint}>{meta.hint}</span>
    </div>
  );
}
