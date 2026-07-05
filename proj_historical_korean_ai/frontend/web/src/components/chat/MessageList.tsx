import { useEffect, useRef } from "react";
import { useAppDispatch, useAppSelector } from "@/redux/hooks";
import {
  ChatMessage,
  removeMessage,
  sendMessage,
} from "@/redux/slices/messagesSlice";
import MessageItem from "./MessageItem";
import EmptyState from "./EmptyState";

export default function MessageList() {
  const dispatch = useAppDispatch();
  const activeSeq = useAppSelector((s) => s.sessions.activeSeq);
  const messages = useAppSelector((s) =>
    activeSeq != null ? s.messages.bySession[activeSeq] ?? [] : []
  );
  const status = useAppSelector((s) =>
    activeSeq != null ? s.messages.statusBySession[activeSeq] : undefined
  );

  const bottomRef = useRef<HTMLDivElement>(null);
  const lastContent =
    messages.length > 0 ? messages[messages.length - 1].content : "";

  // Auto-scroll on new/streaming content.
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length, lastContent]);

  if (activeSeq == null) {
    return (
      <div className="messages">
        <EmptyState
          title="대화를 시작해 보세요"
          description="왼쪽에서 새 대화를 만들거나 기존 대화를 선택하세요."
        />
      </div>
    );
  }

  const handleRetry = (message: ChatMessage) => {
    if (activeSeq == null) return;
    const idx = messages.findIndex((m) => m.id === message.id);
    // Resolve the user content + the paired assistant to clear.
    let userMsg = message;
    let assistantMsg: ChatMessage | undefined;
    if (message.role === "USER") {
      assistantMsg = messages[idx + 1];
    } else {
      userMsg = messages[idx - 1] ?? message;
      assistantMsg = message;
    }
    if (userMsg) dispatch(removeMessage({ sessionSeq: activeSeq, id: userMsg.id }));
    if (assistantMsg)
      dispatch(removeMessage({ sessionSeq: activeSeq, id: assistantMsg.id }));
    dispatch(
      sendMessage({
        sessionSeq: activeSeq,
        content: userMsg.content,
        attachmentName: userMsg.attachmentName,
      })
    );
  };

  if (status === "loading" && messages.length === 0) {
    return (
      <div className="messages">
        <div className="loading-note">불러오는 중…</div>
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <div className="messages">
        <EmptyState
          title="무엇을 번역해 드릴까요?"
          description="현대 한국어 문장과 중세 국어를 번역합니다."
        />
      </div>
    );
  }

  return (
    <div className="messages">
      {messages.map((m) => (
        <MessageItem key={m.id} message={m} onRetry={handleRetry} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
