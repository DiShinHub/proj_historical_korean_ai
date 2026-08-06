import { useEffect } from "react";
import { useAppDispatch, useAppSelector } from "@/redux/hooks";
import { initAuth } from "@/redux/slices/authSlice";
import type { AuthStatus } from "@/redux/slices/authSlice";

/**
 * 인증만 수행하는 부트스트랩.
 *
 * `useBootstrap` 은 인증 후 채팅 세션 목록까지 조회하는데,
 * 사전 관리 화면은 채팅 세션이 필요 없다. 불필요한 요청과
 * 채팅 Redux 상태 오염을 피하려고 인증 단계만 따로 뽑았다.
 *
 * hk_dictionary 의 POST/PUT/DELETE/dump 는 `au`(authenticated) 라우터라
 * access token 이 반드시 있어야 한다. (GET 도 같은 prefix 이므로 동일)
 */
export function useAuthBootstrap(): { status: AuthStatus; error: string | null } {
  const dispatch = useAppDispatch();
  const status = useAppSelector((s) => s.auth.status);
  const error = useAppSelector((s) => s.auth.error);

  useEffect(() => {
    if (status === "idle") {
      dispatch(initAuth());
    }
  }, [status, dispatch]);

  return { status, error };
}
