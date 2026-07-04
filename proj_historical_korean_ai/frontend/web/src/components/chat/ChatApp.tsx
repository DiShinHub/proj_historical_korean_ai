import { useEffect, useState } from "react";
import { useAppDispatch, useAppSelector } from "@/redux/hooks";
import { useBootstrap } from "@/hooks/useBootstrap";
import { useChatRuntime } from "@/hooks/useChatRuntime";
import { initAuth } from "@/redux/slices/authSlice";
import { fetchMessages } from "@/redux/slices/messagesSlice";
import Sidebar from "@/layout/Sidebar";
import ChatArea from "@/layout/ChatArea";

export default function ChatApp() {
  const dispatch = useAppDispatch();
  const [collapsed, setCollapsed] = useState(false);

  useBootstrap();

  const activeSeq = useAppSelector((s) => s.sessions.activeSeq);
  const authStatus = useAppSelector((s) => s.auth.status);
  const authError = useAppSelector((s) => s.auth.error);
  const loadedStatus = useAppSelector((s) =>
    activeSeq != null ? s.messages.statusBySession[activeSeq] : undefined
  );

  useChatRuntime(activeSeq);

  // Load messages when a real (confirmed) session becomes active.
  useEffect(() => {
    if (activeSeq != null && activeSeq > 0 && loadedStatus === undefined) {
      dispatch(fetchMessages(activeSeq));
    }
  }, [activeSeq, loadedStatus, dispatch]);

  if (authStatus === "error") {
    return (
      <div className="fullscreen-state">
        <div className="empty-icon" aria-hidden>
          ⚠️
        </div>
        <h2>백엔드에 연결할 수 없습니다</h2>
        <p className="muted">{authError}</p>
        <button className="new-chat" onClick={() => dispatch(initAuth())}>
          다시 시도
        </button>
      </div>
    );
  }

  return (
    <div className={`app ${collapsed ? "sidebar-collapsed" : ""}`}>
      <Sidebar
        collapsed={collapsed}
        onToggleCollapse={() => setCollapsed((v) => !v)}
      />
      <ChatArea />
    </div>
  );
}
