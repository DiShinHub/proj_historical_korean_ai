import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { fetchMe, login } from "@/lib/api/auth";
import type { MeDto } from "@/lib/api/types";

export type AuthStatus = "idle" | "loading" | "authenticated" | "error";

interface AuthState {
  status: AuthStatus;
  me: MeDto | null;
  error: string | null;
}

const initialState: AuthState = {
  status: "idle",
  me: null,
  error: null,
};

/** 하드코딩 된 인증정보로 로그인. */
export const initAuth = createAsyncThunk("auth/init", async () => {
  await login();
  const me = await fetchMe().catch(() => null);
  return me;
});

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(initAuth.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(initAuth.fulfilled, (state, action) => {
        state.status = "authenticated";
        state.me = action.payload;
      })
      .addCase(initAuth.rejected, (state, action) => {
        state.status = "error";
        state.error = action.error.message ?? "인증에 실패했습니다.";
      });
  },
});

export default authSlice.reducer;
