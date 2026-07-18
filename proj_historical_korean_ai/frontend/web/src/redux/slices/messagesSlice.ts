import {
  createAsyncThunk,
  createSlice,
  PayloadAction,
} from "@reduxjs/toolkit";
import * as messageApi from "@/lib/api/messages";
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

/**
 * 서버에 저장된 대화 내역을 불러온다(새로고침 시 질문/응답 복원).
 *
 * [role 규약] chat_message.role: "USER" = 사용자 입력, 그 외("SYSTEM"/"ASSISTANT")
 * = 시스템(어시스턴트) 응답. 백엔드는 응답을 "SYSTEM" 으로 저장하므로,
 * "USER" 가 아니면 모두 어시스턴트 버블로 렌더한다.
 */
export const fetchMessages = createAsyncThunk(
  "messages/fetch",
  async (sessionSeq: number) => {
    const rows = await messageApi.listMessages(sessionSeq);
    const messages: ChatMessage[] = rows.map((r) => {
      const isUser = r.role === "USER";
      return {
        id: `srv-${r.seq}`,
        seq: r.seq,
        role: isUser ? "USER" : "ASSISTANT",
        content: r.content,
        status: isUser ? "sent" : "done",
        regDt: r.reg_dt,
      };
    });
    console.log("[API] 대화 내역 로드", sessionSeq, `${messages.length}건`);
    return { sessionSeq, messages };
  }
);

/**
 * 질문 전송(낙관적 렌더).
 *
 * [흐름]  사용자 버블 + 어시스턴트 플레이스홀더 즉시 렌더
 *        → POST /chat_message (USER 메시지 저장 + 백엔드가 worker 태스크 enqueue)
 *        → (이후) worker 가 소켓으로 응답 push → useChatRuntime 가 화면 반영
 *
 * ⚠️ 트리거는 POST /chat_message 하나뿐이다. 이 API 가 USER 메시지 저장과
 * 동시에 Redis 큐(LBS_001)에 worker 태스크를 넣으므로, 별도의 /na/prompts
 * 호출은 하지 않는다(호출하면 한 질문에 응답이 2번 생성됨 → 1질문1응답 위반).
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

    // 상태 변경: 사용자 버블(sending) + 어시스턴트 플레이스홀더(waiting) 추가.
    dispatch(
      optimisticSend({ sessionSeq, userId, assistantId, content, attachmentName })
    );

    // 사용자 메시지 저장 + LLM 태스크 트리거(room_name === chat_session_seq).
    try {
      console.log("[API] 질문 저장", { sessionSeq, content });
      const seq = await messageApi.createMessage(sessionSeq, content);
      // 상태 변경: 사용자 메시지 저장 확정(sent) + 서버 seq 반영.
      dispatch(userMessageConfirmed({ sessionSeq, userId, seq }));
      console.log("[API] 질문 저장 완료 → worker 트리거", { sessionSeq, seq });
    } catch (e) {
      // 상태 변경: 저장 실패 → 사용자 버블 failed, 어시스턴트 플레이스홀더 error.
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

    // 타임아웃 가드 — 정해진 시간 안에 응답이 오지 않으면 오류 표시(+재시도 유도).
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
    /**
     * 단발(1질문→1응답) 완료 처리.
     *
     * 백엔드 worker 는 응답을 한 번의 emit 으로 통째로 보낸다(스트리밍 아님).
     * 그래서 청크 누적(assistantChunk)이 아니라 content 를 통째로 "치환"하고
     * 바로 완료(done) 상태로 만든다.
     *
     * 상태 변경: 대기 중이던 어시스턴트 메시지 → content 채움 + status "done",
     *            그리고 pendingAssistant 해제(사이드바 로딩 자동 제거).
     */
    assistantResolved(
      state,
      action: PayloadAction<{
        sessionSeq: number;
        text: string;
        audioUrl?: string;
        messageSeq?: number;
      }>
    ) {
      const { sessionSeq, text, audioUrl, messageSeq } = action.payload;
      const id = state.pendingAssistant[sessionSeq];
      if (!id) return;
      const m = state.bySession[sessionSeq]?.find((x) => x.id === id);
      if (m) {
        m.content = text;
        m.status = "done";
        if (audioUrl) m.audioUrl = audioUrl;
        if (messageSeq != null) m.seq = messageSeq;
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
  assistantResolved,
  assistantErrored,
  removeMessage,
} = messagesSlice.actions;

export default messagesSlice.reducer;
