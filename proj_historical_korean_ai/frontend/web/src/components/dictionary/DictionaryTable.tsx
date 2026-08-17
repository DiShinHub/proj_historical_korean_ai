import styles from "@/styles/Dictionary.module.css";
import { formatDate, formatDateTime } from "@/lib/dictionary/datetime";
import type { HkDictionaryDto } from "@/lib/api/dictionary";
import type { DictionaryFieldKey } from "@/lib/dictionary/fields";
import type { DictionarySortState } from "@/hooks/useDictionaryList";

interface Column {
  key: DictionaryFieldKey;
  label: string;
  align?: "right";
}

/**
 * 목록 응답에 실제로 들어 있는 필드만 컬럼으로 만든다.
 * (reg_member_seq / mod_member_seq 는 목록 API 미제공 → 단건 상세 모달에서 확인한다)
 */
const COLUMNS: Column[] = [
  { key: "seq", label: "번호" },
  { key: "modern_korean", label: "현대어" },
  { key: "historical_korean", label: "고어" },
  { key: "historical_period_start_dt", label: "시대 시작" },
  { key: "historical_period_end_dt", label: "시대 종료" },
  { key: "reg_dt", label: "등록일시" },
  { key: "confirmed_yn", label: "검수 여부" },
];

interface DictionaryTableProps {
  items: HkDictionaryDto[];
  sort: DictionarySortState;
  loading: boolean;
  selectedSeqs: Set<number>;
  onToggleSort: (key: DictionaryFieldKey) => void;
  onToggleSelect: (seq: number) => void;
  onToggleSelectAll: () => void;
  onView: (item: HkDictionaryDto) => void;
  onEdit: (item: HkDictionaryDto) => void;
  onDelete: (item: HkDictionaryDto) => void;
}

export default function DictionaryTable({
  items,
  sort,
  loading,
  selectedSeqs,
  onToggleSort,
  onToggleSelect,
  onToggleSelectAll,
  onView,
  onEdit,
  onDelete,
}: DictionaryTableProps) {
  const allSelected =
    items.length > 0 && items.every((item) => selectedSeqs.has(item.seq));

  return (
    <div className={styles.tableWrap}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th scope="col">
              <div className={styles.thStatic}>
                <input
                  type="checkbox"
                  aria-label="전체 선택"
                  checked={allSelected}
                  onChange={onToggleSelectAll}
                  disabled={items.length === 0}
                />
              </div>
            </th>
            {COLUMNS.map((col) => {
              const active = sort.orderBy === col.key;
              const mark = !active ? "↕" : sort.orderDirection === "asc" ? "▲" : "▼";
              return (
                <th key={col.key} scope="col">
                  <button
                    type="button"
                    className={styles.thButton}
                    onClick={() => onToggleSort(col.key)}
                    title={`${col.label} 기준 정렬`}
                  >
                    {col.label}
                    <span
                      className={`${styles.sortMark} ${
                        active ? styles.sortMarkActive : ""
                      }`}
                      aria-hidden
                    >
                      {mark}
                    </span>
                  </button>
                </th>
              );
            })}
            <th scope="col">
              <div className={styles.thStatic} style={{ textAlign: "right" }}>
                관리
              </div>
            </th>
          </tr>
        </thead>

        <tbody>
          {loading && items.length === 0 ? (
            <tr>
              <td className={styles.emptyRow} colSpan={COLUMNS.length + 2}>
                불러오는 중…
              </td>
            </tr>
          ) : null}

          {!loading && items.length === 0 ? (
            <tr>
              <td className={styles.emptyRow} colSpan={COLUMNS.length + 2}>
                조회된 사전 항목이 없습니다.
              </td>
            </tr>
          ) : null}

          {items.map((item) => (
            <tr key={item.seq}>
              <td>
                <input
                  type="checkbox"
                  aria-label={`#${item.seq} 선택`}
                  checked={selectedSeqs.has(item.seq)}
                  onChange={() => onToggleSelect(item.seq)}
                />
              </td>
              <td className={styles.cellNum}>{item.seq}</td>
              <td className={styles.cellWord}>{item.modern_korean}</td>
              <td className={styles.cellHistorical}>{item.historical_korean}</td>
              <td className={styles.cellPeriod}>
                {formatDate(item.historical_period_start_dt)}
              </td>
              <td className={styles.cellPeriod}>
                {formatDate(item.historical_period_end_dt)}
              </td>
              <td className={styles.cellDt}>{formatDateTime(item.reg_dt)}</td>
              <td>
                <span
                  className={
                    item.confirmed_yn === "Y"
                      ? styles.badgeConfirmedY
                      : styles.badgeConfirmedN
                  }
                >
                  {item.confirmed_yn === "Y" ? "검수 완료" : "미검수"}
                </span>
              </td>
              <td>
                <div className={styles.rowActions}>
                  <button
                    type="button"
                    className={`${styles.btn} ${styles.btnSmall}`}
                    onClick={() => onView(item)}
                  >
                    상세
                  </button>
                  <button
                    type="button"
                    className={`${styles.btn} ${styles.btnSmall}`}
                    onClick={() => onEdit(item)}
                  >
                    수정
                  </button>
                  <button
                    type="button"
                    className={`${styles.btn} ${styles.btnSmall} ${styles.btnDanger}`}
                    onClick={() => onDelete(item)}
                  >
                    삭제
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
