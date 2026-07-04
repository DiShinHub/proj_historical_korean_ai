import { useTheme } from "@/themes/ThemeContext";

export default function Sidebar() {
    
  const { toggleTheme } = useTheme();
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo">고대 한국어 번역 LLM</div>
        <button className="theme-btn" onClick={toggleTheme}>🌙</button>
      </div>

      <button className="new-chat">+ 새 대화</button>

      <div className="session-group">
        <h4>오늘</h4>

        <div className="session active">안녕하세요를 14세기 ...</div>
        <div className="session">안녕하세요를 15세기 ...</div>
        <div className="session">배고파요를 중세국어로 ...</div>
      </div>
    </aside>
  );
}