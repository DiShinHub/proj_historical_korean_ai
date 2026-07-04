import {
  createAsyncThunk,
  createSlice,
  PayloadAction,
} from "@reduxjs/toolkit";
import * as sessionApi from "@/lib/api/sessions";
import type { ApiError } from "@/lib/api/types";

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
  { title: string },
  { rejectValue: { tempId: number; message: string } }
>("sessions/create", async ({ title }, { dispatch, rejectWithValue }) => {
  const tempId = nextTempId();
  // Optimistic insert.
  dispatch(sessionAdded({ seq: tempId, title, optimistic: true }));
  dispatch(setActiveSession(tempId));
  try {
    const seq = await sessionApi.createSession(title);
    return { tempId, seq, title };
  } catch (e) {
    dispatch(sessionRemoved(tempId)); // rollback
    return rejectWithValue({ tempId, message: (e as ApiError).message });
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
        const { tempId, seq, title } = action.payload;
        const item = state.items.find((s) => s.seq === tempId);
        if (item) {
          item.seq = seq;
          item.title = title;
          item.optimistic = false;
        }
        if (state.activeSeq === tempId) state.activeSeq = seq;
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
