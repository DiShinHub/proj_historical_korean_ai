import styles from "@/styles/Dictionary.module.css";
import { PERIOD_PRESETS } from "@/lib/dictionary/fields";

interface DateRangeBarProps {
  start: string;
  end: string;
  onChange: (start: string, end: string) => void;
  /** 외부 <label htmlFor="..."> 연동용 ID */
  startId?: string;
  endId?: string;
  /** 프리셋 칩 노출 여부 */
  showPresets?: boolean;
  disabled?: boolean;
  startLabel?: string;
  endLabel?: string;
  /** 자동으로 붙는 시각 안내 문구 노출 */
  showTimeHint?: boolean;
}

/**
 * 기간 선택 바(Date Range Bar).
 */
export default function DateRangeBar({
  start,
  end,
  onChange,
  startId,
  endId,
  showPresets = true,
  disabled = false,
  startLabel = "시작일",
  endLabel = "종료일",
  showTimeHint = true,
}: DateRangeBarProps) {
  const activePreset = PERIOD_PRESETS.find(
    (p) => p.start === start && p.end === end
  );

  const invalid = Boolean(start && end && start > end);

  // 텍스트 입력 영역 클릭/포커스 시 달력 팝업(Picker) 실행
  const handleOpenPicker = (e: React.SyntheticEvent<HTMLInputElement>) => {
    try {
      e.currentTarget.showPicker();
    } catch {
      // showPicker를 지원하지 않는 일부 브라우저 예외 처리
    }
  };

  return (
    <div className={styles.rangeBar}>
      <div className={styles.rangeRow}>
        <input
          id={startId}
          type="date"
          className={`${styles.input} ${invalid ? styles.inputError : ""}`}
          value={start}
          min="0001-01-01"
          max="9999-12-31"
          disabled={disabled}
          aria-label={startLabel}
          onChange={(e) => onChange(e.target.value, end)}
          onClick={handleOpenPicker}
          onFocus={handleOpenPicker}
        />
        <span className={styles.rangeSep}>~</span>
        <input
          id={endId}
          type="date"
          className={`${styles.input} ${invalid ? styles.inputError : ""}`}
          value={end}
          min="0001-01-01"
          max="9999-12-31"
          disabled={disabled}
          aria-label={endLabel}
          onChange={(e) => onChange(start, e.target.value)}
          onClick={handleOpenPicker}
          onFocus={handleOpenPicker}
        />
      </div>

      {invalid ? (
        <span className={styles.errorText}>
          시작일이 종료일보다 늦습니다.
        </span>
      ) : null}

      {showPresets ? (
        <div className={styles.presetRow}>
          {PERIOD_PRESETS.map((preset) => (
            <button
              key={preset.label}
              type="button"
              className={`${styles.presetChip} ${
                activePreset?.label === preset.label
                  ? styles.presetChipActive
                  : ""
              }`}
              disabled={disabled}
              onClick={() => onChange(preset.start, preset.end)}
            >
              {preset.label}
            </button>
          ))}
          {start || end ? (
            <button
              type="button"
              className={styles.presetChip}
              disabled={disabled}
              onClick={() => onChange("", "")}
            >
              기간 해제
            </button>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}