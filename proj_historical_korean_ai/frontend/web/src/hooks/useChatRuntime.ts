import { useEffect, useRef } from "react";
import { useAppDispatch } from "@/redux/hooks";
import { getChatSocket } from "@/lib/socket";
import { setSocketStatus } from "@/redux/slices/socketSlice";
import {
  assistantChunk,
  assistantResolved,
  assistantErrored,
} from "@/redux/slices/messagesSlice";
import { buildCandidates, parseSocketMessage } from "@/lib/chat/audio";

/**
 * 소켓 생명주기와 응답 라우팅을 담당하는 훅.
 *
 * [전체 흐름]
 *   질문 저장(API) → 백엔드 worker 실행 → worker 가 소켓 room 으로 응답 push
 *   → 브라우저 수신 → 이 훅의 onMessage 핸들러 → Redux 반영 → 화면 갱신
 *
 * 응답은 room_name(=chat_session_seq)으로 어느 세션의 응답인지 구분한다.
 *
 * Room 정책(브리프):
 *  - 활성 세션의 room 은 항상 Join 상태를 유지한다(아래 Effect B).
 *  - 세션 전환 시 이전 room 은 무조건 Leave 하지 않는다. 응답 대기 중이면 유지하고,
 *    응답이 도착하는 순간(백그라운드 세션) 이 핸들러가 Leave 한다.
 */
export function useChatRuntime(activeSeq: number | null): void {
  const dispatch = useAppDispatch();

  // onMessage 핸들러(한 번만 등록됨) 안에서 "지금 활성 세션이 무엇인지"를
  // 최신 값으로 참조하기 위한 ref. state 를 클로저로 가두지 않도록 ref 사용.
  const activeSeqRef = useRef<number | null>(activeSeq);
  activeSeqRef.current = activeSeq;

  // ── Effect A: 소켓 연결 + 상태/메시지 핸들러 등록(최초 1회) ──────────────
  useEffect(() => {
    const socket = getChatSocket();

    // 소켓 연결 상태를 Redux 로 흘려보내 사이드바 표시등에 반영한다.
    const offStatus = socket.onStatus((s) => dispatch(setSocketStatus(s)));

    // [소켓 이벤트] 룸으로 들어온 응답 처리
    const offMessage = socket.onMessage((room, payload, envelope) => {
      // room_name → 세션 seq. 숫자로 변환되지 않으면(ack 등) 무시.
      const sessionSeq = Number(room);
      if (!room || !Number.isFinite(sessionSeq) || sessionSeq <= 0) return;

      console.log("[Socket] 응답 수신(라우팅)", { sessionSeq, payload });

      // 서버가 명시적으로 오류 코드를 준 경우 → 오류 처리.
      if (envelope.response_code != null && envelope.response_code !== 200) {
        dispatch(
          assistantErrored({
            sessionSeq,
            error: envelope.message || "소켓 오류가 발생했습니다.",
          })
        );
        return;
      }

      // 응답 텍스트 추출(과도기 방어: llm_msg → text 순).
      const text =
        payload.llm_msg ?? payload.text ?? "";

      const result =
        payload.result ??  "";

      // done === false 인 경우에만 "스트리밍 청크"로 취급.
      // 그 외에는 백엔드의 단발(1질문→1응답) emit 으로 보고 완료 처리한다.
      if (payload.done === false) {
        dispatch(
          assistantChunk({ sessionSeq, text, audioUrl: payload.audio_url })
        );
        return;
      }

      // ── 응답 완료(1응답) ──
      // 소켓 텍스트는 "text^T|A^audio_path" 형태이며, 후보가 여러 개면
      // "\n\n" 으로 이어져 온다(데이터 API 조회와 동일한 UI 로 노출해야 함).
      const { content, audioPaths } = parseSocketMessage(text);
      const { candidates, mismatch } = buildCandidates(content, null, audioPaths, false);
      dispatch(
        assistantResolved({
          sessionSeq,
          text: content.join("\n\n"),
          candidates,
          audioMismatch: mismatch,
          audioUrl: payload.audio_url,
          messageSeq: payload.message_seq,
        })
      );
      console.log("[Chat] 응답 화면 반영", sessionSeq);

      // Room 정책: 응답을 받은 세션이 "지금 보고 있는 활성 세션이 아니면"
      // (= 백그라운드에서 대기하던 세션) 이제 응답이 끝났으니 Room 을 Leave 한다.
      // 활성 세션이면 계속 보고 있으므로 Room 을 유지한다.
      if (activeSeqRef.current !== sessionSeq) {
        console.log("[Socket] 백그라운드 세션 응답 완료 → Room Leave", sessionSeq);
        socket.unsubscribe(String(sessionSeq));
      }
    });

    // 연결 시작.
    socket.connect();

    // 탭을 닫을 때 정리.
    const onBeforeUnload = () => socket.disconnect();
    window.addEventListener("beforeunload", onBeforeUnload);

    // 훅 언마운트(채팅 화면 이탈) 시 정리.
    return () => {
      window.removeEventListener("beforeunload", onBeforeUnload);
      offStatus();
      offMessage();
      socket.disconnect();
    };
  }, [dispatch]);

  // ── Effect B: 활성 세션의 Room 구독(Join) ───────────────────────────────
  // activeSeq 가 바뀔 때마다 새 활성 room 에 Join 한다(멱등).
  // ⚠️ cleanup 에서 unsubscribe(Leave) 하지 않는다. 이전 세션의 Leave 는
  //    switchSession(완료 세션) 또는 onMessage(대기하다 응답 온 세션)가 담당한다.
  //    여기서 무조건 Leave 하면 "응답 대기 세션 Room 유지" 정책이 깨진다.
  useEffect(() => {
    if (activeSeq == null || activeSeq <= 0) return;
    const socket = getChatSocket();
    socket.subscribe(String(activeSeq)); // 내부에서 "[Socket] Room Join" 로그
  }, [activeSeq]);
}
