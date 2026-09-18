import { useState } from "react";
import styles from "@/styles/Dictionary.module.css";
import Modal from "./Modal";
import DateRangeBar from "./DateRangeBar";
import {
  createDictionary,
  updateDictionary,
  type HkDictionaryDto,
  type HkDictionaryWritePayload,
} from "@/lib/api/dictionary";
import type { ApiError } from "@/lib/api/types";
import {
  toDateInputValue,
  toPeriodEndIso,
  toPeriodStartIso,
} from "@/lib/dictionary/datetime";

interface DictionaryFormDialogProps {
  /** null 이면 신규 등록, 값이 있으면 수정 */
  target: HkDictionaryDto | null;
  onClose: () => void;
  onSaved: (message: string) => void;
}

interface FormState {
  modern_korean: string;
  historical_korean: string;
  periodStart: string;
  periodEnd: string;
  confirmed_yn: string;
}

function toFormState(target: HkDictionaryDto | null): FormState {
  return {
    modern_korean: target?.modern_korean ?? "",
    historical_korean: target?.historical_korean ?? "",
    periodStart: toDateInputValue(target?.historical_period_start_dt),
    periodEnd: toDateInputValue(target?.historical_period_end_dt),
    confirmed_yn: target?.confirmed_yn === "Y" ? "Y" : "N",
  };
}

/**
 * 사전 항목 등록 / 수정 모달.
 *
 * 기간은 연-월-일까지만 입력받고, 전송 시 시각을 자동으로 붙인다.
 *   시작 → T00:00:00+09:00 / 종료 → T23:59:59+09:00
 */
export default function DictionaryFormDialog({
  target,
  onClose,
  onSaved,
}: DictionaryFormDialogProps) {
  const isEdit = target != null;

  const [form, setForm] = useState<FormState>(() => toFormState(target));
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const patch = (part: Partial<FormState>) =>
    setForm((prev) => ({ ...prev, ...part }));

  const modernMissing = !form.modern_korean.trim();
  const historicalMissing = !form.historical_korean.trim();
  const rangeMissing = !form.periodStart || !form.periodEnd;
  const rangeInvalid = Boolean(
    rangeMissing || form.periodStart > form.periodEnd
  );
  const blocked = modernMissing || historicalMissing || rangeInvalid;

  const handleSubmit = async () => {
    if (blocked || submitting) return;

    setSubmitting(true);
    setError(null);

    const payload: HkDictionaryWritePayload = {
      modern_korean: form.modern_korean.trim(),
      historical_korean: form.historical_korean.trim(),
      historical_period_start_dt: toPeriodStartIso(form.periodStart),
      historical_period_end_dt: toPeriodEndIso(form.periodEnd),
    };

    try {
      if (isEdit && target) {
        // confirmed_yn 은 PUT 화이트리스트에 포함되어 수정 시에만 반영된다.
        await updateDictionary(target.seq, {
          ...payload,
          confirmed_yn: form.confirmed_yn,
        });
        onSaved(`사전 항목 #${target.seq} 을(를) 수정했습니다.`);
      } else {
        const seq = await createDictionary(payload);
        onSaved(
          seq != null
            ? `사전 항목 #${seq} 을(를) 등록했습니다.`
            : "사전 항목을 등록했습니다."
        );
      }
      onClose();
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError?.message ?? "저장에 실패했습니다.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      title={isEdit ? `사전 항목 수정 · #${target?.seq}` : "사전 항목 등록"}
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
            {submitting ? "저장 중…" : isEdit ? "수정" : "등록"}
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

      <div className={styles.formGrid}>
        <div className={styles.field}>
          <label className={styles.fieldLabel} htmlFor="d-modern">
            현대어<span className={styles.required}>*</span>
          </label>
          <input
            id="d-modern"
            className={`${styles.input} ${
              modernMissing ? styles.inputError : ""
            }`}
            value={form.modern_korean}
            maxLength={255}
            placeholder="예: 사랑"
            autoFocus
            onChange={(e) => patch({ modern_korean: e.target.value })}
          />
          {modernMissing ? (
            <span className={styles.errorText}>현대어는 필수입니다.</span>
          ) : null}
        </div>
        <div className={styles.field}>
          <label className={styles.fieldLabel} htmlFor="d-historical">
            고어<span className={styles.required}>*</span>
          </label>
          <input
            id="d-historical"
            className={`${styles.input} ${
              historicalMissing ? styles.inputError : ""
            }`}
            value={form.historical_korean}
            maxLength={255}
            placeholder="예: 괴다"
            onChange={(e) => patch({ historical_korean: e.target.value })}
          />
          {historicalMissing ? (
            <span className={styles.errorText}>고어는 필수입니다.</span>
          ) : null}
        </div>

        <div className={`${styles.field} ${styles.formFull}`}>
          <div className={styles.fieldLabelRow}>
            <label className={styles.fieldLabel} htmlFor="f-form-period-start">
              시대 기간<span className={styles.required}>*</span>
            </label>
          </div>
          <DateRangeBar
            startId="f-form-period-start"
            endId="f-form-period-end"
            start={form.periodStart}
            end={form.periodEnd}
            onChange={(periodStart, periodEnd) =>
              patch({ periodStart, periodEnd })
            }
          />
          {rangeMissing ? (
            <span className={styles.errorText}>시대 기간 입력은 필수 입니다.</span>
          ) : null}
        </div>
        {isEdit ? (
          <div className={styles.field}>
            <label className={styles.fieldLabel} htmlFor="d-confirmed">
              검수 여부
            </label>
            <select
              id="d-confirmed"
              className={styles.select}
              value={form.confirmed_yn}
              onChange={(e) => patch({ confirmed_yn: e.target.value })}
            >
              <option value="Y">Y</option>
              <option value="N">N</option>
            </select>
          </div>
        ) : null}
      </div>
    </Modal>
  );
}