export default function InputArea() {
  return (
    <div className="input-area">
      <textarea placeholder="번역할 문장을 입력하세요" />
      <button className="send-btn">전송</button>
    </div>
  );
}