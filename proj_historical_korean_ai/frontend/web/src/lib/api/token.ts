// In-memory token store — the single source of truth the axios request
// interceptor reads synchronously. Tokens are AES-encrypted blobs returned in
// the login RESPONSE HEADERS (not the body), so we never decode them here.

let accessToken: string | null = null;
let refreshToken: string | null = null;

export const tokenStore = {
  getAccess: (): string | null => accessToken,
  getRefresh: (): string | null => refreshToken,
  setTokens: (access: string | null, refresh: string | null): void => {
    accessToken = access;
    refreshToken = refresh;
  },
  clear: (): void => {
    accessToken = null;
    refreshToken = null;
  },
};
