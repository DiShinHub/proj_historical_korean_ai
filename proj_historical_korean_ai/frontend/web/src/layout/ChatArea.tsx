import MessageList from "../components/chat/MessageList";
import InputArea from "./InputArea";

export default function ChatArea() {
  return (
    <main className="chat-area">
      <MessageList />
      <InputArea />
    </main>
  );
}