# 백엔드 수정 요청 노트 — 고어 사전(hk_dictionary)

> 작성 시점: 사전 관리 프론트엔드(`/dictionary`) 개발 완료 시점
> 작성 사유: 요구사항을 프론트엔드만으로 충족할 수 없는 구간이 있어, **백엔드 코드를 직접 수정하지 않고** 사양만 정리합니다.
> 대상 파일
> - `backend/llm/app/handler/api/v1/au/hk_dictionary/hk_dictionary_handler.py`
> - `backend/llm/app/handler/api/v1/au/hk_dictionary/hk_dictionary_service.py`
> - `backend/llm/app/dao/hk_dictionary_dao.py`
> - `backend/llm/task_worker/handlers/hk_dictionary/hk_dictionary_service.py`
> - `backend/llm/task_worker/dao/hk_dictionary_service_dao.py`

## 요약

| # | 항목 | 우선순위 | 요구사항 충족 여부 |
|---|------|----------|--------------------|
| 1 | 목록 조회 필터 컬럼 확장 | **필수** | 요구사항 4-C 미충족 (현재 2종만 지원) |
| 2 | 목록/단건 응답 필드 누락 | **필수** | 정렬은 되지만 결과 확인 불가 |
| 3 | `/dump` 작업 추적 식별자 부재 | 높음 | 공용 room에서 내 작업 구분 불가 |
| 4 | 파일(Excel/PDF) 업로드 API 부재 | 높음 | 요구사항 4-B(2) — 프론트만 구현됨 |
| 5 | 날짜 포맷/타임존 처리 불일치 | 높음 | 데이터 정합성 위험 |
| 6 | `order_by` 화이트리스트 부재 | 중간 | 500 유발 가능 |
| 7 | 기간 검색 조건이 "포함"만 지원 | 중간 | 검색 UX 제약 |
| 8 | `confirmed_yn` 등록 시 하드코딩 | 낮음 | API 간 일관성 |

---

## 1. 목록 조회 필터 컬럼 확장 (필수)

### 현상

요구사항 4-C 는 *"`delete_yn`을 제외한 모든 Entity Key 필드에 대해 조회 필터링 및 정렬 지원"* 인데,
현재 `GET /api/v1/au/hk_dictionary` 가 받는 검색 파라미터는 3개뿐입니다.

```python
# hk_dictionary_handler.py
modern_korean, historical_period_start_dt, historical_period_end_dt
```

`hk_dictionary_dao.get_hk_dictionary_list()` / `get_hk_dictionary_count()` 의 `conditions` 도 동일합니다.

정렬(`order_by`)은 `getattr(HKDictionaryEntity, order_by, ...)` 로 동적 처리되어 **전 컬럼 지원**되므로,
부족한 것은 **필터뿐**입니다.

### 프론트엔드 현재 대응

필터 UI 는 전 필드를 노출하되 지원 수준을 배지로 구분했습니다
(`src/lib/dictionary/fields.ts`, `src/components/dictionary/FilterSupportBadge.tsx`).

| 필드 | 현재 처리 | 배지 |
|------|-----------|------|
| `modern_korean` | 서버 쿼리 파라미터 | `서버 검색` |
| `historical_period_start_dt` / `_end_dt` | 서버 쿼리 파라미터 | `서버 검색` |
| `seq`, `historical_korean`, `reg_dt` | **현재 페이지 응답에 대해서만** 클라이언트 필터 | `페이지 내` |
| `reg_member_seq`, `mod_dt`, `mod_member_seq`, `confirmed_yn` | 입력 불가(disabled) — 응답 필드조차 없음 | `필터 불가` |

`페이지 내` 필터가 걸리면 화면 상단에 "현재 페이지에만 적용됨 / N건 숨김" 경고를 띄웁니다.
**전체 데이터 기준 검색이 아니므로, 운영 투입 전에 백엔드 확장이 필요합니다.**

### 요청 사양

`GET /api/v1/au/hk_dictionary` 에 아래 쿼리 파라미터를 추가해 주세요.

| 파라미터 | 타입 | 조건 | 비고 |
|----------|------|------|------|
| `seq` | int \| None | `= seq` | 정확 일치 |
| `historical_korean` | str \| None | `LIKE %값%` | `modern_korean` 과 동일 방식 |
| `reg_dt_from` / `reg_dt_to` | str(ISO) \| None | `reg_dt BETWEEN` | 등록일시 범위 |
| `mod_dt_from` / `mod_dt_to` | str(ISO) \| None | `mod_dt BETWEEN` | 수정일시 범위 |
| `reg_member_seq` | int \| None | `= reg_member_seq` | |
| `mod_member_seq` | int \| None | `= mod_member_seq` | |
| `confirmed_yn` | str \| None | `= confirmed_yn` | `'Y'` / `'N'` |

- `get_hk_dictionary_list()` 와 `get_hk_dictionary_count()` **양쪽 모두**에 동일 조건을 반영해야 합니다
  (한쪽만 반영하면 `total_cnt` 와 실제 목록이 어긋나 페이지네이션이 깨집니다).
- 두 함수의 조건 구성 코드가 완전히 중복되므로, 조건 빌더 함수 하나로 추출하는 것을 권장합니다.

### 프론트엔드 반영 방법

`src/lib/dictionary/fields.ts` 의 각 필드 `filter` 값을 `"server"` 로 바꾸고,
`src/hooks/useDictionaryList.ts` 의 `listDictionary({...})` 호출에 파라미터를 추가하면 됩니다.
(클라이언트 필터 로직은 해당 필드에서 제거)

---

## 2. 목록 / 단건 응답 필드 누락 (필수)

### 현상

`hk_dictionary_service.get_hk_dictionary_list()` 의 응답 매핑:

```python
{
    "seq", "modern_korean", "historical_korean",
    "historical_period_start_dt", "historical_period_end_dt", "reg_dt",
}
```

`reg_member_seq`, `mod_dt`, `mod_member_seq`, `confirmed_yn` 이 빠져 있습니다.
`get_hk_dictionary()`(단건)에도 `confirmed_yn` 이 없습니다.

### 문제

- 이 필드들은 **정렬은 가능한데 화면에 값이 없습니다.** 사용자가 "수정일시 내림차순"으로 정렬해도
  수정일시 컬럼이 없어 정렬 결과를 확인할 수 없습니다.
- `confirmed_yn`(검수 여부)은 사전 품질 관리의 핵심 값인데 조회 수단이 전혀 없습니다.
  특히 `/dump` 로 들어온 항목은 `'N'`, 단건 등록 항목은 `'Y'` 로 서로 다르게 저장되므로
  (§8 참고) 목록에서 구분할 수 있어야 합니다.

### 요청 사양

목록 응답 아이템에 `reg_member_seq`, `mod_dt`, `mod_member_seq`, `confirmed_yn` 추가,
단건 응답에 `confirmed_yn` 추가.

프론트엔드는 이미 `HkDictionaryDto` 에 optional 로 선언해 두었으므로
(`src/lib/api/dictionary.ts`) **백엔드가 내려주기 시작하면 상세 모달은 즉시 값이 표시**되고,
목록 컬럼만 `src/components/dictionary/DictionaryTable.tsx` 의 `COLUMNS` 에 추가하면 됩니다.

---

## 3. `/dump` 비동기 작업 추적 식별자 부재

### 현상

```python
# hk_dictionary_service.dump_raw_hk_dictionary()
task_id = str(uuid.uuid4())   # 생성은 하지만
...
return ResultVo(success=True) # 응답에 담기지 않음
```

```python
# task_worker/handlers/hk_dictionary/hk_dictionary_service.handle_response()
llm_response = {"result": ..., "llm_msg": ..., "items_cnt": ...}
```

브로드캐스트 페이로드에도 `task_id` / 요청자 정보가 없습니다.

### 문제

요구사항에 따라 사전 화면의 소켓 room 은 **세션별이 아닌 전체 통합(`hk_dictionary_service`)** 입니다.
즉 A 사용자가 요청한 작업 결과가 B 사용자 화면에도 그대로 도착하는데,
현재 페이로드로는 **어느 요청에 대한 결과인지 구분할 수 없습니다.**

프론트엔드는 이 제약을 그대로 노출합니다 — 작업 결과 피드에
"모든 사용자의 일괄 삽입 결과가 함께 표시됩니다" 라고 안내하고, 요청 건수만 카운트합니다
(`src/hooks/useDictionaryRoom.ts`, `src/components/dictionary/TaskFeed.tsx`).

### 요청 사양

1. `POST /dump` 응답에 `task_id` 반환

```python
return ResultVo(success=True, data={"task_id": task_id})
```

2. 워커 브로드캐스트 페이로드에 `task_id` 와 요청자 포함

```python
llm_response = {
    "task_id": task_id,          # task["task_id"] 를 params 로 전달하거나 task 에서 직접 사용
    "reg_member_seq": reg_member_seq,
    "result": result,
    "llm_msg": llm_msg,
    "items_cnt": items_cnt,
}
```

이 두 가지가 들어오면 프론트에서 "내가 요청한 작업"만 골라 진행 상태/완료 알림을 매칭할 수 있습니다.

### (참고) 실패 시 원인 미전달

`handle_hk_dictionary_dump_raw()` 는 LLM 실패/DB 실패 모두 `llm_msg="관리자에게 문의 주세요."` 로 동일하게 응답합니다.
운영 중 원인 구분이 어려우므로 최소한 실패 단계 코드(`stage: "llm" | "db"`) 정도는 함께 내려주면 좋겠습니다.

---

## 4. 파일(Excel / CSV / PDF) 일괄 업로드 API 부재

요구사항 4-B(2) 에 따라 **프론트엔드만 구현**했습니다.
(`src/components/dictionary/BulkFileDialog.tsx` — 드래그앤드롭 / 확장자·용량 검증 / 목록 관리 / 기간 지정까지)

전송 함수는 스텁이며 실제 요청을 보내지 않고 `BackendNotImplementedError` 를 던집니다
(`src/lib/api/dictionary.ts` 의 `uploadDictionaryFiles`).
**백엔드가 준비되면 같은 파일의 주석 블록 구현으로 교체하면 끝납니다.**

### 프론트엔드가 기대하는 계약

```
POST /api/v1/au/hk_dictionary/dump/file
Content-Type: multipart/form-data

files                        : File[]   (복수, 최대 10개 / 파일당 20MB)
historical_period_start_dt   : str      "YYYY-MM-DD 00:00:00"
historical_period_end_dt     : str      "YYYY-MM-DD 23:59:59"
room_name                    : str      "hk_dictionary_service"

→ 200 ResultVo(success=True, data={"task_ids": ["...", "..."]})
```

허용 확장자: `.xlsx`, `.xls`, `.csv`, `.pdf`

### 백엔드에서 정해야 할 것

1. **파일 저장 위치** — 프로젝트에 MinIO 구성이 있으므로(`proj_historical_korean_ai/minio`) 원본 보관은 MinIO 권장.
2. **Excel/CSV 스키마 규격** — 다음 중 택일이 필요합니다.
   - (a) 정형: `modern_korean`, `historical_korean` 컬럼 헤더 고정 → LLM 없이 바로 `bulk_add_hk_dictionary`
   - (b) 비정형: 셀 텍스트를 이어붙여 기존 `raw_text` LLM 파이프라인(`TSK_002`)에 투입
   - 프론트는 (a)/(b) 어느 쪽이든 UI 변경 없이 대응 가능하나, (a) 라면 사용자에게 보여줄 **템플릿 파일**이 필요합니다.
3. **PDF 텍스트 추출** — 스캔 PDF(이미지)면 OCR 이 필요합니다. 지원 범위 확정 필요.
4. **결과 통보** — `/dump` 와 동일하게 `room_name` 소켓 브로드캐스트를 권장합니다(§3 의 `task_id` 포함).

---

## 5. 날짜 포맷 / 타임존 처리 불일치

### 현상

같은 `historical_period_*_dt` 인데 엔드포인트마다 포맷과 처리 경로가 다릅니다.

| 경로 | 예시 값 | 처리 |
|------|---------|------|
| `POST` / `PUT` / `GET(list)` | `"1446-10-09T00:00:00+09:00"` | `datetime.fromisoformat()` → **오프셋 포함 aware** |
| `POST /dump` | `"1418-01-01 00:00:00"` | 파싱 없이 워커까지 문자열 전달 → psycopg2 바인딩 → **DB 세션 TZ 로 해석되는 naive** |

`hk_dictionary.historical_period_start_dt` 컬럼은 `TIMESTAMP(timezone=True)` 이므로,
**동일한 연도를 입력해도 CRUD 로 넣은 값과 `/dump` 로 넣은 값의 실제 저장 시각이 어긋날 수 있습니다.**
DB 세션 TZ 가 UTC 라면 `/dump` 항목은 KST 기준보다 9시간 앞선 값으로 저장되고,
그 결과 §1 의 기간 검색(`>= start AND <= end`) 경계에서 항목이 누락/포함될 수 있습니다.

### 프론트엔드 현재 대응

문서화된 예시 스펙을 **그대로** 따랐습니다 (`src/lib/dictionary/datetime.ts`).

- CRUD → `toPeriodStartIso()` / `toPeriodEndIso()` : `YYYY-MM-DDT00:00:00+09:00` / `T23:59:59+09:00`
- `/dump` → `toDumpStart()` / `toDumpEnd()` : `YYYY-MM-DD 00:00:00` / `YYYY-MM-DD 23:59:59`

### 요청 사양

`/dump` 도 ISO 8601(오프셋 포함)을 받아 `datetime.fromisoformat()` 로 정규화한 뒤 워커에 넘겨주세요.
확정되면 프론트는 `toDumpStart/End` 를 `toPeriodStartIso/EndIso` 로 교체하기만 하면 됩니다(1줄 변경).

> 참고: UI 는 요구사항대로 **연-월-일만 입력**받고, 시각(시작 `00:00:00` / 종료 `23:59:59`)은
> 전송 직전에 자동으로 채웁니다. 사용자가 시각을 지정할 수단은 없습니다.

---

## 6. `order_by` 화이트리스트 부재

```python
# hk_dictionary_dao.get_hk_dictionary_list()
order_column = getattr(HKDictionaryEntity, order_by, HKDictionaryEntity.seq)
```

`getattr` 의 기본값은 **속성이 없을 때만** 동작합니다.
`order_by=metadata`, `order_by=registry`, `order_by=__table__` 처럼
SQLAlchemy 선언적 모델이 실제로 갖고 있는 속성명이 들어오면 컬럼이 아닌 객체가 반환되어
`.asc()` 호출 단계에서 예외 → `InternalServerException("사전 목록 조회 실패")` 로 떨어집니다.

프론트는 셀렉트 박스로만 값을 만들어 정상 컬럼만 보내지만, 외부에서 직접 호출되는 경우를 막아 주세요.

```python
ALLOWED_ORDER_COLUMNS = {
    "seq", "modern_korean", "historical_korean",
    "historical_period_start_dt", "historical_period_end_dt",
    "reg_dt", "reg_member_seq", "mod_dt", "mod_member_seq", "confirmed_yn",
}
if order_by not in ALLOWED_ORDER_COLUMNS:
    order_by = "seq"
```

---

## 7. 기간 검색 조건이 "포함(contained)"만 지원

```python
if start_dt and end_dt:
    conditions.append(and_(
        HKDictionaryEntity.historical_period_start_dt >= start_dt,
        HKDictionaryEntity.historical_period_end_dt   <= end_dt,
    ))
```

이는 **검색 기간 안에 완전히 들어가는 항목**만 찾습니다.
예를 들어 `1392~1892` 로 검색하면, 시대가 `1446~1910` 인 항목은 종료일이 범위를 벗어나 제외됩니다.

사전 검색에서는 보통 "이 기간과 **겹치는** 항목"을 원합니다(overlap).

```python
# overlap 조건
and_(
    HKDictionaryEntity.historical_period_start_dt <= end_dt,
    HKDictionaryEntity.historical_period_end_dt   >= start_dt,
)
```

`period_match_mode=contain|overlap` (기본 `contain`, 하위호환 유지) 파라미터 추가를 제안합니다.
프론트는 기간 바 옆에 모드 토글만 추가하면 됩니다.

> 참고로 현재 필터 라벨에는 실제 동작(`start_dt ≥ 시작일 · end_dt ≤ 종료일`)을 그대로 적어
> 사용자가 오해하지 않도록 해 두었습니다.

---

## 8. `confirmed_yn` 등록 시 하드코딩

| 경로 | 저장되는 `confirmed_yn` |
|------|-------------------------|
| `POST /hk_dictionary` (`app` 서비스) | `'Y'` 하드코딩 |
| `/dump` → 워커 `bulk_add_hk_dictionary` | `'N'` 하드코딩 |
| `PUT /hk_dictionary/{seq}` | 요청 값 반영 (화이트리스트에 포함) |

단건 등록은 무조건 "검수 완료"로 들어가는데, 사람이 직접 넣은 값이라도 검수 전 상태로 두고 싶을 수 있습니다.
`POST` 도 요청 바디의 `confirmed_yn` 을 받아(기본값 `'Y'` 유지) 처리하도록 열어 주세요.

프론트는 등록 폼에서 이 항목을 **disabled + "등록 시에는 백엔드가 'Y' 로 고정합니다" 안내**로 처리해 두었습니다.
백엔드가 열리면 `disabled={!isEdit}` 만 제거하면 됩니다
(`src/components/dictionary/DictionaryFormDialog.tsx`).

---

## 9. (참고) 삭제는 Soft Delete 로 확인됨

`delete_hk_dictionary()` 는 `delete_yn='Y'`, `mod_member_seq`, `mod_dt` 만 갱신합니다.
조회 쿼리는 전부 `delete_yn = 'N'` 조건을 걸고 있어 목록에서 사라집니다.

프론트 삭제 확인 다이얼로그에 *"Soft Delete: delete_yn 이 'Y' 로 변경되며 목록에서 제외됩니다"* 로 명시했습니다.

향후 복구 기능이 필요하면 `include_deleted=true` 옵션과 복구용 엔드포인트가 별도로 필요합니다(현재 요구사항 범위 밖).

---

## 10. (참고) `/dump` 의 `member_seq` 중복 전달

```python
input_message = f"<!rule^.^member_seq={user_details.seq}!>{raw_text}"
task = {"params": {"input_message": input_message, ..., "reg_member_seq": reg_member_seq}}
```

`member_seq` 가 프롬프트 문자열 내부와 `params` 양쪽에 들어갑니다.
워커는 `params.reg_member_seq` 만 DB 적재에 사용하므로, 프롬프트에 섞인 값은 LLM 입력을 오염시킬 소지가 있습니다.
(프론트 영향은 없으나 정리 대상으로 남깁니다.)

---

## 부록 — 프론트엔드에서 함께 수정한 공통 코드 1건

백엔드와 무관하지만 기록으로 남깁니다.

`src/lib/socket/RealChatSocket.ts` 의 `disconnect()` 에서 **소켓을 닫기 전에 이벤트 핸들러를 먼저 떼도록** 4줄을 추가했습니다.

- 사유: `close()` 는 비동기라 `onclose` 가 나중에 발화합니다. 채팅 → 사전 페이지로 이동하면
  (채팅 `useChatRuntime` 의 cleanup 이 `disconnect()`, 사전 훅이 `connect()`)
  그 사이 `manualClose` 가 이미 `false` 로 돌아가 있어, 뒤늦은 `onclose` 가 이를 "예기치 않은 끊김"으로
  오인해 **방금 새로 만든 소켓 참조(`this.ws`)를 `null` 로 덮고** 재연결을 예약합니다.
  결과적으로 유령 소켓이 남고 `join_room` 이 유실됩니다.
- 수동 종료 경로에서는 이후 이벤트가 필요 없으므로, 핸들러 해제는 기존 채팅 동작에 영향을 주지 않습니다.
