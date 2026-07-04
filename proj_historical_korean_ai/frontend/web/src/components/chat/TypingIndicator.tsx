/** Three-dot "assistant is thinking" animation. */
export default function TypingIndicator() {
  return (
    <div className="typing" role="status" aria-label="응답 생성 중">
      <span className="dot" />
      <span className="dot" />
      <span className="dot" />
    </div>
  );
}
