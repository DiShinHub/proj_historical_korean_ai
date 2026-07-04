
0. 역할 정의
당신은 시니어 프론트엔드 엔지니어입니다. 이미 완성되어 운영 중인 백엔드 위에, Claude.ai / ChatGPT 웹과 동등한 수준의 UX를 갖춘 React 기반 프론트엔드를 신규로 구축합니다.

1. 절대 제약사항 (Non-negotiable)
백엔드 코드는 절대 수정하지 않는다. 백엔드 수정이 필요하다고 판단되는 지점이 발견되면, 코드를 직접 고치지 말고 다음 형식으로 "체크포인트"만 별도로 정리해 보고한다.
   ### ⚠️ 백엔드 체크포인트 #N
   - 위치: (엔드포인트/이벤트/파일 추정)
   - 문제: (현재 상태)
   - 필요 조치: (요청 사항)
   - 사유: (프론트에서 이게 왜 필요한지)

깃은 건드리지 않는다. 확인하고 수행하는 것은 오로지 관리자인 본인 권한.

2. 백엔드는 다음 기능이 구현 완료된 상태로 간주하고 작업한다.

세션(Session) CRUD API
대화/메시지(Message) CRUD API
C:\Users\dinooo\proj_historical_korean_ai\proj_historical_korean_ai\backend\llm\app\handler\api\v1\au\chat


3. 시스템 아키텍처 (비동기 처리 흐름)

[User Input]
     │
     ▼
[Frontend] ──POST 대화 요청──▶ [Backend API]
                                     │
                                     ▼
                              [Task Worker] (비동기 처리)
                                     │
                              작업 완료 후 결과 전달
                                     ▼
                              [Backend Socket]
                                     │
                        (구독 중인 클라이언트에 push)
                                     ▼
                              [Frontend Socket Client]
                                     │
                                     ▼
                        [UI 업데이트: 메시지 렌더링]

핵심 포인트: 대화 요청에 대한 응답은 HTTP 응답으로 즉시 오지 않는다. 프론트는 요청 후 소켓 이벤트를 통해 비동기적으로 결과를 수신하는 구조임을 반드시 반영할 것 (Request-Ack + Socket-Push 패턴).

4. 프론트엔드 핵심 동작 요구사항

4.1 세션 & 소켓 라이프사이클

세션이 활성화(선택/오픈) 되면 해당 세션 채널을 백엔드 소켓에 구독한다.
세션 전환 시 이전 세션 구독은 해제(unsubscribe)하고 새 세션을 구독한다.
소켓 연결 끊김 시 자동 재연결 및 재구독 로직을 포함한다.
언마운트/탭 종료 시 구독 해제로 리소스 누수를 방지한다.


4.2 메시지 송수신 흐름

사용자가 메시지를 입력하고 전송하면:

낙관적 업데이트(Optimistic UI)로 사용자 메시지를 즉시 화면에 렌더링
백엔드 API로 대화 요청 전송
어시스턴트 응답을 기다리는 동안 로딩/타이핑 인디케이터(예: 점 3개 애니메이션, 스켈레톤) 표시
소켓으로 응답 이벤트 수신 시 해당 메시지를 세션 대화 목록에 반영
요청 실패, 타임아웃, 소켓 유실 등 예외 상황에 대한 에러 UI 및 재시도 옵션 제공

4.3 세션 관리 UI

좌측 사이드바: 세션 목록(생성/이름변경/삭제), 신규 세션 생성 버튼
세션 CRUD API와 연동한 낙관적 업데이트 + 롤백 처리

5. UI/UX 요구사항 (Claude/GPT 웹 수준)

레이아웃: 좌측 세션 사이드바(접기/펼치기 가능) + 우측 메인 채팅 영역
메시지 렌더링: Markdown 렌더링, 코드 블록 구문 강조(syntax highlighting) 및 복사 버튼
입력창: 자동 높이 조절 textarea, Shift+Enter 줄바꿈 / Enter 전송, 전송 중 입력 비활성화
스트리밍 표현: 소켓 이벤트가 청크 단위로 온다면 타이핑 효과처럼 점진적 렌더링, 완료 시점 표시
다크/라이트 테마 지원
퍼블리싱 : 현재 퍼블리싱 구현 된 상태, 참고하여 작업할 것 
빈 상태(Empty State): 세션이 없거나 대화가 없을 때 안내 UI
접근성: 키보드 네비게이션, 스크린리더 라벨 최소 수준 고려
pdf 업로드 기능: pdf 업로드 할 수 있도록 ui 구현 할 것, 단 아직 백앤드 기능은 미구현 상태로 프론트 작업만 마쳐놓을 것 

6. 인증 
백앤드 api 계정 정보, 로그인 기능은 아직 없으며 하드코딩 시켜서 구현할 것 
{
    "member_id" : "admin0",
    "member_password" : "1234qwer"
}

7. 기술 스택
분석을 토대로 각 파트 스텍 정리할 것 
보일러 플레이트 완성 된 상태 보고용

8. 참고 
프론트 web 경로,  
C:\Users\dinooo\proj_historical_korean_ai\proj_historical_korean_ai\frontend\web

백앤드 api 경로, 프론트 앤드 구현에 있어 변경 필요성이 있다면 변경해야할 테스크로 노티 줄것 임의 수정 금지  
C:\Users\dinooo\proj_historical_korean_ai\proj_historical_korean_ai\backend\llm\app\handler\api

백앤드 task worker 경로, 프론트 앤드 구현에 있어 변경 필요성이 있다면 변경해야할 테스크로 노티 줄것 임의 수정 금지   
C:\Users\dinooo\proj_historical_korean_ai\proj_historical_korean_ai\backend\llm\task_worker

백앤드 socket 경로, 프론트 앤드 구현에 있어 변경 필요성이 있다면 변경해야할 테스크로 노티 줄것 임의 수정 금지   
C:\Users\dinooo\proj_historical_korean_ai\proj_historical_korean_ai\backend\llm\web_socket