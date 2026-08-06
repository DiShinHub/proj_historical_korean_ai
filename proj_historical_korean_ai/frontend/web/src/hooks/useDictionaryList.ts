import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  listDictionary,
  type HkDictionaryDto,
} from "@/lib/api/dictionary";
import type { ApiError } from "@/lib/api/types";
import type { DictionaryFieldKey } from "@/lib/dictionary/fields";
import {
  isDateInRange,
  toDateInputValue,
  toPeriodEndIso,
  toPeriodStartIso,
} from "@/lib/dictionary/datetime";

/**
 * 목록 조회 상태 관리 훅.
 *
 * 서버가 지원하는 필터(현대어 / 시대 기간)는 쿼리 파라미터로 보내고,
 * 서버 미지원 필터(seq / 고어 / 등록일시)는 받아온 **현재 페이지**에 한해
 * 클라이언트에서 거른다. 어떤 필터가 어느 쪽인지는 fields.ts 의 메타데이터가 기준이다.
 */

export interface DictionaryFilterState {
  /** client 필터 */
  seq: string;
  /** server 필터 (LIKE) */
  modern_korean: string;
  /** client 필터 */
  historical_korean: string;
  /** server 필터 — 기간 바(YYYY-MM-DD) */
  periodStart: string;
  periodEnd: string;
  /** client 필터 — 등록일시 범위(YYYY-MM-DD) */
  regDtFrom: string;
  regDtTo: string;
}

export const EMPTY_FILTERS: DictionaryFilterState = {
  seq: "",
  modern_korean: "",
  historical_korean: "",
  periodStart: "",
  periodEnd: "",
  regDtFrom: "",
  regDtTo: "",
};

export interface DictionarySortState {
  orderBy: DictionaryFieldKey;
  orderDirection: "asc" | "desc";
}

export const DEFAULT_SORT: DictionarySortState = {
  orderBy: "seq",
  orderDirection: "desc",
};

/** 백엔드 page_size 제약: 1 ≤ page_size ≤ 100 */
export const PAGE_SIZE_OPTIONS = [15, 20, 30, 50, 100];

export interface UseDictionaryListResult {
  /** 클라이언트 필터까지 적용된 표시용 목록 */
  items: HkDictionaryDto[];
  /** 서버가 내려준 현재 페이지 원본 건수(클라이언트 필터 적용 전) */
  pageItemCount: number;
  /** 전체 건수(서버 필터 기준) */
  totalCnt: number;
  page: number;
  pageSize: number;
  totalPages: number;
  loading: boolean;
  error: string | null;

  filters: DictionaryFilterState;
  sort: DictionarySortState;
  /** 현재 클라이언트 필터가 하나라도 걸려 있는가 */
  clientFilterActive: boolean;

  applyFilters: (next: DictionaryFilterState) => void;
  resetFilters: () => void;
  setSort: (next: DictionarySortState) => void;
  toggleSort: (key: DictionaryFieldKey) => void;
  setPage: (page: number) => void;
  setPageSize: (size: number) => void;
  refresh: () => void;
}

function hasClientFilter(f: DictionaryFilterState): boolean {
  return Boolean(
    f.seq.trim() ||
      f.historical_korean.trim() ||
      f.regDtFrom ||
      f.regDtTo
  );
}

export function useDictionaryList(): UseDictionaryListResult {
  const [filters, setFilters] = useState<DictionaryFilterState>(EMPTY_FILTERS);
  const [sort, setSortState] = useState<DictionarySortState>(DEFAULT_SORT);
  const [page, setPageState] = useState(1);
  const [pageSize, setPageSizeState] = useState(20);
  const [reloadToken, setReloadToken] = useState(0);

  const [rows, setRows] = useState<HkDictionaryDto[]>([]);
  const [totalCnt, setTotalCnt] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 늦게 도착한 이전 요청이 최신 결과를 덮어쓰지 않도록 막는다.
  const requestSeq = useRef(0);

  useEffect(() => {
    const currentRequest = ++requestSeq.current;
    let cancelled = false;

    setLoading(true);
    setError(null);

    listDictionary({
      modern_korean: filters.modern_korean.trim() || undefined,
      historical_period_start_dt: toPeriodStartIso(filters.periodStart),
      historical_period_end_dt: toPeriodEndIso(filters.periodEnd),
      order_by: sort.orderBy,
      order_direction: sort.orderDirection,
      page,
      page_size: pageSize,
    })
      .then((result) => {
        if (cancelled || currentRequest !== requestSeq.current) return;
        setRows(result.data_list);
        setTotalCnt(result.total_cnt);
      })
      .catch((err: ApiError) => {
        if (cancelled || currentRequest !== requestSeq.current) return;
        setRows([]);
        setTotalCnt(0);
        setError(err?.message ?? "목록을 불러오지 못했습니다.");
      })
      .finally(() => {
        if (cancelled || currentRequest !== requestSeq.current) return;
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [
    filters.modern_korean,
    filters.periodStart,
    filters.periodEnd,
    sort.orderBy,
    sort.orderDirection,
    page,
    pageSize,
    reloadToken,
  ]);

  // ── 서버 미지원 필터: 현재 페이지 한정 클라이언트 필터 ────────────────────
  const items = useMemo(() => {
    const seqTerm = filters.seq.trim();
    const historicalTerm = filters.historical_korean.trim();

    return rows.filter((row) => {
      if (seqTerm && !String(row.seq).includes(seqTerm)) return false;

      if (
        historicalTerm &&
        !(row.historical_korean ?? "").includes(historicalTerm)
      ) {
        return false;
      }

      if (filters.regDtFrom || filters.regDtTo) {
        const regDate = toDateInputValue(row.reg_dt);
        if (!isDateInRange(regDate, filters.regDtFrom, filters.regDtTo)) {
          return false;
        }
      }

      return true;
    });
  }, [
    rows,
    filters.seq,
    filters.historical_korean,
    filters.regDtFrom,
    filters.regDtTo,
  ]);

  const applyFilters = useCallback((next: DictionaryFilterState) => {
    setFilters(next);
    setPageState(1);
  }, []);

  const resetFilters = useCallback(() => {
    setFilters(EMPTY_FILTERS);
    setSortState(DEFAULT_SORT);
    setPageState(1);
  }, []);

  const setSort = useCallback((next: DictionarySortState) => {
    setSortState(next);
    setPageState(1);
  }, []);

  const toggleSort = useCallback((key: DictionaryFieldKey) => {
    setSortState((prev) =>
      prev.orderBy === key
        ? {
            orderBy: key,
            orderDirection: prev.orderDirection === "asc" ? "desc" : "asc",
          }
        : { orderBy: key, orderDirection: "asc" }
    );
    setPageState(1);
  }, []);

  const totalPages = Math.max(1, Math.ceil(totalCnt / pageSize));

  const setPage = useCallback(
    (next: number) => {
      setPageState(Math.min(Math.max(1, next), Math.max(1, totalPages)));
    },
    [totalPages]
  );

  const setPageSize = useCallback((size: number) => {
    setPageSizeState(size);
    setPageState(1);
  }, []);

  const refresh = useCallback(() => setReloadToken((n) => n + 1), []);

  return {
    items,
    pageItemCount: rows.length,
    totalCnt,
    page,
    pageSize,
    totalPages,
    loading,
    error,
    filters,
    sort,
    clientFilterActive: hasClientFilter(filters),
    applyFilters,
    resetFilters,
    setSort,
    toggleSort,
    setPage,
    setPageSize,
    refresh,
  };
}
