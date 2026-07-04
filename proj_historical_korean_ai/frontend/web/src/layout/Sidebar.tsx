import { useState } from "react";
import { useTheme } from "@/themes/ThemeContext";
import { useAppDispatch, useAppSelector } from "@/redux/hooks";
import {
  createSession,
  deleteSession,
  renameSession,
  setActiveSession,
  type ChatSession,
} from "@/redux/slices/sessionsSlice";
import type { SocketStatus } from "@/lib/socket";

interface SidebarProps {
  collapsed: boolean;
  onToggleCollapse: () => void;
}

const SOCKET_LABEL: Record<SocketStatus, string> = {
  idle: "대기",
  connecting: "연결 중",
  open: "연결됨",
  reconnecting: "재연결 중",
  closed: "끊김",
  error: "오류",
};

export default function Sidebar({ collapsed, onToggleCollapse }: SidebarProps) {
  const dispatch = useAppDispatch();
  const { toggleTheme } = useTheme();

  const sessions = useAppSelector((s) => s.sessions.items);
  const activeSeq = useAppSelector((s) => s.sessions.activeSeq);
  const status = useAppSelector((s) => s.sessions.status);
  const memberId = useAppSelector((s) => s.auth.me?.memberId ?? "admin0");
  const socketStatus = useAppSelector((s) => s.socket.status);

  const [editingSeq, setEditingSeq] = useState<number | null>(null);
  const [editValue, setEditValue] = useState("");

  const handleNewChat = () => {
    dispatch(createSession({ title: "새 대화" }));
  };

  const handleSelect = (seq: number) => {
    if (seq !== activeSeq) dispatch(setActiveSession(seq));
  };

  const startRename = (session: ChatSession) => {
    setEditingSeq(session.seq);
    setEditValue(session.title);
  };

  const commitRename = (seq: number) => {
    const title = editValue.trim();
    if (title) dispatch(renameSession({ seq, title }));
    setEditingSeq(null);
  };

  const handleDelete = (session: ChatSession) => {
    if (window.confirm(`"${session.title}" 대화를 삭제할까요?`)) {
      dispatch(deleteSession(session.seq));
    }
  };

  if (collapsed) {
    return (
      <aside className="sidebar collapsed">
        <button
          className="icon-btn"
          onClick={onToggleCollapse}
          aria-label="사이드바 펼치기"
          title="사이드바 펼치기"
        >
          ☰
        </button>
        <button
          className="icon-btn"
          onClick={handleNewChat}
          aria-label="새 대화"
          title="새 대화"
        >
          ＋
        </button>
      </aside>
    );
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo">고대 한국어 번역 LLM</div>
        <div className="header-actions">
          <button
            className="icon-btn"
            onClick={toggleTheme}
            aria-label="테마 전환"
            title="테마 전환"
          >
            🌙
          </button>
          <button
            className="icon-btn"
            onClick={onToggleCollapse}
            aria-label="사이드바 접기"
            title="사이드바 접기"
          >
            «
          </button>
        </div>
      </div>

      <button className="new-chat" onClick={handleNewChat}>
        ＋ 새 대화
      </button>

      <div className="session-group">
        <h4>대화</h4>

        {status === "loading" && sessions.length === 0 ? (
          <div className="sidebar-note">불러오는 중…</div>
        ) : null}

        {status === "loaded" && sessions.length === 0 ? (
          <div className="sidebar-note">아직 대화가 없습니다.</div>
        ) : null}

        {sessions.map((session) => {
          const isActive = session.seq === activeSeq;
          const isEditing = editingSeq === session.seq;
          return (
            <div
              key={session.seq}
              className={`session ${isActive ? "active" : ""}`}
              onClick={() => !isEditing && handleSelect(session.seq)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (!isEditing && (e.key === "Enter" || e.key === " ")) {
                  e.preventDefault();
                  handleSelect(session.seq);
                }
              }}
            >
              {isEditing ? (
                <input
                  className="session-edit"
                  value={editValue}
                  autoFocus
                  onChange={(e) => setEditValue(e.target.value)}
                  onBlur={() => commitRename(session.seq)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") commitRename(session.seq);
                    if (e.key === "Escape") setEditingSeq(null);
                  }}
                  onClick={(e) => e.stopPropagation()}
                />
              ) : (
                <>
                  <span className="session-title">{session.title}</span>
                  <span className="session-actions">
                    <button
                      className="icon-btn small"
                      aria-label="이름 변경"
                      title="이름 변경"
                      onClick={(e) => {
                        e.stopPropagation();
                        startRename(session);
                      }}
                    >
                      ✎
                    </button>
                    <button
                      className="icon-btn small"
                      aria-label="삭제"
                      title="삭제"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(session);
                      }}
                    >
                      🗑
                    </button>
                  </span>
                </>
              )}
            </div>
          );
        })}
      </div>

      <div className="sidebar-footer">
        <span className="user-id">👤 {memberId}</span>
        <span className={`socket-status ${socketStatus}`}>
          <span className="socket-dot" />
          {SOCKET_LABEL[socketStatus]}
        </span>
      </div>
    </aside>
  );
}
