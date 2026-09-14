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
  const [collapsed, setCollapsed] = useState(false); // 사이드바 접힘/펼침 UI 상태
  
  // 최초 동작 (인증 후 세션 리스트 조회)
  useBootstrap();

  const activeSeq = useAppSelector((s) => s.sessions.activeSeq);
  const authStatus = useAppSelector((s) => s.auth.status);
  const authError = useAppSelector((s) => s.auth.error);
  const loadedStatus = useAppSelector((s) =>
    activeSeq != null ? s.messages.statusBySession[activeSeq] : undefined
  );

  // 활성화 된 세션의 socket 연결
  useChatRuntime(activeSeq);

  // 활성화 된 세션의 메세지들을 로드
  useEffect(() => {
    if (activeSeq != null && activeSeq > 0 && loadedStatus === undefined) {
      dispatch(fetchMessages(activeSeq));
    }
  }, [activeSeq, loadedStatus, dispatch]);

  // 오류 처리
  if (authStatus === "error") {
    return (
      <div className="fullscreen-state">
        <div className="empty-icon" aria-hidden>
          ⚠️
        </div>
        <h2>서버에 연결할 수 없습니다</h2>
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
