import { useRef, useState } from "react";
import styles from "@/styles/Dictionary.module.css";
import Modal from "./Modal";
import DateRangeBar from "./DateRangeBar";
import {
  BackendNotImplementedError,
  DICTIONARY_UPLOAD_ENDPOINT,
  uploadDictionaryFiles,
} from "@/lib/api/dictionary";
import { HK_DICTIONARY_ROOM } from "@/hooks/useDictionaryRoom";
import { toDumpEnd, toDumpStart } from "@/lib/dictionary/datetime";

const ACCEPT_EXTENSIONS = [".xlsx", ".xls", ".csv", ".pdf"];
const ACCEPT_ATTR = ACCEPT_EXTENSIONS.join(",");
const MAX_FILE_BYTES = 20 * 1024 * 1024; // 20MB
const MAX_FILES = 10;

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function hasAllowedExtension(name: string): boolean {
  const lower = name.toLowerCase();
  return ACCEPT_EXTENSIONS.some((ext) => lower.endsWith(ext));
}

interface BulkFileDialogProps {
  onClose: () => void;
  onNotice: (message: string) => void;
}

/**
 * 일괄 삽입 2 · 파일 업로드(Excel / CSV / PDF) — **프론트엔드 전용**.
 *
 * 요구사항 4-B 에 따라 백엔드 API 가 없는 상태이므로,
 * 파일 선택/검증/목록/기간 지정까지의 UI 흐름만 완성해 두고
 * 실제 전송은 스텁(uploadDictionaryFiles)이 막는다.
 * 백엔드가 준비되면 lib/api/dictionary.ts 의 주석 블록만 살리면 된다.
 */
export default function BulkFileDialog({
  onClose,
  onNotice,
}: BulkFileDialogProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);

  const [files, setFiles] = useState<File[]>([]);
  const [dragging, setDragging] = useState(false);
  const [periodStart, setPeriodStart] = useState("");
  const [periodEnd, setPeriodEnd] = useState("");
  const [rejected, setRejected] = useState<string[]>([]);
  const [notImplemented, setNotImplemented] = useState(false);

  const addFiles = (incoming: FileList | null) => {
    if (!incoming) return;

    const nextRejected: string[] = [];
    const accepted: File[] = [];

    Array.from(incoming).forEach((file) => {
      if (!hasAllowedExtension(file.name)) {
        nextRejected.push(`${file.name} · 지원하지 않는 형식`);
        return;
      }
      if (file.size > MAX_FILE_BYTES) {
        nextRejected.push(
          `${file.name} · 용량 초과 (${formatBytes(file.size)} > 20 MB)`
        );
        return;
      }
      accepted.push(file);
    });

    setFiles((prev) => {
      // 같은 이름+크기는 중복으로 본다.
      const seen = new Set(prev.map((f) => `${f.name}:${f.size}`));
      const merged = [...prev];
      accepted.forEach((file) => {
        const key = `${file.name}:${file.size}`;
        if (!seen.has(key)) {
          seen.add(key);
          merged.push(file);
        }
      });
      if (merged.length > MAX_FILES) {
        nextRejected.push(`최대 ${MAX_FILES}개까지 선택할 수 있습니다.`);
        return merged.slice(0, MAX_FILES);
      }
      return merged;
    });

    setRejected(nextRejected);
  };

  const removeFile = (index: number) =>
    setFiles((prev) => prev.filter((_, i) => i !== index));

  const rangeInvalid = Boolean(
    periodStart && periodEnd && periodStart > periodEnd
  );
  const blocked = files.length === 0 || rangeInvalid;

  const handleSubmit = async () => {
    if (blocked) return;

    try {
      await uploadDictionaryFiles({
        files,
        historical_period_start_dt: toDumpStart(periodStart),
        historical_period_end_dt: toDumpEnd(periodEnd),
        room_name: HK_DICTIONARY_ROOM,
      });
    } catch (err) {
      if (err instanceof BackendNotImplementedError) {
        setNotImplemented(true);
        onNotice(
          `파일 업로드 API(${err.endpoint})가 아직 없어 전송하지 않았습니다.`
        );
        return;
      }
      onNotice("파일 업로드 중 알 수 없는 오류가 발생했습니다.");
    }
  };

  return (
    <Modal
      title="일괄 삽입 · 파일 업로드 (Excel / CSV / PDF)"
      wide
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
            disabled={blocked}
            onClick={handleSubmit}
            title={
              blocked
                ? "파일을 선택하세요"
                : "백엔드 API 준비 전이므로 실제 전송되지 않습니다"
            }
          >
            업로드
          </button>
        </>
      }
    >
      <div className={`${styles.notice} ${styles.noticeWarn}`}>
        <span aria-hidden>🚧</span>
        <span>
          <strong> 기능 추가 예정입니다. </strong> 
        </span>
      </div>

      {notImplemented ? (
        <div className={`${styles.notice} ${styles.noticeError}`}>
          <span aria-hidden>⛔</span>
          <span>
            전송이 중단되었습니다. 아직 다음 엔드포인트가 없습니다:
            <br />
            <code>POST {DICTIONARY_UPLOAD_ENDPOINT}</code> (multipart/form-data)
          </span>
        </div>
      ) : null}

      <div
        className={`${styles.dropzone} ${
          dragging ? styles.dropzoneActive : ""
        }`}
        role="button"
        tabIndex={0}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            inputRef.current?.click();
          }
        }}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          addFiles(e.dataTransfer.files);
        }}
      >
        <span className={styles.dropIcon} aria-hidden>
          📄
        </span>
        파일을 이곳에 끌어다 놓거나 클릭해서 선택하세요
        <div className={styles.dropHint}>
          {ACCEPT_EXTENSIONS.join(" / ")} · 파일당 최대 20MB · 최대 {MAX_FILES}개
        </div>
      </div>

      <input
        ref={inputRef}
        type="file"
        multiple
        accept={ACCEPT_ATTR}
        style={{ display: "none" }}
        onChange={(e) => {
          addFiles(e.target.files);
          // 같은 파일을 다시 선택해도 change 가 발생하도록 초기화.
          e.target.value = "";
        }}
      />

      {rejected.length > 0 ? (
        <div className={`${styles.notice} ${styles.noticeError}`}>
          <span aria-hidden>⚠️</span>
          <span>
            제외된 파일
            <br />
            {rejected.map((line) => (
              <span key={line}>
                · {line}
                <br />
              </span>
            ))}
          </span>
        </div>
      ) : null}

      {files.length > 0 ? (
        <div className={styles.field}>
          <div className={styles.fieldLabelRow}>
            <span className={styles.fieldLabel}>
              선택된 파일 {files.length}개
            </span>
            <span className={styles.panelSpacer} />
            <button
              type="button"
              className={`${styles.btn} ${styles.btnSmall} ${styles.btnGhost}`}
              onClick={() => {
                setFiles([]);
                setRejected([]);
              }}
            >
              전체 비우기
            </button>
          </div>
          <div className={styles.fileList}>
            {files.map((file, index) => (
              <div className={styles.fileItem} key={`${file.name}:${file.size}`}>
                <span aria-hidden>
                  {file.name.toLowerCase().endsWith(".pdf") ? "📕" : "📊"}
                </span>
                <span className={styles.fileName} title={file.name}>
                  {file.name}
                </span>
                <span className={styles.fileSize}>{formatBytes(file.size)}</span>
                <button
                  type="button"
                  className={styles.fileRemove}
                  aria-label={`${file.name} 제거`}
                  onClick={() => removeFile(index)}
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      <div className={styles.field}>
        <span className={styles.fieldLabel}>시대 기간 (업로드 항목 공통 적용)</span>
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
