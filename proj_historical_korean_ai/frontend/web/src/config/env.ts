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

export const env = {
  apiBaseUrl: `${host}:${port}`,
  apiTimeoutMs: readTimeoutMs(),
  wsUrl: `ws://${host}:${port}/websocket/ws`,
};
