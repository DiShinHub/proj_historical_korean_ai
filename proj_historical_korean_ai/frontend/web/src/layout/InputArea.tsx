import { KeyboardEvent, useRef, useState } from "react";
import { useAppDispatch, useAppSelector } from "@/redux/hooks";
import { sendMessage } from "@/redux/slices/messagesSlice";
import { createSession } from "@/redux/slices/sessionsSlice";

const MAX_TEXTAREA_HEIGHT = 200;

export default function InputArea() {
  const dispatch = useAppDispatch();
  const activeSeq = useAppSelector((s) => s.sessions.activeSeq);
  const sending = useAppSelector((s) =>
    activeSeq != null ? Boolean(s.messages.pendingAssistant[activeSeq]) : false
  );

  const [value, setValue] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  // Unconfirmed optimistic session (negative seq) → block until it resolves.
  const blockedByUnconfirmed = activeSeq != null && activeSeq < 0;
  const disabled = sending || busy || blockedByUnconfirmed;
  const canSend = value.trim().length > 0 && !disabled;

  const autoGrow = () => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, MAX_TEXTAREA_HEIGHT)}px`;
  };

  const resetTextarea = () => {
    setValue("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  };

  const handleSend = async () => {
    const text = value.trim();
    if (!text || disabled) return;

    setBusy(true);
    try {
      let seq = activeSeq;
      if (seq == null) {
        // Auto-create a session titled from the first line.
        const created = await dispatch(
          createSession({ title: text.slice(0, 30) || "새 대화" })
        ).unwrap();
        seq = created.seq;
      }
      dispatch(
        sendMessage({
          sessionSeq: seq,
          content: text,
          attachmentName: file?.name,
        })
      );
      resetTextarea();
      setFile(null);
      if (fileRef.current) fileRef.current.value = "";
    } catch {
      /* createSession failure is surfaced via the sessions slice */
    } finally {
      setBusy(false);
    }
  };

  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault();
      void handleSend();
    }
  };

  return (
    <div className="input-area">
      {file ? (
        <div className="attachment-preview">
          <span className="attachment-chip" title="백엔드 업로드 미구현 (체크포인트 #7)">
            📎 {file.name}
          </span>
          <button
            type="button"
            className="attachment-remove"
            onClick={() => {
              setFile(null);
              if (fileRef.current) fileRef.current.value = "";
            }}
            aria-label="첨부 제거"
          >
            ✕
          </button>
        </div>
      ) : null}

      <div className="input-row">
        <button
          type="button"
          className="attach-btn"
          onClick={() => fileRef.current?.click()}
          disabled={disabled}
          title="PDF 첨부 (백엔드 미구현)"
          aria-label="PDF 첨부"
        >
          📎
        </button>
        <input
          ref={fileRef}
          type="file"
          accept="application/pdf,.pdf"
          hidden
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />

        <textarea
          ref={textareaRef}
          value={value}
          placeholder={
            blockedByUnconfirmed
              ? "대화 생성 중…"
              : "번역할 문장을 입력하세요 (Enter 전송 · Shift+Enter 줄바꿈)"
          }
          onChange={(e) => {
            setValue(e.target.value);
            autoGrow();
          }}
          onKeyDown={onKeyDown}
          disabled={disabled}
          rows={1}
          aria-label="메시지 입력"
        />

        <button
          type="button"
          className="send-btn"
          onClick={() => void handleSend()}
          disabled={!canSend}
        >
          {sending ? "응답 중…" : "전송"}
        </button>
      </div>
    </div>
  );
}
