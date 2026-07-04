// src/components/chat/MessageList.tsx

export default function MessageList() {
  return (
    <div className="messages">
      {/* USER MESSAGE */}
      <div className="message user">
        <div className="bubble">
          안녕하세요를 14세기 중세 국어로 변환해줘.
        </div>
      </div>

      {/* ASSISTANT MESSAGE */}
      <div className="message assistant">
        
        {/* TRANSLATION CARD */}
        <div className="response-card translation">
          <div className="card-title">번역 결과</div>

          <div className="card-content">
            平安ᄒᆞ신잇가?
          </div>

          <div className="card-actions">
            <button type="button">복사</button>
            <button type="button">재생</button>
          </div>
        </div>

        {/* AUDIO CARD */}
        <div className="response-card">
          <div className="card-title">음성 생성 결과</div>

          <div className="audio-player">
            <button type="button" className="play-btn">
              ▶
            </button>

            <div className="progress-bar">
              <div className="progress" />
            </div>

            <span>00:15</span>
          </div>
        </div>
      </div>
    </div>
  );
}