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
  { seq: number; title: string },
  { title: string },
  { rejectValue: { message: string } }
>("sessions/create", async ({ title }, { dispatch, rejectWithValue }) => {

  const tempId = nextTempId();

  // Optimistic insert.
  
  
  try {
    const seq = await sessionApi.createSession(title);
    dispatch(sessionAdded({ seq: seq, title, optimistic: true }));
    dispatch(switchSession(seq));
    return { seq, title };
  } catch (e) {
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
    dispatch(sessionRenamed({ seq, title })); // optimistic
    try {
      await sessionApi.updateSession(seq, { title });
    } catch (e) {
      dispatch(sessionRenamed({ seq, title: prev })); // rollback
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
    // 삭제된 세션의 Room 에서 나간다(더 이상 응답을 받을 필요 없음).
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

/**
 * 세션 전환(사이드바 Room 정책).
 *
 * 브리프에서 정한 순서를 그대로 오케스트레이션한다:
 *   1. 새 세션을 Active 로 표시
 *   2. (백엔드) 이전 세션 status=inactive
 *   3. Room 처리: 이전 세션이 "응답 대기 중"이면 Leave 하지 않고 유지,
 *      완료 상태면 Leave. (새 세션 Join 은 useChatRuntime 의 활성-room effect 담당)
 *   4. (백엔드) 새 세션 status=active + activate_dt
 *   5. 세션 리스트 갱신
 *
 * 참고: 새 세션 Room Join 은 setActiveSession 직후 useChatRuntime 의
 * "활성 Room 구독" effect 가 수행하므로 여기서 중복 호출하지 않는다.
 */
export const switchSession = createAsyncThunk(
  "sessions/switch",
  async (seq: number, { dispatch, getState }) => {
    const state = getState() as {
      sessions: SessionsState;
      messages: { pendingAssistant: Record<number, string | undefined> };
    };

    const prev = state.sessions.activeSeq;
    if (prev === seq) return; // 같은 세션 클릭 → 아무것도 안 함

    const socket = getChatSocket();

    // 1. 새 세션 Active
    console.log("[Sidebar] Active Session 변경", { prev, next: seq });
    dispatch(setActiveSession(seq));

    // 2·3. 이전 세션 정리(비활성화 + 조건부 Room Leave)
    if (prev != null && prev > 0) {
      // 2. 백엔드에 이전 세션 inactive 통보(best-effort)
      sessionApi
        .updateSession(prev, { status: "inactive" })
        .catch((e) => console.warn("[API] 이전 세션 inactive 실패", prev, e));

      // 3. 이전 세션이 아직 응답을 기다리는 중이면 Room 을 유지한다.
      //    (Leave 하면 늦게 도착하는 응답을 못 받는다.)
      const awaiting = Boolean(state.messages.pendingAssistant[prev]);
      if (awaiting) {
        console.log("[Socket] 이전 세션 응답 대기 중 → Room 유지", prev);
      } else {
        socket.unsubscribe(String(prev)); // 완료 세션 → Leave
      }
    }

    // 4. 새 세션 active + activate_dt (초 단위 ISO; Python fromisoformat 호환)
    if (seq > 0) {
      const activateDt = new Date().toISOString().slice(0, 19); // "YYYY-MM-DDTHH:MM:SS"
      sessionApi
        .updateSession(seq, { status: "active", activate_dt: activateDt })
        .catch((e) => console.warn("[API] 새 세션 active 실패", seq, e));
    }

    // // 5. 세션 리스트 갱신(정렬/상태 최신화)
    // dispatch(fetchSessions());
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
      // Reconcile optimistic temp id -> real seq.
      .addCase(createSession.fulfilled, (state, action) => {
        // const { tempId, seq, title } = action.payload;
        // const item = state.items.find((s) => s.seq === tempId);
        // if (item) {
        //   item.seq = seq;
        //   item.title = title;
        //   item.optimistic = false;
        // }
        // if (state.activeSeq === tempId) state.activeSeq = seq;
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
