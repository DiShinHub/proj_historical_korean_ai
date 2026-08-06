import styles from "@/styles/Dictionary.module.css";
import {
  HK_DICTIONARY_ROOM,
  type DictionaryEventLevel,
  type DictionaryTaskEvent,
} from "@/hooks/useDictionaryRoom";

const LEVEL_LABEL: Record<DictionaryEventLevel, string> = {
  success: "완료",
  fail: "실패",
  info: "안내",
};

const LEVEL_CLASS: Record<DictionaryEventLevel, string> = {
  success: styles.feedItemSuccess,
  fail: styles.feedItemFail,
  info: styles.feedItemInfo,
};

const LEVEL_COLOR: Record<DictionaryEventLevel, string> = {
  success: "var(--ok)",
  fail: "var(--danger)",
  info: "var(--accent)",
};

interface TaskFeedProps {
  events: DictionaryTaskEvent[];
  pendingCount: number;
  onClear: () => void;
}

/**
 * 작업 결과 피드.
 *
 * 공용 room 이므로 **다른 사용자가 요청한 작업의 결과도 함께** 표시된다.
 * 현재 백엔드 브로드캐스트 페이로드에는 요청자/task_id 가 없어
 * 내 요청과 남의 요청을 구분할 수 없다(노트 §3).
 */
export default function TaskFeed({
  events,
  pendingCount,
  onClear,
}: TaskFeedProps) {
  return (
    <aside className={styles.feed}>
      <div className={styles.feedHead}>
        <span className={styles.feedTitle}>작업 결과</span>
        <span className={styles.panelSpacer} />
        <button
          type="button"
          className={`${styles.btn} ${styles.btnSmall} ${styles.btnGhost}`}
          onClick={onClear}
          disabled={events.length === 0}
        >
          지우기
        </button>
      </div>

      {pendingCount > 0 ? (
        <div className={styles.feedPending}>
          <span className={styles.spinner} aria-hidden />
          처리 대기 중 {pendingCount}건 · 소켓 응답을 기다리는 중입니다
        </div>
      ) : null}

      <div className={styles.feedList}>
        {events.length === 0 ? (
          <div className={styles.feedEmpty}>
            아직 수신한 작업 결과가 없습니다.
            <br />
            room <code>{HK_DICTIONARY_ROOM}</code> 에 조인되어 있습니다.
            <br />
            모든 사용자의 일괄 삽입 결과가 이곳에 함께 표시됩니다.
          </div>
        ) : null}

        {events.map((event) => (
          <div
            key={event.id}
            className={`${styles.feedItem} ${LEVEL_CLASS[event.level]}`}
          >
            <div className={styles.feedItemHead}>
              <span
                className={styles.feedLevel}
                style={{ color: LEVEL_COLOR[event.level] }}
              >
                {LEVEL_LABEL[event.level]}
              </span>
              <span className={styles.feedTime}>{event.at}</span>
            </div>
            <div>{event.message}</div>
            {event.itemsCnt != null ? (
              <div className={styles.feedCount}>
                적재 항목 {event.itemsCnt.toLocaleString()}건
              </div>
            ) : null}
          </div>
        ))}
      </div>
    </aside>
  );
}
