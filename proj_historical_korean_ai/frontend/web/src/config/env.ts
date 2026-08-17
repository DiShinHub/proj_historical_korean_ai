// Centralized environment access.
//
// NOTE: the repo's docker env sets NEXT_PUBLIC_API_TIMEOUT=5, and the original
// api/index.ts fed that straight into axios `timeout` (milliseconds) — a 5ms
// timeout that fails every request. We interpret small values as SECONDS.

function readTimeoutMs(): number {
  const raw = Number(process.env.NEXT_PUBLIC_API_TIMEOUT);
  if (!raw || Number.isNaN(raw)) return 30_000;
  // The docker env uses "5" (seconds). Anything <= 300 is treated as seconds.
  return raw <= 300 ? raw * 1000 : raw;
}
const host = process.env.NEXT_PUBLIC_FASTAPI_APP_HOST || "http://localhost";
const port = process.env.NEXT_PUBLIC_FASTAPI_APP_PORT || "28001";

// HTTP(S) 주소. 예: "http://localhost:28001"
const apiBaseUrl = `${host}:${port}`;

/**
 * HTTP 주소를 WebSocket 주소로 변환한다.
 *
 * host 값에는 스킴(http:// 또는 https://)이 이미 포함되어 있으므로,
 * 단순히 앞에 "ws://" 를 붙이면 "ws://http://localhost..." 처럼
 * 잘못된 주소가 만들어진다(브라우저가 연결 실패). 따라서 스킴을 치환한다.
 *   http  -> ws
 *   https -> wss
 * 백엔드 WebSocket 엔드포인트 경로는 "/websocket/ws".
 */
function toWebSocketUrl(httpUrl: string): string {
  const wsBase = httpUrl.replace(/^http(s?):\/\//, (_m, s) => `ws${s}://`);
  return `${wsBase}/websocket/ws`;
}

// audio_path(예: "/audio/output_xxx.wav")를 재생 가능한 URL로 만들기 위한
// MinIO 엔드포인트/버킷. 백엔드 properties 와 별개로 브라우저가 직접
// MinIO 오브젝트를 조회하므로(익명 다운로드 정책 전제) 프론트 env 로 노출한다.
// 값이 없으면 로컬 개발 docker-compose 기준 기본값을 사용한다.
const minioEndpoint =
  process.env.NEXT_PUBLIC_MINIO_ENDPOINT || "http://localhost:9000";
const minioBucket = process.env.NEXT_PUBLIC_MINIO_BUCKET || "hkai-bucket";

export const env = {
  apiBaseUrl,
  apiTimeoutMs: readTimeoutMs(),
  wsUrl: toWebSocketUrl(apiBaseUrl),
  minioEndpoint,
  minioBucket,
};
