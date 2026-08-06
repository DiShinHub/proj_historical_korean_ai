import styles from "@/styles/Dictionary.module.css";
import { PAGE_SIZE_OPTIONS } from "@/hooks/useDictionaryList";

interface PaginationProps {
  page: number;
  pageSize: number;
  totalCnt: number;
  totalPages: number;
  loading: boolean;
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
}

/** 현재 페이지 주변 번호만 노출한다(최대 7개). */
function buildPageWindow(page: number, totalPages: number): number[] {
  const WINDOW = 7;
  if (totalPages <= WINDOW) {
    return Array.from({ length: totalPages }, (_, i) => i + 1);
  }

  const half = Math.floor(WINDOW / 2);
  let start = Math.max(1, page - half);
  const end = Math.min(totalPages, start + WINDOW - 1);
  start = Math.max(1, end - WINDOW + 1);

  return Array.from({ length: end - start + 1 }, (_, i) => start + i);
}

export default function Pagination({
  page,
  pageSize,
  totalCnt,
  totalPages,
  loading,
  onPageChange,
  onPageSizeChange,
}: PaginationProps) {
  const pages = buildPageWindow(page, totalPages);
  const firstIndex = totalCnt === 0 ? 0 : (page - 1) * pageSize + 1;
  const lastIndex = Math.min(page * pageSize, totalCnt);

  return (
    <div className={styles.pagination}>
      <span className={styles.pageInfo}>
        전체 {totalCnt.toLocaleString()}건 · {firstIndex}–{lastIndex} 표시 ({page}/
        {totalPages} 페이지)
      </span>

      <span className={styles.panelSpacer} />

      <select
        className={styles.select}
        style={{ width: "auto" }}
        value={pageSize}
        disabled={loading}
        aria-label="페이지당 개수"
        onChange={(e) => onPageSizeChange(Number(e.target.value))}
      >
        {PAGE_SIZE_OPTIONS.map((size) => (
          <option key={size} value={size}>
            {size}건씩
          </option>
        ))}
      </select>

      <div className={styles.pageBtns}>
        <button
          type="button"
          className={styles.pageBtn}
          disabled={loading || page <= 1}
          onClick={() => onPageChange(1)}
          aria-label="첫 페이지"
        >
          «
        </button>
        <button
          type="button"
          className={styles.pageBtn}
          disabled={loading || page <= 1}
          onClick={() => onPageChange(page - 1)}
          aria-label="이전 페이지"
        >
          ‹
        </button>

        {pages.map((n) => (
          <button
            key={n}
            type="button"
            className={`${styles.pageBtn} ${
              n === page ? styles.pageBtnActive : ""
            }`}
            disabled={loading}
            aria-current={n === page ? "page" : undefined}
            onClick={() => onPageChange(n)}
          >
            {n}
          </button>
        ))}

        <button
          type="button"
          className={styles.pageBtn}
          disabled={loading || page >= totalPages}
          onClick={() => onPageChange(page + 1)}
          aria-label="다음 페이지"
        >
          ›
        </button>
        <button
          type="button"
          className={styles.pageBtn}
          disabled={loading || page >= totalPages}
          onClick={() => onPageChange(totalPages)}
          aria-label="마지막 페이지"
        >
          »
        </button>
      </div>
    </div>
  );
}
