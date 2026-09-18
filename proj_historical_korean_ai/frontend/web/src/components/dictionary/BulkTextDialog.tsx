import { useState } from "react";
import styles from "@/styles/Dictionary.module.css";
import Modal from "./Modal";
import DateRangeBar from "./DateRangeBar";
import { dumpRawDictionary } from "@/lib/api/dictionary";
import type { ApiError } from "@/lib/api/types";
import { HK_DICTIONARY_ROOM } from "@/hooks/useDictionaryRoom";
import { toDumpEnd, toDumpStart } from "@/lib/dictionary/datetime";
import {
  toPeriodEndIso,
  toPeriodStartIso,
} from "@/lib/dictionary/datetime";

/** 백엔드 문서에 실린 예시 원문. QA/데모용 채우기 버튼에서 사용한다. */
const SAMPLE_RAW_TEXT =
  "복식근주001) 하람주002) 사름미라주003) 녀름주004) 지주005) 주006) 치길주007) 더니 " +
  "져믄주008) 아주009) 잇더니주010) 그 앗이주011) 라거주012) 집 뎐디주013) 믈주014) " +
  "를주015) 다 아 주고 다주016)  이ㄹ주017) 나닐주018) 복식기주019) 가지고 뫼헤주020) " +
  "드러가주021) 여나믄주022) 주023)  치니 일쳔 나마주024) 도어주025) 집 뎐딜주026) " +
  " 사니 그 아주027) 셰간주028) 다 배오주029) 잇거 다시 논화주030) 주니라";

interface BulkTextDialogProps {
  onClose: () => void;
  /** 큐 적재 성공(=요청 접수) 시 호출. 실제 결과는 소켓으로 들어온다. */
  onRequested: (message: string) => void;
}

/**
 * 원문(raw_text) 일괄 삽입 모달.
 *
 * POST /au/hk_dictionary/dump 는 **비동기**다.
 * 요청은 Redis 큐(TSK_002)에 적재만 되고 즉시 성공을 반환하며,
 * LLM 이 고어/현대어 쌍을 뽑아 DB 에 넣은 결과는
 * room_name 으로 지정한 소켓 room 에 브로드캐스트된다.
 * → 이 화면은 전 사용자 공용 room(HK_DICTIONARY_ROOM)에 조인해 결과를 받는다.
 */
export default function BulkTextDialog({
  onClose,
  onRequested,
}: BulkTextDialogProps) {
  const [rawText, setRawText] = useState("");
  const [periodStart, setPeriodStart] = useState("");
  const [periodEnd, setPeriodEnd] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const textMissing = !rawText.trim();
  const rangeInvalid = Boolean(
    periodStart && periodEnd && periodStart > periodEnd
  );
  const blocked = textMissing || rangeInvalid;

  const handleSubmit = async () => {
    if (blocked || submitting) return;

    setSubmitting(true);
    setError(null);

    try {
      await dumpRawDictionary({
        raw_text: rawText.trim(),
        historical_period_start_dt: toPeriodStartIso(periodStart),
        historical_period_end_dt: toPeriodEndIso(periodEnd),
        room_name: HK_DICTIONARY_ROOM,
      });

      onRequested(
        `원문 일괄 삽입 요청을 접수했습니다 (${rawText.trim().length.toLocaleString()}자). 처리 결과를 기다립니다…`
      );
      onClose();
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError?.message ?? "일괄 삽입 요청에 실패했습니다.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      title="일괄 삽입 · 원문 텍스트"
      wide
      onClose={onClose}
      footer={
        <>
          <span className={styles.panelSpacer} />
          <button type="button" className={styles.btn} onClick={onClose}>
            취소
          </button>
          <button
            type="button"
            className={`${styles.btn} ${styles.btnPrimary}`}
            disabled={blocked || submitting}
            onClick={handleSubmit}
          >
            {submitting ? "요청 중…" : "일괄 삽입 요청"}
          </button>
        </>
      }
    >

      {error ? (
        <div className={`${styles.notice} ${styles.noticeError}`}>
          <span aria-hidden>⚠️</span>
          <span>{error}</span>
        </div>
      ) : null}

      <div className={styles.field}>
        <div className={styles.fieldLabelRow}>
          <label className={styles.fieldLabel} htmlFor="d-raw">
            원문 (raw_text)<span className={styles.required}>*</span>
          </label>
          <span className={styles.panelSpacer} />
          <button
            type="button"
            className={`${styles.btn} ${styles.btnSmall} ${styles.btnGhost}`}
            onClick={() => setRawText(SAMPLE_RAW_TEXT)}
          >
            예시 원문 채우기
          </button>
          <button
            type="button"
            className={`${styles.btn} ${styles.btnSmall} ${styles.btnGhost}`}
            onClick={() => setRawText("")}
          >
            비우기
          </button>
        </div>
        <textarea
          id="d-raw"
          className={`${styles.textarea} ${
            textMissing ? styles.inputError : ""
          }`}
          value={rawText}
          placeholder="고문헌 원문을 붙여 넣으세요. 고어–현대어 쌍은 백엔드 LLM 파이프라인이 추출합니다."
          onChange={(e) => setRawText(e.target.value)}
        />
        <span className={styles.charCount}>
          {rawText.length.toLocaleString()}자
        </span>
      </div>

      <div className={styles.field}>
        <span className={styles.fieldLabel}>시대 기간 (추출 항목 공통 적용)</span>
        <DateRangeBar
          start={periodStart}
          end={periodEnd}
          onChange={(start, end) => {
            setPeriodStart(start);
            setPeriodEnd(end);
          }}
        />
      </div>

    </Modal>
  );
}
