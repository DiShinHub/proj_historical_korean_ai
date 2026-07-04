import axios, {
  AxiosError,
  AxiosInstance,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from "axios";
import { env } from "@/config/env";
import { tokenStore } from "./token";
import type { ApiError, ResultVo } from "./types";

// HTTP header names (backend uses lowercase; HTTP headers are case-insensitive).
export const ACCESS_HEADER = "authorization";
export const REFRESH_HEADER = "authorization-refresh";

const MAX_REAUTH_RETRIES = 3;
const REAUTH_RETRY_DELAY_MS = 1000;

function wait(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// A request that has been retried once already should not be retried again.
interface RetryableConfig extends InternalAxiosRequestConfig {
  _retriedAfterAuth?: boolean;
}

export const httpClient: AxiosInstance = axios.create({
  baseURL: env.apiBaseUrl,
  timeout: env.apiTimeoutMs,
  // Backend CORS uses allow_credentials=true and is pinned to localhost:30001.
  withCredentials: true,
});

// Attach the access token to every request.
httpClient.interceptors.request.use((config) => {
  const token = tokenStore.getAccess();
  if (token) {
    config.headers.set(ACCESS_HEADER, token);
  }
  return config;
});

// --- 401 재로그인 처리 상태 ---
let isReauthenticating = false;
let reauthPromise: Promise<void> | null = null;

/** Re-run login up to MAX_REAUTH_RETRIES times (with backoff). Shared across concurrent 401s. */
function reauthenticate(): Promise<void> {
  if (isReauthenticating && reauthPromise) {
    return reauthPromise; // 이미 진행 중이면 그 결과에 편승
  }

  isReauthenticating = true;
  reauthPromise = (async () => {
    // 순환 참조 방지를 위한 동적 import
    const { login } = await import("./auth");

    let lastError: unknown;
    for (let attempt = 1; attempt <= MAX_REAUTH_RETRIES; attempt += 1) {
      try {
        await login(); // 성공 시 내부에서 tokenStore를 갱신한다고 가정
        return;
      } catch (error) {
        lastError = error;
        if (attempt < MAX_REAUTH_RETRIES) {
          await wait(REAUTH_RETRY_DELAY_MS * attempt);
        }
      }
    }
    throw lastError;
  })().finally(() => {
    isReauthenticating = false;
    reauthPromise = null;
  });

  return reauthPromise;
}

// Normalize errors into ApiError, retrying once after re-login on 401.
httpClient.interceptors.response.use(
  (res) => res,
  async (error: AxiosError<ResultVo>) => {
    const originalRequest = error.config as RetryableConfig | undefined;
    const isAuthError = error.response?.status === 401;
    const isLoginEndpoint = originalRequest?.url?.includes("/auth/login");

    if (
      isAuthError &&
      originalRequest &&
      !originalRequest._retriedAfterAuth &&
      !isLoginEndpoint
    ) {
      originalRequest._retriedAfterAuth = true;
      try {
        await reauthenticate();
        // 갱신된 토큰으로 원래 요청을 한 번만 재시도
        return httpClient(originalRequest);
      } catch (reauthError) {
        // 재로그인 자체가 최종 실패한 경우 -> 그대로 에러 전파
        const normalized: ApiError = {
          status: 401,
          message: "재인증에 실패했습니다. 다시 로그인해 주세요.",
          data: undefined,
        };
        return Promise.reject(normalized);
      }
    }

    const normalized: ApiError = {
      status: error.response?.status,
      message:
        error.response?.data?.message ||
        (error.code === "ECONNABORTED"
          ? "요청 시간이 초과되었습니다."
          : error.message) ||
        "요청 중 오류가 발생했습니다.",
      data: error.response?.data,
    };
    return Promise.reject(normalized);
  }
);

/**
 * Unwrap a ResultVo response, throwing on a business-level failure
 * (success === false) even when the HTTP status is 2xx.
 */
export function unwrap<T>(res: AxiosResponse<ResultVo<T>>): T {
  const body = res.data;
  if (body && body.success === false) {
    const err: ApiError = {
      status: res.status,
      message: body.message ?? "요청에 실패했습니다.",
      data: body.data,
    };
    throw err;
  }
  return body?.data as T;
}