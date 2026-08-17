import { useState } from "react";
import type { TranslationCandidate } from "@/lib/chat/audio";
import { buildAudioUrl } from "@/lib/chat/audio";

interface CandidateAudioProps {
  candidate: TranslationCandidate;
}

/**
 * 번역 후보 1건(텍스트 + IPA + 오디오)을 렌더링한다.
 *
 * state === "play" 여도 MinIO 에 실제 오브젝트가 없으면(삭제/만료) <audio> 가
 * error 이벤트를 던지므로, 그 경우 런타임에 "만료" 배지로 전환한다.
 */
export default function CandidateAudio({ candidate }: CandidateAudioProps) {
  const [runtimeExpired, setRuntimeExpired] = useState(false);
  const expired = candidate.state === "expired" || runtimeExpired;

  return (
    <div className="candidate-row">
      <div className="candidate-text">
        <div className="candidate-ko">{candidate.text}</div>
        {candidate.ipa ? <div className="candidate-ipa">/{candidate.ipa}/</div> : null}
      </div>
      <div className="candidate-audio">
        {candidate.state === "notexist" ? (
          <span className="audio-badge notexist">오디오 없음</span>
        ) : (
          <>
            {/* MinIO가 오브젝트를 application/octet-stream 으로 서빙하므로
                (audio/wav 아님) source type 힌트를 명시해 재생을 돕는다. */}
            <audio
              controls
              preload="none"
              className="audio-native candidate-audio-el"
              onError={() => setRuntimeExpired(true)}
            >
              <source src={buildAudioUrl(candidate.audioPath!)} type="audio/wav" />
            </audio>
            {expired ? <span className="audio-badge expired">만료됨</span> : null}
          </>
        )}
      </div>
    </div>
  );
}
