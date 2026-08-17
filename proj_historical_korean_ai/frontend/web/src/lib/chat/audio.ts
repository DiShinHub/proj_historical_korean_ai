import { env } from "@/config/env";

/**
 * SYSTEM 메시지 후보(번역 결과) 1건의 오디오 상태.
 *  - play:     재생 가능(정상)
 *  - notexist: audio_path 자체가 없음(오디오 생성 실패로 간주)
 *  - expired:  audio_expire_yn === "Y" 이거나 MinIO 에 실제 오브젝트가 없음(만료로 간주)
 */
export type AudioState = "play" | "notexist" | "expired";

export interface TranslationCandidate {
  text: string;
  ipa?: string | null;
  audioPath?: string | null;
  state: AudioState;
}

export interface CandidateBundle {
  candidates: TranslationCandidate[];
  /** content/audio_path 개수가 달라 바인딩 없이 순차 노출된 경우 true. */
  mismatch: boolean;
}

/** MinIO 오브젝트 경로("/audio/xxx.wav")를 브라우저에서 재생 가능한 URL로 변환한다. */
export function buildAudioUrl(audioPath: string): string {
  const base = env.minioEndpoint.replace(/\/$/, "");
  const bucket = env.minioBucket.replace(/^\/|\/$/g, "");
  const path = audioPath.replace(/^\//, "");
  return `${base}/${bucket}/${path}`;
}

/**
 * content/ipa/audio_path 배열을 후보별 렌더링 정보로 바인딩한다.
 *
 * 정책(AGENTS.md 작업 목표 참고):
 *  - audio_path 가 없음(null) → 전체 notexist
 *  - content 와 audio_path 개수가 다름 → 바인딩하지 않고 순차 노출 + mismatch=true
 *  - 그 외 → 인덱스로 바인딩. audio_expire_yn === "Y" 이거나 개별 path 가 없으면 expired
 */
export function buildCandidates(
  content: string[],
  ipa: (string | null)[] | null | undefined,
  audioPaths: (string | null)[] | null | undefined,
  expired: boolean
): CandidateBundle {
  if (!audioPaths || audioPaths.length === 0) {
    return {
      candidates: content.map((text, i) => ({
        text,
        ipa: ipa?.[i] ?? null,
        audioPath: null,
        state: "notexist",
      })),
      mismatch: false,
    };
  }

  if (content.length !== audioPaths.length) {
    const maxLen = Math.max(content.length, audioPaths.length);
    const candidates: TranslationCandidate[] = [];
    for (let i = 0; i < maxLen; i++) {
      const text = content[i] ?? "(텍스트 없음)";
      const path = audioPaths[i] ?? null;
      candidates.push({
        text,
        ipa: ipa?.[i] ?? null,
        audioPath: path,
        state: !path ? "notexist" : expired ? "expired" : "play",
      });
    }
    return { candidates, mismatch: true };
  }

  return {
    candidates: content.map((text, i) => {
      const path = audioPaths[i] ?? null;
      return {
        text,
        ipa: ipa?.[i] ?? null,
        audioPath: path,
        state: !path ? "notexist" : expired ? "expired" : "play",
      };
    }),
    mismatch: false,
  };
}

/** 소켓 llm_msg 안에서 텍스트/오디오 경로를 구분하는 구분자. */
const SOCKET_DELIM = "^T|A^";

/**
 * 소켓으로 오는 plain text 응답을 파싱한다.
 * 예) "안녕ᄒᆞ신가^T|A^/audio/a.wav\n\n평안ᄒᆞ신가^T|A^/audio/b.wav"
 * 후보가 여러 개면 "\n\n" 으로 구분되어 온다.
 */
export function parseSocketMessage(raw: string): {
  content: string[];
  audioPaths: (string | null)[];
} {
  const parts = raw
    .split(/\n\n+/)
    .map((s) => s.trim())
    .filter(Boolean);

  const content: string[] = [];
  const audioPaths: (string | null)[] = [];

  parts.forEach((part) => {
    const idx = part.indexOf(SOCKET_DELIM);
    if (idx === -1) {
      content.push(part);
      audioPaths.push(null);
      return;
    }
    content.push(part.slice(0, idx).trim());
    audioPaths.push(part.slice(idx + SOCKET_DELIM.length).trim() || null);
  });

  return { content, audioPaths };
}
