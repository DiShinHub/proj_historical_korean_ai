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

function deriveWsUrl(host: string, port: string): string {
  // Assumed browser-facing bridge endpoint. The current backend socket is a
  // raw TCP server unreachable from a browser — see backend checkpoint #1.
  const secure = host.startsWith("https");
  const bare = host.replace(/^https?:\/\//, "");
  return `${secure ? "wss" : "ws"}://${bare}:${port}/ws`;
}

const host = process.env.NEXT_PUBLIC_FASTAPI_APP_HOST || "http://localhost";
const port = process.env.NEXT_PUBLIC_FASTAPI_APP_PORT || "28001";

export const env = {
  apiBaseUrl: `${host}:${port}`,
  apiTimeoutMs: readTimeoutMs(),
  wsUrl: process.env.NEXT_PUBLIC_WS_URL || deriveWsUrl(host, port),
  // Default ON: there is no browser-consumable socket yet (checkpoint #1), so
  // the mock lets the full send -> typing -> response UX run end to end.
  useMockSocket: (process.env.NEXT_PUBLIC_USE_MOCK_SOCKET ?? "true") !== "false",
};
