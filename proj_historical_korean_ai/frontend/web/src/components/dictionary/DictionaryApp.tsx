import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import styles from "@/styles/Dictionary.module.css";
import { useTheme } from "@/themes/ThemeContext";
import { useAppDispatch } from "@/redux/hooks";
import { initAuth } from "@/redux/slices/authSlice";
import { useAuthBootstrap } from "@/hooks/useAuthBootstrap";
import { useDictionaryList } from "@/hooks/useDictionaryList";
import {
  HK_DICTIONARY_ROOM,
  useDictionaryRoom,
  type DictionaryEventLevel,
} from "@/hooks/useDictionaryRoom";
import {
  confirmDictionaries,
  deleteDictionary,
  type HkDictionaryDto,
} from "@/lib/api/dictionary";
import type { ApiError } from "@/lib/api/types";
import type { SocketStatus } from "@/lib/socket";

import DictionaryFilters from "./DictionaryFilters";
import DictionaryTable from "./DictionaryTable";
import Pagination from "./Pagination";
import DictionaryFormDialog from "./DictionaryFormDialog";
import DictionaryDetailDialog from "./DictionaryDetailDialog";
import BulkTextDialog from "./BulkTextDialog";
import BulkFileDialog from "./BulkFileDialog";
import TaskFeed from "./TaskFeed";

const SOCKET_LABEL: Record<SocketStatus, string> = {
  idle: "대기",
  connecting: "연결 중",
  open: "연결됨",
  reconnecting: "재연결 중",
  closed: "끊김",
  error: "오류",
};

type DialogState =
  | { type: "none" }
  | { type: "form"; target: HkDictionaryDto | null }
  | { type: "detail"; seq: number }
  | { type: "bulkText" }
  | { type: "bulkFile" };

interface Flash {
  level: DictionaryEventLevel;
  message: string;
}

/**
 * 고어 사전(hk_dictionary) 관리 화면.
 *
 * 인증이 끝난 뒤에만 실제 콘솔을 마운트해서, 토큰 없이 목록 조회가
 * 먼저 나가고 401 → 재로그인으로 도는 경로를 피한다.
 */
export default function DictionaryApp() {
  const dispatch = useAppDispatch();
  const { status, error } = useAuthBootstrap();

  if (status === "error") {
    return (
      <div className={styles.fullscreen}>
        <div className={styles.fullscreenIcon} aria-hidden>
          ⚠️
        </div>
        <h2 className={styles.fullscreenTitle}>백엔드에 연결할 수 없습니다</h2>
        <p>{error}</p>
        <button
          type="button"
          className={`${styles.btn} ${styles.btnPrimary}`}
          onClick={() => dispatch(initAuth())}
        >
          다시 시도
        </button>
      </div>
    );
  }

  if (status !== "authenticated") {
    return (
      <div className={styles.fullscreen}>
        <span className={styles.spinner} aria-hidden />
        <p>인증 중…</p>
      </div>
    );
  }

  return <DictionaryConsole />;
}

function DictionaryConsole() {
  const { toggleTheme } = useTheme();
  const list = useDictionaryList();

  const [dialog, setDialog] = useState<DialogState>({ type: "none" });
  const [flash, setFlash] = useState<Flash | null>(null);
  const [deletingSeq, setDeletingSeq] = useState<number | null>(null);
  const [bulkConfirming, setBulkConfirming] = useState(false);

  // 소켓 room 은 세션별이 아닌 전체 통합. 작업 완료 시 목록을 새로고침한다.
  const refresh = list.refresh;
  const handleTaskDone = useCallback(() => {
    refresh();
  }, [refresh]);

  const room = useDictionaryRoom(handleTaskDone);
  const { pushLocalEvent } = room;

  // flash 메시지는 잠깐만 노출한다.
  useEffect(() => {
    if (!flash) return;
    const timer = setTimeout(() => setFlash(null), 5000);
    return () => clearTimeout(timer);
  }, [flash]);

  const notify = useCallback(
    (level: DictionaryEventLevel, message: string) => {
      setFlash({ level, message });
      pushLocalEvent(level, message);
    },
    [pushLocalEvent]
  );

  const handleSaved = useCallback(
    (message: string) => {
      notify("success", message);
      refresh();
    },
    [notify, refresh]
  );

  const handleDelete = useCallback(
    async (item: HkDictionaryDto) => {
      const confirmed = window.confirm(
        `#${item.seq} "${item.modern_korean} / ${item.historical_korean}" 항목을 삭제할까요?\n` +
          "(Soft Delete: delete_yn 이 'Y' 로 변경되며 목록에서 제외됩니다)"
      );
      if (!confirmed) return;

      setDeletingSeq(item.seq);
      try {
        await deleteDictionary(item.seq);
        notify("success", `사전 항목 #${item.seq} 을(를) 삭제했습니다.`);
        refresh();
      } catch (err) {
        const apiError = err as ApiError;
        notify("fail", apiError?.message ?? "삭제에 실패했습니다.");
      } finally {
        setDeletingSeq(null);
      }
    },
    [notify, refresh]
  );

  const handleBulkConfirm = useCallback(async () => {
    const seqs = Array.from(list.selectedSeqs);
    if (seqs.length === 0) return;

    const confirmed = window.confirm(
      `선택한 ${seqs.length}개의 항목을 검수 처리하시겠습니까?`
    );
    if (!confirmed) return;

    console.log("[dictionary] bulk confirm request →", { seqs });
    setBulkConfirming(true);
    try {
      await confirmDictionaries({ seqs, confirmed_yn: "Y" });
      console.log("[dictionary] bulk confirm ← ok", { seqs });
      notify("success", `${seqs.length}개 항목을 검수 완료로 처리했습니다.`);
      refresh();
    } catch (err) {
      const apiError = err as ApiError;
      console.log("[dictionary] bulk confirm ← error", apiError);
      notify("fail", apiError?.message ?? "일괄 검수에 실패했습니다.");
    } finally {
      setBulkConfirming(false);
    }
  }, [list.selectedSeqs, notify, refresh]);

  const closeDialog = useCallback(() => setDialog({ type: "none" }), []);

  const hiddenByClientFilter = list.pageItemCount - list.items.length;

  return (
    <div className={styles.page}>
      {/* ── 상단 바 ─────────────────────────────────────────────── */}
      <header className={styles.topbar}>
        <div className={styles.brand}>
          <span className={styles.brandTitle}>고어 사전 관리</span>
          <span className={styles.brandSub}>hk_dictionary</span>
        </div>

        <span className={styles.topbarSpacer} />

        <div className={styles.topbarActions}>
          <span
            className={styles.roomBadge}
            title={`소켓 room: ${HK_DICTIONARY_ROOM} (전체 통합)`}
          >
            <span
              className={styles.roomDot}
              data-status={room.socketStatus}
              aria-hidden
            />
            {SOCKET_LABEL[room.socketStatus]} · {HK_DICTIONARY_ROOM}
          </span>

          <button
            type="button"
            className={styles.iconBtn}
            onClick={toggleTheme}
            aria-label="테마 전환"
            title="테마 전환"
          >
            🌙
          </button>

          <Link href="/chat" className={styles.btn}>
            채팅으로
          </Link>
        </div>
      </header>

      <div className={styles.body}>
        <main className={styles.main}>
          <div className={styles.scroll}>
            {flash ? (
              <div
                className={`${styles.notice} ${
                  flash.level === "fail"
                    ? styles.noticeError
                    : flash.level === "success"
                    ? styles.noticeInfo
                    : styles.noticeWarn
                }`}
              >
                <span aria-hidden>
                  {flash.level === "fail"
                    ? "⚠️"
                    : flash.level === "success"
                    ? "✅"
                    : "ℹ️"}
                </span>
                <span>{flash.message}</span>
              </div>
            ) : null}

            {list.error ? (
              <div className={`${styles.notice} ${styles.noticeError}`}>
                <span aria-hidden>⚠️</span>
                <span>{list.error}</span>
              </div>
            ) : null}

            {/* ── 액션 버튼 ─────────────────────────────────── */}
            <div className={styles.actionRow}>
              <button
                type="button"
                className={`${styles.btn} ${styles.btnPrimary}`}
                onClick={() => setDialog({ type: "form", target: null })}
              >
                ＋ 사전 항목 등록
              </button>
              <button
                type="button"
                className={styles.btn}
                onClick={() => setDialog({ type: "bulkText" })}
              >
                📝 일괄 삽입 · 원문
              </button>
              <button
                type="button"
                className={styles.btn}
                onClick={() => setDialog({ type: "bulkFile" })}
              >
                📄 일괄 삽입 · 파일
              </button>

              <span className={styles.panelSpacer} />

              <button
                type="button"
                className={styles.btn}
                onClick={refresh}
                disabled={list.loading}
              >
                {list.loading ? "새로고침 중…" : "↻ 새로고침"}
              </button>
            </div>

            {/* ── 조회 조건 ─────────────────────────────────── */}
            <DictionaryFilters
              filters={list.filters}
              sort={list.sort}
              loading={list.loading}
              onApply={list.applyFilters}
              onReset={list.resetFilters}
              onSortChange={list.setSort}
            />

            {list.clientFilterActive ? (
              <div className={`${styles.notice} ${styles.noticeWarn}`}>
                <span aria-hidden>⚠️</span>
                <span>
                  서버가 지원하지 않는 검색 조건이 포함되어 있어{" "}
                  <strong>현재 페이지({list.pageItemCount}건)에만</strong> 적용
                  했습니다
                  {hiddenByClientFilter > 0
                    ? ` — ${hiddenByClientFilter}건 숨김`
                    : ""}
                  . 전체 데이터 기준 검색을 하려면 백엔드 확장이 필요합니다
                  (BACKEND_MODIFICATION_NOTES.md §1).
                </span>
              </div>
            ) : null}

            {/* ── 일괄 검수 ─────────────────────────────────── */}
            {list.selectedSeqs.size > 0 ? (
              <div className={styles.actionRow}>
                <span className={styles.fieldHint}>
                  {list.selectedSeqs.size}개 선택됨
                </span>
                <button
                  type="button"
                  className={`${styles.btn} ${styles.btnPrimary}`}
                  disabled={bulkConfirming}
                  onClick={handleBulkConfirm}
                >
                  {bulkConfirming ? "검수 처리 중…" : "✔ 일괄 검수"}
                </button>
                <button
                  type="button"
                  className={styles.btn}
                  disabled={bulkConfirming}
                  onClick={list.clearSelection}
                >
                  선택 해제
                </button>
              </div>
            ) : null}

            {/* ── 목록 ──────────────────────────────────────── */}
            <DictionaryTable
              items={list.items}
              sort={list.sort}
              loading={list.loading || deletingSeq != null || bulkConfirming}
              selectedSeqs={list.selectedSeqs}
              onToggleSort={list.toggleSort}
              onToggleSelect={list.toggleSelect}
              onToggleSelectAll={list.toggleSelectAll}
              onView={(item) => setDialog({ type: "detail", seq: item.seq })}
              onEdit={(item) => setDialog({ type: "form", target: item })}
              onDelete={handleDelete}
            />

            <Pagination
              page={list.page}
              pageSize={list.pageSize}
              totalCnt={list.totalCnt}
              totalPages={list.totalPages}
              loading={list.loading}
              onPageChange={list.setPage}
              onPageSizeChange={list.setPageSize}
            />
          </div>
        </main>

        <TaskFeed
          events={room.events}
          pendingCount={room.pendingCount}
          onClear={room.clearEvents}
        />
      </div>

      {/* ── 모달 ─────────────────────────────────────────────── */}
      {dialog.type === "form" ? (
        <DictionaryFormDialog
          target={dialog.target}
          onClose={closeDialog}
          onSaved={handleSaved}
        />
      ) : null}

      {dialog.type === "detail" ? (
        <DictionaryDetailDialog
          seq={dialog.seq}
          onClose={closeDialog}
          onEdit={(item) => setDialog({ type: "form", target: item })}
        />
      ) : null}

      {dialog.type === "bulkText" ? (
        <BulkTextDialog
          onClose={closeDialog}
          onRequested={(message) => {
            setFlash({ level: "info", message });
            room.markTaskRequested(message);
          }}
        />
      ) : null}

      {dialog.type === "bulkFile" ? (
        <BulkFileDialog
          onClose={closeDialog}
          onNotice={(message) => notify("fail", message)}
        />
      ) : null}
    </div>
  );
}
