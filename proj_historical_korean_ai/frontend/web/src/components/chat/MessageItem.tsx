import { useState } from "react";
import type { ChatMessage } from "@/redux/slices/messagesSlice";
import Markdown from "./Markdown";
import TypingIndicator from "./TypingIndicator";

interface MessageItemProps {
  message: ChatMessage;
  onRetry?: (message: ChatMessage) => void;
}

export default function MessageItem({ message, onRetry }: MessageItemProps) {
  if (message.role === "USER") {
    return <UserMessage message={message} onRetry={onRetry} />;
  }
  return <AssistantMessage message={message} onRetry={onRetry} />;
}

function UserMessage({ message, onRetry }: MessageItemProps) {
  return (
    <div className="message user">
      <div className="bubble">
        {message.attachmentName ? (
          <div className="attachment-chip" title="프론트 전용 첨부 (백엔드 미구현)">
            📎 {message.attachmentName}
          </div>
        ) : null}
        <div className="bubble-text">{message.content}</div>
        {message.status === "failed" ? (
          <div className="msg-error">
            <span>전송 실패</span>
            {onRetry ? (
              <button type="button" onClick={() => onRetry(message)}>
                다시 시도
              </button>
            ) : null}
          </div>
        ) : null}
      </div>
    </div>
  );
}

function AssistantMessage({ message, onRetry }: MessageItemProps) {
  const [copied, setCopied] = useState(false);

  const copyAll = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* noop */
    }
  };

  if (message.status === "waiting") {
    return (
      <div className="message assistant">
        <div className="response-card translation">
          <TypingIndicator />
        </div>
      </div>
    );
  }

  if (message.status === "error") {
    return (
      <div className="message assistant">
        <div className="response-card error-card">
          <div className="card-title">오류</div>
          <div className="card-content">
            {message.error ?? "응답을 받지 못했습니다."}
          </div>
          {onRetry ? (
            <div className="card-actions">
              <button type="button" onClick={() => onRetry(message)}>
                다시 시도
              </button>
            </div>
          ) : null}
        </div>
      </div>
    );
  }

  const isEmpty = message.status === "done" && message.content.trim() === "";

  return (
    <div className="message assistant">
      <div className="response-card translation">
        <div className="card-title">번역 결과</div>
        <div className="card-content">
          {isEmpty ? (
            <span className="muted">
              (응답이 비어 있습니다 — 백엔드가 아직 텍스트를 생성하지 않습니다.
              체크포인트 #2)
            </span>
          ) : (
            <Markdown content={message.content} />
          )}
          {message.status === "streaming" ? (
            <span className="stream-caret" aria-hidden />
          ) : null}
        </div>
        {!isEmpty ? (
          <div className="card-actions">
            <button type="button" onClick={copyAll}>
              {copied ? "복사됨" : "복사"}
            </button>
          </div>
        ) : null}
      </div>

      {message.audioUrl ? (
        <div className="response-card">
          <div className="card-title">음성 생성 결과</div>
          <audio controls src={message.audioUrl} className="audio-native" />
        </div>
      ) : null}
    </div>
  );
}
