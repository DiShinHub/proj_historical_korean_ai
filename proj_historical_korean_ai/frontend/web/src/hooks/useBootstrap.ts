import { useEffect } from "react";
import { useAppDispatch, useAppSelector } from "@/redux/hooks";
import { initAuth } from "@/redux/slices/authSlice";
import { fetchSessions } from "@/redux/slices/sessionsSlice";

/** 하드코딩된 자격증명으로 인증한 뒤, 세션 목록을 불러온다. */
export function useBootstrap(): void {
  const dispatch = useAppDispatch();
  const authStatus = useAppSelector((s) => s.auth.status);

  // 앱 최초 진입(authStatus === "idle")일 때만 인증 시도.
  useEffect(() => {
    if (authStatus === "idle") {
      dispatch(initAuth());
    }
  }, [authStatus, dispatch]);

  // 인증이 성공적으로 끝났을 때 세션 목록을 서버에서 조회한다.
  useEffect(() => {
    if (authStatus === "authenticated") {
      dispatch(fetchSessions());
    }
  }, [authStatus, dispatch]);
}
