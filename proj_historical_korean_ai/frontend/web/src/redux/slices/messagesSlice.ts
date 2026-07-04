import {
  createAsyncThunk,
  createSlice,
  PayloadAction,
} from "@reduxjs/toolkit";
import * as messageApi from "@/lib/api/messages";
import { sendPrompt } from "@/lib/api/prompts";
import type { ApiError } from "@/lib/api/types";
import { env } from "@/config/env";
import { mockBus } from "@/lib/socket";
import { uuid } from "@/lib/uuid";

export type MessageStatus =
  | "sending" // user msg being persisted
  | "sent" // user msg persisted
  | "failed" // user msg failed to send
  | "waiting" // assistant placeholder, no chunk yet
  | "streaming" // assistant receiving chunks
  | "done" // assistant complete
  | "error"; // assistant errored / timed out

export interface ChatMessage {
  id: string; // client id
  seq?: number; // server seq once persisted
  role: "USER" | "ASSISTANT";
  content: string;
  status: MessageStatus;
  regDt?: string;
  audioUrl?: string;
  error?: string;
  attachmentName?: string; // PDF filename (frontend-only, checkpoint #7)
}

/** How long to wait for the first assistant chunk before timing out (ms). */
export const ASSISTANT_TIMEOUT_MS = 45_000;

interface MessagesState {
  bySession: Record<number, ChatMessage[]>;
  statusBySession: Record<number, "idle" | "loading" | "loaded" | "error">;
  // client id of the assistant placeholder currently awaiting a response.
  pendingAssistant: Record<number, string | undefined>;
}

const initialState: MessagesState = {
  bySession: {},
  statusBySession: {},
  pendingAssistant: {},
};

function list(state: MessagesState, seq: number): ChatMessage[] {
  return (state.bySession[seq] ??= []);
}

export const fetchMessages = createAsyncThunk(
  "messages/fetch",
  async (sessionSeq: number) => {
    const rows = await messageApi.listMessages(sessionSeq);
    const messages: ChatMessage[] = rows.map((r) => ({
      id: `srv-${r.seq}`,
      seq: r.seq,
      role: r.role === "ASSISTANT" ? "ASSISTANT" : "USER",
      content: r.content,
      status: r.role === "ASSISTANT" ? "done" : "sent",
      regDt: r.reg_dt,
    }));
    return { sessionSeq, messages };
  }
);

/**
 * Optimistic send: renders the user bubble + an assistant placeholder
 * immediately, persists the user message, then triggers the LLM task.
 * The assistant answer arrives asynchronously via the socket (see
 * messagesSlice `assistantChunk` / `assistantDone`, dispatched by useChatSocket).
 */
export const sendMessage = createAsyncThunk(
  "messages/send",
  async (
    args: { sessionSeq: number; content: string; attachmentName?: string },
    { dispatch, getState }
  ) => {
    const { sessionSeq, content, attachmentName } = args;
    const userId = uuid();
    const assistantId = uuid();

    dispatch(
      optimisticSend({ sessionSeq, userId, assistantId, content, attachmentName })
    );

    // 1. Persist the user message (best effort).
    try {
      const seq = await messageApi.createMessage(sessionSeq, content);
      dispatch(userMessageConfirmed({ sessionSeq, userId, seq }));
    } catch (e) {
      dispatch(userMessageFailed({ sessionSeq, userId }));
      dispatch(
        assistantErrored({
          sessionSeq,
          assistantId,
          error: "메시지 저장에 실패했습니다.",
        })
      );
      throw e;
    }

    // 2. Trigger the LLM task. room_name === chat_session_seq (checkpoint #4).
    const roomName = String(sessionSeq);
    try {
      await sendPrompt(content, roomName);
      if (env.useMockSocket) mockBus.emitPrompt(roomName, content);
    } catch (e) {
      dispatch(
        assistantErrored({
          sessionSeq,
          assistantId,
          error: "요청 전송에 실패했습니다.",
        })
      );
      throw e;
    }

    // 3. Timeout guard — if no chunk arrives, surface an error + retry.
    setTimeout(() => {
      const s = getState() as { messages: MessagesState };
      const msg = s.messages.bySession[sessionSeq]?.find(
        (m) => m.id === assistantId
      );
      if (msg && msg.status === "waiting") {
        dispatch(
          assistantErrored({
            sessionSeq,
            assistantId,
            error: "응답 시간이 초과되었습니다.",
          })
        );
      }
    }, ASSISTANT_TIMEOUT_MS);
  }
);

const messagesSlice = createSlice({
  name: "messages",
  initialState,
  reducers: {
    optimisticSend(
      state,
      action: PayloadAction<{
        sessionSeq: number;
        userId: string;
        assistantId: string;
        content: string;
        attachmentName?: string;
      }>
    ) {
      const { sessionSeq, userId, assistantId, content, attachmentName } =
        action.payload;
      const msgs = list(state, sessionSeq);
      msgs.push({
        id: userId,
        role: "USER",
        content,
        status: "sending",
        attachmentName,
      });
      msgs.push({
        id: assistantId,
        role: "ASSISTANT",
        content: "",
        status: "waiting",
      });
      state.pendingAssistant[sessionSeq] = assistantId;
    },
    userMessageConfirmed(
      state,
      action: PayloadAction<{
        sessionSeq: number;
        userId: string;
        seq: number | null;
      }>
    ) {
      const m = state.bySession[action.payload.sessionSeq]?.find(
        (x) => x.id === action.payload.userId
      );
      if (m) {
        m.status = "sent";
        if (action.payload.seq != null) m.seq = action.payload.seq;
      }
    },
    userMessageFailed(
      state,
      action: PayloadAction<{ sessionSeq: number; userId: string }>
    ) {
      const m = state.bySession[action.payload.sessionSeq]?.find(
        (x) => x.id === action.payload.userId
      );
      if (m) m.status = "failed";
    },
    /** Append an assistant chunk (delta). */
    assistantChunk(
      state,
      action: PayloadAction<{
        sessionSeq: number;
        text: string;
        audioUrl?: string;
      }>
    ) {
      const { sessionSeq, text, audioUrl } = action.payload;
      const id = state.pendingAssistant[sessionSeq];
      if (!id) return;
      const m = state.bySession[sessionSeq]?.find((x) => x.id === id);
      if (!m) return;
      m.content += text;
      m.status = "streaming";
      if (audioUrl) m.audioUrl = audioUrl;
    },
    /** Mark the pending assistant message complete. */
    assistantDone(
      state,
      action: PayloadAction<{ sessionSeq: number; audioUrl?: string }>
    ) {
      const { sessionSeq, audioUrl } = action.payload;
      const id = state.pendingAssistant[sessionSeq];
      if (!id) return;
      const m = state.bySession[sessionSeq]?.find((x) => x.id === id);
      if (m) {
        m.status = "done";
        if (audioUrl) m.audioUrl = audioUrl;
      }
      state.pendingAssistant[sessionSeq] = undefined;
    },
    assistantErrored(
      state,
      action: PayloadAction<{
        sessionSeq: number;
        assistantId?: string;
        error: string;
      }>
    ) {
      const { sessionSeq, error } = action.payload;
      const id = action.payload.assistantId ?? state.pendingAssistant[sessionSeq];
      const m = id
        ? state.bySession[sessionSeq]?.find((x) => x.id === id)
        : undefined;
      if (m) {
        m.status = "error";
        m.error = error;
      }
      state.pendingAssistant[sessionSeq] = undefined;
    },
    removeMessage(
      state,
      action: PayloadAction<{ sessionSeq: number; id: string }>
    ) {
      const arr = state.bySession[action.payload.sessionSeq];
      if (arr) {
        state.bySession[action.payload.sessionSeq] = arr.filter(
          (m) => m.id !== action.payload.id
        );
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchMessages.pending, (state, action) => {
        state.statusBySession[action.meta.arg] = "loading";
      })
      .addCase(fetchMessages.fulfilled, (state, action) => {
        const { sessionSeq, messages } = action.payload;
        // Preserve any in-flight optimistic messages not yet persisted.
        const pending = (state.bySession[sessionSeq] ?? []).filter(
          (m) => m.seq == null && m.status !== "done"
        );
        state.bySession[sessionSeq] = [...messages, ...pending];
        state.statusBySession[sessionSeq] = "loaded";
      })
      .addCase(fetchMessages.rejected, (state, action) => {
        state.statusBySession[action.meta.arg] = "error";
      });
  },
});

export const {
  optimisticSend,
  userMessageConfirmed,
  userMessageFailed,
  assistantChunk,
  assistantDone,
  assistantErrored,
  removeMessage,
} = messagesSlice.actions;

export default messagesSlice.reducer;
