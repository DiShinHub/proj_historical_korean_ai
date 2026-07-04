import { useAppSelector } from "@/redux/hooks";
import MessageList from "@/components/chat/MessageList";
import InputArea from "./InputArea";

export default function ChatArea() {
  const activeSeq = useAppSelector((s) => s.sessions.activeSeq);
  const title = useAppSelector(
    (s) => s.sessions.items.find((x) => x.seq === activeSeq)?.title
  );

  return (
    <main className="chat-area">
      <header className="chat-header">
        <h1 className="chat-title">{title ?? "고대 한국어 번역 LLM"}</h1>
      </header>
      <MessageList />
      <InputArea />
    </main>
  );
}
