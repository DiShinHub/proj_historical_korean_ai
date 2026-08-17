import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  listDictionary,
  type HkDictionaryDto,
} from "@/lib/api/dictionary";
import type { ApiError } from "@/lib/api/types";
import type {
  DictionaryFieldKey,
  SearchConditionKey,
} from "@/lib/dictionary/fields";
import { toPeriodEndIso, toPeriodStartIso } from "@/lib/dictionary/datetime";

/**
 * 목록 조회 상태 관리 훅.
 *
 * 검색 조건은 4개 중 여러 개를 동시에 선택해서 AND 로 결합할 수 있다
 * (현대어 / 고어 / 시대 기간 / 검수 여부).
 * 서버가 지원하는 조건(현대어 / 시대 기간)은 쿼리 파라미터로 보내고,
 * 서버 미지원 조건(고어 / 검수 여부)은 받아온 **현재 페이지**에 한해
 * 클라이언트에서 거른다(선택된 조건들끼리는 AND). 어떤 조건이 어느 쪽인지는
 * fields.ts 의 SEARCH_CONDITIONS 가 기준이다.
 */

export interface DictionaryFilterState {
  /** 4개 검색 조건 중 현재 활성화된 것들(다중 선택, AND 결합) */
  conditions: SearchConditionKey[];
  /** server 필터 (LIKE) */
  modern_korean: string;
  /** client 필터(현재 페이지 한정) */
  historical_korean: string;
  /** server 필터 — 기간 바(YYYY-MM-DD) */
  periodStart: string;
  periodEnd: string;
  /** client 필터(현재 페이지 한정). "" | "Y" | "N" */
  confirmed_yn: string;
}

export const EMPTY_FILTERS: DictionaryFilterState = {
  conditions: ["modern_korean", "historical_korean", "period", "confirmed_yn"],
  modern_korean: "",
  historical_korean: "",
  periodStart: "",
  periodEnd: "",
  confirmed_yn: "",
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
  /** 현재 클라이언트 필터가 걸려 있는가(고어 / 검수 여부 조건 선택 + 값 있음) */
  clientFilterActive: boolean;

  applyFilters: (next: DictionaryFilterState) => void;
  resetFilters: () => void;
  setSort: (next: DictionarySortState) => void;
  toggleSort: (key: DictionaryFieldKey) => void;
  setPage: (page: number) => void;
  setPageSize: (size: number) => void;
  refresh: () => void;

  /** 일괄 검수용 행 선택 */
  selectedSeqs: Set<number>;
  toggleSelect: (seq: number) => void;
  toggleSelectAll: () => void;
  clearSelection: () => void;
}

function hasClientFilter(f: DictionaryFilterState): boolean {
  if (f.conditions.includes("historical_korean") && f.historical_korean.trim()) {
    return true;
  }
  if (f.conditions.includes("confirmed_yn") && f.confirmed_yn) {
    return true;
  }
  return false;
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

  const [selectedSeqs, setSelectedSeqs] = useState<Set<number>>(new Set());

  // 늦게 도착한 이전 요청이 최신 결과를 덮어쓰지 않도록 막는다.
  const requestSeq = useRef(0);

  useEffect(() => {
    const currentRequest = ++requestSeq.current;
    let cancelled = false;

    setLoading(true);
    setError(null);

    const query = {
      // 선택된 조건에 해당하는 값만 서버로 전달한다(다중 조건은 AND 로 결합).
      modern_korean: filters.conditions.includes("modern_korean")
        ? filters.modern_korean.trim() || undefined
        : undefined,
      historical_korean: filters.conditions.includes("historical_korean")
        ? filters.historical_korean.trim() || undefined
        : undefined,
      historical_period_start_dt: filters.conditions.includes("period")
        ? toPeriodStartIso(filters.periodStart)
        : undefined,
      historical_period_end_dt: filters.conditions.includes("period")
        ? toPeriodEndIso(filters.periodEnd)
        : undefined,
      confirmed_yn: filters.conditions.includes("confirmed_yn")
        ? filters.confirmed_yn.trim() || undefined
        : undefined,
      order_by: sort.orderBy,
      order_direction: sort.orderDirection,
      page,
      page_size: pageSize,
    };

    console.log("[dictionary] list fetch →", query);

    listDictionary(query)
      .then((result) => {
        if (cancelled || currentRequest !== requestSeq.current) return;
        console.log("[dictionary] list fetch ← ok", {
          total_cnt: result.total_cnt,
          rows: result.data_list.length,
        });
        setRows(result.data_list);
        setTotalCnt(result.total_cnt);
      })
      .catch((err: ApiError) => {
        if (cancelled || currentRequest !== requestSeq.current) return;
        console.log("[dictionary] list fetch ← error", err);
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
    filters.conditions,
    filters.modern_korean,
    filters.historical_korean,
    filters.periodStart,
    filters.periodEnd,
    filters.confirmed_yn,
    sort.orderBy,
    sort.orderDirection,
    page,
    pageSize,
    reloadToken,
  ]);

  // 새로 응답을 받은 페이지에 대해서는 이전 선택을 유지하지 않는다
  // (화면에 없는 seq 가 선택된 채로 남아 일괄 검수에 잘못 반영되는 것을 막는다).
  useEffect(() => {
    setSelectedSeqs(new Set());
  }, [rows]);

  // ── 서버 미지원 조건(고어 / 검수 여부): 현재 페이지 한정 클라이언트 필터 ──────────
  // 여러 조건이 함께 선택된 경우 AND 로 결합한다.
  const items = useMemo(() => {
    const historicalTerm = filters.conditions.includes("historical_korean")
      ? filters.historical_korean.trim()
      : "";
    const confirmedFilter = filters.conditions.includes("confirmed_yn")
      ? filters.confirmed_yn
      : "";

    if (!historicalTerm && !confirmedFilter) return rows;

    return rows.filter((row) => {
      if (historicalTerm && !(row.historical_korean ?? "").includes(historicalTerm)) {
        return false;
      }
      if (confirmedFilter && row.confirmed_yn !== confirmedFilter) {
        return false;
      }
      return true;
    });
  }, [rows, filters.conditions, filters.historical_korean, filters.confirmed_yn]);

  const applyFilters = useCallback((next: DictionaryFilterState) => {
    console.log("[dictionary] applyFilters", next);
    setFilters(next);
    setPageState(1);
  }, []);

  const resetFilters = useCallback(() => {
    console.log("[dictionary] resetFilters");
    setFilters(EMPTY_FILTERS);
    setSortState(DEFAULT_SORT);
    setPageState(1);
  }, []);

  const setSort = useCallback((next: DictionarySortState) => {
    console.log("[dictionary] setSort", next);
    setSortState(next);
    setPageState(1);
  }, []);

  const toggleSort = useCallback((key: DictionaryFieldKey) => {
    setSortState((prev) => {
      const next: DictionarySortState =
        prev.orderBy === key
          ? {
              orderBy: key,
              orderDirection: prev.orderDirection === "asc" ? "desc" : "asc",
            }
          : { orderBy: key, orderDirection: "asc" };
      console.log("[dictionary] toggleSort", next);
      return next;
    });
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

  const toggleSelect = useCallback((seq: number) => {
    setSelectedSeqs((prev) => {
      const next = new Set(prev);
      if (next.has(seq)) {
        next.delete(seq);
      } else {
        next.add(seq);
      }
      console.log("[dictionary] toggleSelect", {
        seq,
        selected: Array.from(next),
      });
      return next;
    });
  }, []);

  const toggleSelectAll = useCallback(() => {
    setSelectedSeqs((prev) => {
      const allSelected =
        items.length > 0 && items.every((item) => prev.has(item.seq));
      const next = allSelected
        ? new Set<number>()
        : new Set(items.map((item) => item.seq));
      console.log("[dictionary] toggleSelectAll", {
        selected: Array.from(next),
      });
      return next;
    });
  }, [items]);

  const clearSelection = useCallback(() => {
    console.log("[dictionary] clearSelection");
    setSelectedSeqs(new Set());
  }, []);

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
    selectedSeqs,
    toggleSelect,
    toggleSelectAll,
    clearSelection,
  };
}
