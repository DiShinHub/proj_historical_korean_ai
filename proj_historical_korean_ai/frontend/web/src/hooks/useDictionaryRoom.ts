import { useCallback, useEffect, useRef, useState } from "react";
import { getChatSocket } from "@/lib/socket";
import type { SocketStatus } from "@/lib/socket";
import { nowClock } from "@/lib/dictionary/datetime";

/**
 * 사전 화면 전용 소켓 Room.
 *
 * 채팅과 달리 **세션 단위가 아니라 전체 통합 room** 이다.
 * 모든 사용자가 같은 room 에 조인하고, 백엔드 task_worker 의 브로드캐스트도
 * 같은 room 으로 들어온다. (백엔드 /dump 예시의 room_name 과 동일해야 한다)
 */
export const HK_DICTIONARY_ROOM = "hk_dictionary_service";

export type DictionaryEventLevel = "success" | "fail" | "info";

export interface DictionaryTaskEvent {
  id: string;
  /** "HH:mm:ss" */
  at: string;
  level: DictionaryEventLevel;
  message: string;
  /** 적재된 사전 항목 수(백엔드 items_cnt). 없으면 null. */
  itemsCnt: number | null;
}

const MAX_EVENTS = 50;

let eventSeq = 0;
function nextEventId(): string {
  eventSeq += 1;
  return `evt-${eventSeq}`;
}

export interface UseDictionaryRoomResult {
  socketStatus: SocketStatus;
  events: DictionaryTaskEvent[];
  /** 요청 후 아직 소켓 응답이 오지 않은 작업 수. */
  pendingCount: number;
  /** /dump 요청 직후 호출 → 대기 카운트 증가 + 로컬 로그 남김. */
  markTaskRequested: (message: string) => void;
  /** 로컬 안내/오류 로그 추가(소켓과 무관한 UI 이벤트). */
  pushLocalEvent: (level: DictionaryEventLevel, message: string) => void;
  clearEvents: () => void;
}

/**
 * 공용 room 조인 + 작업 결과 수신.
 *
 * @param onTaskDone 작업 성공 수신 시 호출(목록 새로고침 등).
 */
export function useDictionaryRoom(
  onTaskDone?: (event: DictionaryTaskEvent) => void
): UseDictionaryRoomResult {
  const [socketStatus, setSocketStatus] = useState<SocketStatus>("idle");
  const [events, setEvents] = useState<DictionaryTaskEvent[]>([]);
  const [pendingCount, setPendingCount] = useState(0);

  // onMessage 핸들러는 마운트 시 1회만 등록하므로, 최신 콜백을 ref 로 참조한다.
  const onTaskDoneRef = useRef(onTaskDone);
  onTaskDoneRef.current = onTaskDone;

  const appendEvent = useCallback((event: DictionaryTaskEvent) => {
    setEvents((prev) => [event, ...prev].slice(0, MAX_EVENTS));
  }, []);

  const pushLocalEvent = useCallback(
    (level: DictionaryEventLevel, message: string) => {
      appendEvent({
        id: nextEventId(),
        at: nowClock(),
        level,
        message,
        itemsCnt: null,
      });
    },
    [appendEvent]
  );

  const markTaskRequested = useCallback(
    (message: string) => {
      setPendingCount((n) => n + 1);
      pushLocalEvent("info", message);
    },
    [pushLocalEvent]
  );

  const clearEvents = useCallback(() => setEvents([]), []);

  useEffect(() => {
    const socket = getChatSocket();

    const offStatus = socket.onStatus((status) => setSocketStatus(status));

    const offMessage = socket.onMessage((room, payload, envelope) => {
      // 공용 room 이외의 프레임(= 채팅 세션 응답)은 이 화면과 무관하다.
      if (room !== HK_DICTIONARY_ROOM) return;

      // 서버가 오류 코드를 실어 보낸 경우.
      if (envelope.response_code != null && envelope.response_code !== 200) {
        appendEvent({
          id: nextEventId(),
          at: nowClock(),
          level: "fail",
          message: envelope.message || "소켓 오류가 발생했습니다.",
          itemsCnt: null,
        });
        setPendingCount((n) => Math.max(0, n - 1));
        return;
      }

      // task_worker 가 보내는 페이로드: { result, llm_msg, items_cnt }
      // (LlmResponsePayload 에는 items_cnt 가 없어 unknown 경유로 읽는다)
      const raw = payload as unknown as Record<string, unknown>;
      const rawItemsCnt = raw.items_cnt;
      const itemsCnt =
        typeof rawItemsCnt === "number" && Number.isFinite(rawItemsCnt)
          ? rawItemsCnt
          : null;

      const result = payload.result ?? "";
      const level: DictionaryEventLevel =
        result === "success" ? "success" : result === "fail" ? "fail" : "info";

      const message =
        payload.llm_msg ??
        payload.text ??
        (level === "success" ? "처리 성공" : "처리 결과를 수신했습니다.");

      const event: DictionaryTaskEvent = {
        id: nextEventId(),
        at: nowClock(),
        level,
        message,
        itemsCnt,
      };

      appendEvent(event);
      setPendingCount((n) => Math.max(0, n - 1));

      if (level === "success") {
        onTaskDoneRef.current?.(event);
      }
    });

    // _app.tsx 에서 이미 connect 하지만, 채팅 화면을 벗어나며 disconnect 된
    // 상태로 진입할 수 있으므로 여기서도 보장한다(멱등).
    socket.connect();
    socket.subscribe(HK_DICTIONARY_ROOM);

    return () => {
      offStatus();
      offMessage();
      // 소켓 자체는 앱 전역 자원이므로 끊지 않고 room 만 떠난다.
      socket.unsubscribe(HK_DICTIONARY_ROOM);
    };
  }, [appendEvent]);

  return {
    socketStatus,
    events,
    pendingCount,
    markTaskRequested,
    pushLocalEvent,
    clearEvents,
  };
}
