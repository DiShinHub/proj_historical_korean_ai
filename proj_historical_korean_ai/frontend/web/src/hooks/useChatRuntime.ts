import { useEffect } from "react";
import { useAppDispatch } from "@/redux/hooks";
import { getChatSocket } from "@/lib/socket";
import { setSocketStatus } from "@/redux/slices/socketSlice";
import {
  assistantChunk,
  assistantDone,
  assistantErrored,
} from "@/redux/slices/messagesSlice";

/**
 * Owns the socket lifecycle (brief §4.1):
 *  - connect once, wire status + message handlers
 *  - subscribe the active session's room; unsubscribe on switch/unmount
 *  - disconnect on unmount / tab close
 *
 * Response routing is by room_name === chat_session_seq (checkpoint #4).
 */
export function useChatRuntime(activeSeq: number | null): void {
  const dispatch = useAppDispatch();

  // Connect + handlers (once).
  useEffect(() => {
    const socket = getChatSocket();

    const offStatus = socket.onStatus((s) => dispatch(setSocketStatus(s)));
    const offMessage = socket.onMessage((room, payload, envelope) => {
      const sessionSeq = Number(room);
      if (!Number.isFinite(sessionSeq)) return;

      if (envelope.response_code !== 200) {
        dispatch(
          assistantErrored({
            sessionSeq,
            error: envelope.message || "소켓 오류가 발생했습니다.",
          })
        );
        return;
      }

      if (payload.text) {
        dispatch(
          assistantChunk({
            sessionSeq,
            text: payload.text,
            audioUrl: payload.audio_url,
          })
        );
      }
      if (payload.done) {
        dispatch(assistantDone({ sessionSeq, audioUrl: payload.audio_url }));
      }
      // Current backend only echoes {prompt, room_name} with no text/done
      // (checkpoint #2): resolve the placeholder so the UI doesn't hang.
      if (!payload.text && !payload.done && payload.prompt !== undefined) {
        dispatch(assistantDone({ sessionSeq }));
      }
    });

    socket.connect();

    const onBeforeUnload = () => socket.disconnect();
    window.addEventListener("beforeunload", onBeforeUnload);

    return () => {
      window.removeEventListener("beforeunload", onBeforeUnload);
      offStatus();
      offMessage();
      socket.disconnect();
    };
  }, [dispatch]);

  // Subscribe to the active room; swap on change.
  useEffect(() => {
    if (activeSeq == null || activeSeq < 0) return;
    const socket = getChatSocket();
    const room = String(activeSeq);
    socket.subscribe(room);
    return () => socket.unsubscribe(room);
  }, [activeSeq]);
}
