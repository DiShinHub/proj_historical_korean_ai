import {
  createAsyncThunk,
  createSlice,
  PayloadAction,
} from "@reduxjs/toolkit";
import * as sessionApi from "@/lib/api/sessions";
import type { ApiError } from "@/lib/api/types";
import { getChatSocket } from "@/lib/socket";

export interface ChatSession {
  seq: number; // negative = optimistic temp id not yet confirmed
  title: string;
  regDt?: string;
  optimistic?: boolean;
}

interface SessionsState {
  items: ChatSession[];
  activeSeq: number | null;
  status: "idle" | "loading" | "loaded" | "error";
  error: string | null;
}

const initialState: SessionsState = {
  items: [],
  activeSeq: null,
  status: "idle",
  error: null,
};

let tempIdCounter = -1;
const nextTempId = () => tempIdCounter--;

export const fetchSessions = createAsyncThunk("sessions/fetch", async () => {
  const list = await sessionApi.listSessions();
  return list.map<ChatSession>((s) => ({
    seq: s.seq,
    title: s.title,
    regDt: s.reg_dt,
  }));
});

export const createSession = createAsyncThunk<
  { tempId: number; seq: number; title: string },
  { title?: string },
  { rejectValue: { message: string } }
>("sessions/create", async ({ title = "새 대화" }, { dispatch, getState, rejectWithValue }) => {
  const state = getState() as {
    sessions: SessionsState;
    messages: { pendingAssistant: Record<number, string | undefined> };
  };

  const prev = state.sessions.activeSeq;
  const tempId = nextTempId();

  // 1. 이전 활성 세션 정리 (switchSession과 동일한 cleanup 처리)
  if (prev != null && prev > 0) {
    sessionApi
      .updateSession(prev, { status: "inactive" })
      .catch((e) => console.warn("[API] 이전 세션 inactive 실패", prev, e));

    const awaiting = Boolean(state.messages.pendingAssistant[prev]);
    if (awaiting) {
      console.log("[Socket] 이전 세션 응답 대기 중 → Room 유지", prev);
    } else {
      const socket = getChatSocket();
      socket.unsubscribe(String(prev));
    }
  }

  // 2. UI에 즉시 반영 (Optimistic)
  dispatch(
    sessionAdded({
      seq: tempId,
      title,
      optimistic: true,
    })
  );
  dispatch(setActiveSession(tempId));

  try {
    // 3. 백엔드 세션 생성 API 호출
    const seq = await sessionApi.createSession(title);
    return { tempId, seq, title };
  } catch (e) {
    // 실패 시 임시 세션 제거 및 이전 세션 상태 복구 검토
    dispatch(sessionRemoved(tempId));
    return rejectWithValue({ message: (e as ApiError).message });
  }
});

export const renameSession = createAsyncThunk(
  "sessions/rename",
  async (
    { seq, title }: { seq: number; title: string },
    { dispatch, getState }
  ) => {
    const state = getState() as { sessions: SessionsState };
    const prev = state.sessions.items.find((s) => s.seq === seq)?.title ?? "";
    
    dispatch(sessionRenamed({ seq, title })); // optimistic UI update
    
    try {
      await sessionApi.updateSession(seq, { title });
    } catch (e) {
      dispatch(sessionRenamed({ seq, title: prev })); // rollback on failure
      throw e;
    }
  }
);

export const deleteSession = createAsyncThunk(
  "sessions/delete",
  async (seq: number, { dispatch, getState }) => {
    const state = getState() as { sessions: SessionsState };
    const snapshot = state.sessions.items.find((s) => s.seq === seq);
    const wasActive = state.sessions.activeSeq === seq;
    
    dispatch(sessionRemoved(seq)); // optimistic
    if (seq > 0) getChatSocket().unsubscribe(String(seq));
    
    if (wasActive) {
      const remaining = state.sessions.items.filter((s) => s.seq !== seq);
      dispatch(setActiveSession(remaining[0]?.seq ?? null));
    }
    
    try {
      await sessionApi.deleteSession(seq);
    } catch (e) {
      if (snapshot) dispatch(sessionAdded(snapshot)); // rollback
      throw e;
    }
  }
);

export const switchSession = createAsyncThunk(
  "sessions/switch",
  async (seq: number, { dispatch, getState }) => {
    const state = getState() as {
      sessions: SessionsState;
      messages: { pendingAssistant: Record<number, string | undefined> };
    };

    const prev = state.sessions.activeSeq;
    if (prev === seq) return;

    const socket = getChatSocket();

    console.log("[Sidebar] Active Session 변경", { prev, next: seq });
    dispatch(setActiveSession(seq));

    if (prev != null && prev > 0) {
      sessionApi
        .updateSession(prev, { status: "inactive" })
        .catch((e) => console.warn("[API] 이전 세션 inactive 실패", prev, e));

      const awaiting = Boolean(state.messages.pendingAssistant[prev]);
      if (awaiting) {
        console.log("[Socket] 이전 세션 응답 대기 중 → Room 유지", prev);
      } else {
        socket.unsubscribe(String(prev));
      }
    }

    if (seq > 0) {
      const now = new Date();
      const offset = now.getTimezoneOffset() * 60000;
      const activateDt = new Date(now.getTime() - offset).toISOString().slice(0, 19);
      sessionApi
        .updateSession(seq, { status: "active", activate_dt: activateDt })
        .catch((e) => console.warn("[API] 새 세션 active 실패", seq, e));
    }
  }
);

const sessionsSlice = createSlice({
  name: "sessions",
  initialState,
  reducers: {
    setActiveSession(state, action: PayloadAction<number | null>) {
      state.activeSeq = action.payload;
    },
    sessionAdded(state, action: PayloadAction<ChatSession>) {
      if (!state.items.some((s) => s.seq === action.payload.seq)) {
        state.items.unshift(action.payload);
      }
    },
    sessionRemoved(state, action: PayloadAction<number>) {
      state.items = state.items.filter((s) => s.seq !== action.payload);
    },
    sessionRenamed(
      state,
      action: PayloadAction<{ seq: number; title: string }>
    ) {
      const s = state.items.find((x) => x.seq === action.payload.seq);
      if (s) s.title = action.payload.title;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchSessions.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(fetchSessions.fulfilled, (state, action) => {
        state.status = "loaded";
        state.items = action.payload;
        if (
          state.activeSeq == null ||
          !action.payload.some((s) => s.seq === state.activeSeq)
        ) {
          state.activeSeq = action.payload[0]?.seq ?? null;
        }
      })
      .addCase(fetchSessions.rejected, (state, action) => {
        state.status = "error";
        state.error = action.error.message ?? "세션을 불러오지 못했습니다.";
      })
      // 음수 tempId를 실제 발급된 seq로 치환 (Reconcile)
      .addCase(createSession.fulfilled, (state, action) => {
        const { tempId, seq, title } = action.payload;
        const item = state.items.find((s) => s.seq === tempId);
        if (item) {
          item.seq = seq;
          item.title = title;
          item.optimistic = false;
        }
        if (state.activeSeq === tempId) {
          state.activeSeq = seq;
        }
      });
  },
});

export const {
  setActiveSession,
  sessionAdded,
  sessionRemoved,
  sessionRenamed,
} = sessionsSlice.actions;

export default sessionsSlice.reducer;