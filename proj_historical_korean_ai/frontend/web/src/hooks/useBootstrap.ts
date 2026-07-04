import { useEffect } from "react";
import { useAppDispatch, useAppSelector } from "@/redux/hooks";
import { initAuth } from "@/redux/slices/authSlice";
import { fetchSessions } from "@/redux/slices/sessionsSlice";

/** Authenticate with hardcoded credentials, then load the session list. */
export function useBootstrap(): void {
  const dispatch = useAppDispatch();
  const authStatus = useAppSelector((s) => s.auth.status);

  useEffect(() => {
    if (authStatus === "idle") {
      dispatch(initAuth());
    }
  }, [authStatus, dispatch]);

  useEffect(() => {
    if (authStatus === "authenticated") {
      dispatch(fetchSessions());
    }
  }, [authStatus, dispatch]);
}
