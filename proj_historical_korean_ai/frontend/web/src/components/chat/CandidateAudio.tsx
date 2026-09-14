import { useState } from "react";
import type { TranslationCandidate } from "@/lib/chat/audio";
import { buildAudioUrl } from "@/lib/chat/audio";

interface CandidateAudioProps {
  candidate: TranslationCandidate;
}

/**
 * 번역 후보 1건(텍스트 + IPA + 오디오 + 복사 버튼)을 렌더링한다.
 */
export default function CandidateAudio({ candidate }: CandidateAudioProps) {
  const [runtimeExpired, setRuntimeExpired] = useState(false);
  const [copied, setCopied] = useState(false);
  const expired = candidate.state === "expired" || runtimeExpired;

  // 순수 번역 텍스트만 복사
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(candidate.text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* clipboard unavailable */
    }
  };

  return (
    <div className="candidate-row">
      <div className="candidate-text">
        <div className="candidate-ko">{candidate.text}</div>
        {candidate.ipa ? (
          <div className="candidate-ipa">/{candidate.ipa}/</div>
        ) : null}
        <div className="candidate-actions">
          <button
            type="button"
            className="candidate-copy-btn"
            onClick={handleCopy}
            aria-label="텍스트 복사"
          >
            {copied ? "복사됨" : "복사"}
          </button>
        </div>
      </div>


      <div className="candidate-audio">
        {candidate.state === "notexist" ? (
          <span className="audio-badge notexist">오디오 없음</span>
        ) : (
          <>
            <audio
              controls
              preload="none"
              className="audio-native candidate-audio-el"
              onError={() => setRuntimeExpired(true)}
            >
              <source
                src={buildAudioUrl(candidate.audioPath!)}
                type="audio/wav"
              />
            </audio>
            {expired ? (
              <span className="audio-badge expired">만료됨</span>
            ) : null}
          </>
        )}
      </div>
    </div>
  );
}