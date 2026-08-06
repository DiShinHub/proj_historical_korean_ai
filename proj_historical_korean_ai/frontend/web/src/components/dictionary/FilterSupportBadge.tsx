import styles from "@/styles/Dictionary.module.css";
import type { FilterSupport } from "@/lib/dictionary/fields";

const LABEL: Record<FilterSupport, string> = {
  server: "서버 검색",
  client: "페이지 내",
  unavailable: "필터 불가",
};

const CLASS: Record<FilterSupport, string> = {
  server: styles.badgeServer,
  client: styles.badgeClient,
  unavailable: styles.badgeOff,
};

const TITLE: Record<FilterSupport, string> = {
  server: "백엔드가 지원하는 검색 조건입니다. 전체 데이터 기준으로 조회합니다.",
  client:
    "백엔드가 아직 지원하지 않는 조건입니다. 현재 페이지에 불러온 데이터에만 적용됩니다.",
  unavailable:
    "백엔드 검색 미지원 + 목록 응답에도 값이 없어 필터할 수 없습니다. 정렬만 가능합니다.",
};

/** 각 필터가 서버/클라이언트/불가 중 어디에 해당하는지 시각적으로 알린다. */
export default function FilterSupportBadge({
  support,
}: {
  support: FilterSupport;
}) {
  return (
    <span className={CLASS[support]} title={TITLE[support]}>
      {LABEL[support]}
    </span>
  );
}
