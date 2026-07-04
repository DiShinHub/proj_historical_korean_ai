import {
  ACCESS_HEADER,
  REFRESH_HEADER,
  httpClient,
  unwrap,
} from "./client";
import { tokenStore } from "./token";
import { ADMIN_CREDENTIALS } from "@/config/credentials";
import type { MeDto, ResultVo } from "./types";

function readTokenHeaders(headers: Record<string, unknown>): {
  access: string | null;
  refresh: string | null;
} {
  // axios lowercases response header keys.
  const access = (headers[ACCESS_HEADER] as string) ?? null;
  const refresh = (headers[REFRESH_HEADER] as string) ?? null;
  return { access, refresh };
}

/** POST /na/auth/login — tokens arrive in RESPONSE HEADERS, not the body. */
export async function login(): Promise<void> {
  const res = await httpClient.post<ResultVo>(
    "/api/v1/na/auth/login",
    ADMIN_CREDENTIALS
  );
  const { access, refresh } = readTokenHeaders(res.headers as Record<string, unknown>);
  if (!access) {
    throw {
      status: res.status,
      message:
        "로그인 응답에 access token 헤더가 없습니다. (백엔드 CORS expose_headers 확인 필요)",
    };
  }
  tokenStore.setTokens(access, refresh);
}

/** POST /na/auth/refresh — reads current tokens from headers, returns new ones. */
export async function refresh(): Promise<boolean> {
  const current = tokenStore.getRefresh();
  if (!current) return false;
  const res = await httpClient.post<ResultVo>("/api/v1/na/auth/refresh", null, {
    headers: {
      [ACCESS_HEADER]: tokenStore.getAccess() ?? "",
      [REFRESH_HEADER]: current,
    },
  });
  const { access, refresh: newRefresh } = readTokenHeaders(
    res.headers as Record<string, unknown>
  );
  if (!access) return false;
  tokenStore.setTokens(access, newRefresh ?? current);
  return true;
}

/** GET /au/users/me */
export async function fetchMe(): Promise<MeDto> {
  const res = await httpClient.get<ResultVo<MeDto>>("/api/v1/au/users/me");
  return unwrap(res);
}

// ---- Auto-refresh on 401 (registered once) ----
let refreshing: Promise<boolean> | null = null;

httpClient.interceptors.response.use(undefined, async (error) => {
  const original = error?.config;
  const status = error?.status ?? error?.response?.status;
  if (
    status === 401 &&
    original &&
    !original.__isRetry &&
    tokenStore.getRefresh()
  ) {
    original.__isRetry = true;
    refreshing =
      refreshing ??
      refresh().finally(() => {
        refreshing = null;
      });
    const ok = await refreshing.catch(() => false);
    if (ok) {
      original.headers = original.headers ?? {};
      original.headers[ACCESS_HEADER] = tokenStore.getAccess();
      return httpClient(original);
    }
  }
  return Promise.reject(error);
});
