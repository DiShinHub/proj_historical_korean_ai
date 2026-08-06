import { useEffect, useState } from "react";
import styles from "@/styles/Dictionary.module.css";
import Modal from "./Modal";
import { getDictionary, type HkDictionaryDto } from "@/lib/api/dictionary";
import type { ApiError } from "@/lib/api/types";
import { formatDate, formatDateTime } from "@/lib/dictionary/datetime";

interface DictionaryDetailDialogProps {
  seq: number;
  onClose: () => void;
  onEdit: (item: HkDictionaryDto) => void;
}

/**
 * 단건 조회 모달 (GET /au/hk_dictionary/{seq}).
 *
 * 목록 API 가 내려주지 않는 reg_member_seq / mod_dt / mod_member_seq 를
 * 여기서 확인할 수 있다.
 * (confirmed_yn 은 단건 응답에도 없어 "-" 로 표시된다 — 노트 §2)
 */
export default function DictionaryDetailDialog({
  seq,
  onClose,
  onEdit,
}: DictionaryDetailDialogProps) {
  const [item, setItem] = useState<HkDictionaryDto | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    setLoading(true);
    setError(null);

    getDictionary(seq)
      .then((data) => {
        if (!cancelled) setItem(data);
      })
      .catch((err: ApiError) => {
        if (!cancelled) setError(err?.message ?? "조회에 실패했습니다.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [seq]);

  return (
    <Modal
      title={`사전 항목 상세 · #${seq}`}
      onClose={onClose}
      footer={
        <>
          <span className={styles.panelSpacer} />
          <button type="button" className={styles.btn} onClick={onClose}>
            닫기
          </button>
          <button
            type="button"
            className={`${styles.btn} ${styles.btnPrimary}`}
            disabled={!item}
            onClick={() => item && onEdit(item)}
          >
            수정
          </button>
        </>
      }
    >
      {loading ? <div className={styles.feedEmpty}>불러오는 중…</div> : null}

      {error ? (
        <div className={`${styles.notice} ${styles.noticeError}`}>
          <span aria-hidden>⚠️</span>
          <span>{error}</span>
        </div>
      ) : null}

      {item ? (
        <div className={styles.detailList}>
          <span className={styles.detailKey}>번호 (seq)</span>
          <span className={styles.detailVal}>{item.seq}</span>

          <span className={styles.detailKey}>현대어</span>
          <span className={styles.detailVal}>{item.modern_korean}</span>

          <span className={styles.detailKey}>고어</span>
          <span className={styles.detailVal}>{item.historical_korean}</span>

          <span className={styles.detailKey}>시대 시작일</span>
          <span className={styles.detailVal}>
            {formatDate(item.historical_period_start_dt)}
            <span className={styles.fieldHint}>
              {" "}
              ({formatDateTime(item.historical_period_start_dt)})
            </span>
          </span>

          <span className={styles.detailKey}>시대 종료일</span>
          <span className={styles.detailVal}>
            {formatDate(item.historical_period_end_dt)}
            <span className={styles.fieldHint}>
              {" "}
              ({formatDateTime(item.historical_period_end_dt)})
            </span>
          </span>

          <span className={styles.detailKey}>등록일시</span>
          <span className={styles.detailVal}>{formatDateTime(item.reg_dt)}</span>

          <span className={styles.detailKey}>수정일시</span>
          <span className={styles.detailVal}>{formatDateTime(item.mod_dt)}</span>

          <span className={styles.detailKey}>검수여부</span>
          <span className={styles.detailVal}>
            {item.confirmed_yn ?? "-"}
            {item.confirmed_yn == null ? (
              <span className={styles.fieldHint}> (단건 응답 미포함)</span>
            ) : null}
          </span>
        </div>
      ) : null}
    </Modal>
  );
}
