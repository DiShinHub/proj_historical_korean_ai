import { useEffect, useState } from "react";
import styles from "@/styles/Dictionary.module.css";
import DateRangeBar from "./DateRangeBar";
import FilterSupportBadge from "./FilterSupportBadge";
import {
  SEARCH_CONDITIONS,
  SORTABLE_FIELDS,
  getSearchConditionMeta,
} from "@/lib/dictionary/fields";
import type {
  DictionaryFilterState,
  DictionarySortState,
} from "@/hooks/useDictionaryList";
import type {
  DictionaryFieldKey,
  SearchConditionKey,
} from "@/lib/dictionary/fields";

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
 * 검색 조건은 4개(현대어 / 고어 / 시대 기간 / 검수 여부) 중 여러 개를 동시에
 * 체크할 수 있다(다중 선택, AND 결합). 체크된 조건마다 입력 UI가 함께 표시된다.
 * 정렬은 별도로, 7개 필드 중에서 고른다(fields.ts 의 SORTABLE_FIELDS 기준).
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

  const toggleCondition = (key: SearchConditionKey) => {
    setDraft((prev) => {
      const active = prev.conditions.includes(key);
      const conditions = active
        ? prev.conditions.filter((k) => k !== key)
        : [...prev.conditions, key];
      return { ...prev, conditions };
    });
  };

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("[dictionary] filter submit", draft);
    onApply(draft);
  };

  return (
    <form className={styles.panel} onSubmit={submit}>
      <div className={styles.panelHead}>
        <span className={styles.panelTitle}>조회 조건</span>
      </div>

      <div className={styles.panelBody}>
        {/* ── 검색 조건(다중 선택) ─────────────────────────────────── */}
        <div className={styles.searchBar}>
          {SEARCH_CONDITIONS.map((cond) => (
            <label key={cond.key} className={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={draft.conditions.includes(cond.key)}
                onChange={() => toggleCondition(cond.key)}
              />
              {cond.label}
            </label>
          ))}

          <span className={styles.panelSpacer} />

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

        {/* ── 체크된 조건마다 입력 UI를 함께 노출한다 ───────────────── */}
        {draft.conditions.length > 0 ? (
          <div className={styles.filterGrid} style={{ marginTop: 12 }}>
            {draft.conditions.includes("modern_korean") ? (
              <ConditionField conditionKey="modern_korean">
                <input
                  className={styles.input}
                  value={draft.modern_korean}
                  placeholder="현대어 부분 일치 검색 (예: 사랑)"
                  onChange={(e) => patch({ modern_korean: e.target.value })}
                />
              </ConditionField>
            ) : null}

            {draft.conditions.includes("historical_korean") ? (
              <ConditionField conditionKey="historical_korean">
                <input
                  className={styles.input}
                  value={draft.historical_korean}
                  placeholder="고어 부분 일치 검색 (예: 괴다)"
                  onChange={(e) => patch({ historical_korean: e.target.value })}
                />
              </ConditionField>
            ) : null}

            {draft.conditions.includes("period") ? (
              <ConditionField conditionKey="period" wide>
                <DateRangeBar
                  start={draft.periodStart}
                  end={draft.periodEnd}
                  onChange={(periodStart, periodEnd) =>
                    patch({ periodStart, periodEnd })
                  }
                />
              </ConditionField>
            ) : null}

            {draft.conditions.includes("confirmed_yn") ? (
              <ConditionField conditionKey="confirmed_yn">
                <select
                  className={styles.select}
                  value={draft.confirmed_yn}
                  onChange={(e) => patch({ confirmed_yn: e.target.value })}
                >
                  <option value="">전체</option>
                  <option value="Y">검수 완료 (Y)</option>
                  <option value="N">미검수 (N)</option>
                </select>
              </ConditionField>
            ) : null}
          </div>
        ) : null}

        {/* ── 정렬 기준 / 방향 ──────────────────────────────────────── */}
        <div className={styles.filterGrid} style={{ marginTop: 16 }}>
          <div className={styles.field}>
            <div className={styles.fieldLabelRow}>
              <label className={styles.fieldLabel} htmlFor="f-order-by">
                정렬 기준
              </label>
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
      </div>
    </form>
  );
}

/** 체크된 검색 조건 1개의 입력 필드 + 서버/클라이언트 필터 배지. */
function ConditionField({
  conditionKey,
  wide,
  children,
}: {
  conditionKey: SearchConditionKey;
  wide?: boolean;
  children: React.ReactNode;
}) {
  const meta = getSearchConditionMeta(conditionKey);

  return (
    <div className={`${styles.field} ${wide ? styles.fieldWide : ""}`}>
      <div className={styles.fieldLabelRow}>
        <span className={styles.fieldLabel}>{meta.label}</span>
        <FilterSupportBadge support={meta.support} />
      </div>
      {children}
      {meta.hint ? (
        <span className={styles.fieldHint}>{meta.hint}</span>
      ) : null}
    </div>
  );
}
