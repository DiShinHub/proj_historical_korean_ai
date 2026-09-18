# AGENTS.md

## 1. 프로젝트 개요

이 프로젝트는 다음 구조를 가진다.

```text
proj_historical_korean_ai/
├── backend/
│   └── llm/
├── frontend/
│   └── web/
├── minio/
├── postgres/
└── redis/
```

주요 구성:

* Backend: `backend/llm`
* Frontend Web: `frontend/web`
* Infrastructure: `minio`, `postgres`, `redis`

---
본 프로젝트는 현대국어와 중세국어의 LLM 번역 프로젝트로, chat gpt와 유사한 ui를 갖는다. 
핵심 기능은 요청에 대한 번역으로,  

## 2. 가장 중요한 작업 규칙

### Git 절대 금지

Codex는 Git과 관련된 작업을 수행하지 않는다.

금지:

* `git add`
* `git commit`
* `git push`
* `git pull`
* `git merge`
* `git rebase`
* `git checkout`
* `git reset`
* branch 생성/변경
* 기타 Git 상태나 이력에 영향을 주는 작업

Git 명령을 실행하지 않는다.

---

## 3. Backend 수정 

### ### Backend는 수정이 필요한 경우 수정 후 수정일지를 작성합니다.

Backend 경로:

```text
backend/llm/
```

다음과 같은 수정의 경우 정지 후 개발자에게 수정을 요청한다 

* DB 수정
* Docker 설정 변경


Backend 수정이 필요하면 다음 파일에 변경 요청 사항을 기록한다.

```text
./BACKEND_MODIFICATION_NOTES.md
```

기록 내용:

1. 문제가 무엇인지
2. 현재 동작이 어떻게 되어 있는지
3. 왜 Backend 수정이 필요한지
4. 수정이 필요한 파일
5. 수정이 필요한 코드 또는 로직
6. 권장 수정 방법
7. Frontend에서 함께 변경해야 하는 사항이 있는지
8. 예상되는 영향

---

## 4. Frontend 작업

Frontend Web 경로:

```text
frontend/web/
```

기본적으로 다음 범위의 작업은 수행할 수 있다.

* React / Next.js 코드 수정
* TypeScript 코드 수정
* UI 수정
* API 호출 코드 수정
* 상태 관리 코드 수정
* WebSocket 클라이언트 코드 수정
* Frontend 설정 수정
* Frontend Docker 관련 수정

---

## 5. 작업 방식

작업을 시작하기 전에 관련 파일과 현재 구조를 확인한다.

불필요한 파일을 대량으로 수정하거나 삭제하지 않는다.

가능하면:

* 가장 작은 범위로 수정한다.
* 기존 구조와 패턴을 유지한다.
* 기존 API 계약을 임의로 변경하지 않는다.
* 기존 기능을 임의로 제거하지 않는다.
* 수정 전후의 동작 차이를 확인한다.
* 데이터 흐름을 이해할 수 있게 console.log 로 주요 파트를 표시한다.

확실하지 않은 부분은 임의로 결정하지 말고 현재 코드를 기준으로 판단한다.

---

## 6. 환경 파일 및 민감 정보

다음과 같은 파일은 내용을 임의로 변경하지 않는다. 

```text
*.env
*.env.local
*.yaml
*.yaml.local
```

특히 다음 디렉터리의 설정 파일은 주의한다.

```text
backend/llm/properties/
backend/llm/docker-compose/env/
frontend/web/.env.local
minio/docker-compose/env/
postgres/docker-compose/env/
redis/docker-compose/env/
```

비밀번호, API Key, Secret 등의 값을 출력하거나 변경하지 않는다.

---

## 7. Docker

Docker 관련 작업은 현재 프로젝트 구조를 먼저 확인한 후 수행한다.

주요 Docker 구성:

```text
backend/llm/docker/
backend/llm/docker-compose/

frontend/web/docker/
frontend/web/docker-compose/

minio/docker-compose/
postgres/docker-compose/
redis/docker-compose/
```

Docker 설정을 변경할 때는 해당 서비스의 기존 실행 방식과 의존 관계를 먼저 확인한다.

---

## 8. 테스트 및 검증

코드를 수정한 경우 가능한 범위에서 관련 테스트 또는 검증을 수행한다.

예:

* TypeScript 오류 확인
* ESLint 확인
* Python 구문 오류 확인
* 관련 테스트 실행
* Docker Compose 설정 검증
* 애플리케이션 실행 확인

단, 검증을 위해 Git 명령을 사용하지 않는다.

---

## 9. 작업 결과 보고

작업이 끝나면 다음 내용을 간단히 정리한다.


```text
./FROMTEND_MODIFICATION_NOTES.md
```

### 주의 사항

추가 작업이 필요한 경우 명확하게 적는다.
패키지 설치는 정상 작업 


### 작업 목표 


**목적**
다음의 컬럼이 추가되었습니다. audio_path를 이용하여 번역 재생기를 만드는 것이 목적입니다.
audio_path = Column(ARRAY(Text))

**핵심 기능**
1. 데이터 api 조회 시 다음과 같이 조회됩니다. audio_path 칼럼을 이용하여 플레이어 재생 기능을 만들어야 합니다.
    api 
    def : 세션 키를 기반으로 채팅 정보를 로드합니다.
    url : http://localhost:28001/api/v1/au/chat/chat_message/list?page=1&page_size=10&chat_session_seq=1, 
    method : GET
    auth : necessary  

    response 
    {
        "success": true,
        "message": null,
        "data": {
            "data_list": [
                {
                    "seq": 1,
                    "role": "USER",
                    "content": [
                        "안녕하세요를 14세기 중세국어로 번역해줘."
                    ],
                    "ipa": null,
                    "audio_path": null,
                    "reg_dt": "2026-08-16T18:35:09.760931Z"
                },
                {
                    "seq": 2,
                    "role": "SYSTEM",
                    "content": [
                        "안녕ᄒᆞ신가"
                    ],
                    "ipa": [
                        "an.njəŋ.hʌ.ɕin.ɡa"
                    ],
                    "audio_path": [
                        "/audio/output_20260817033522834045.wav"
                    ],
                    "audio_expire_yn": ""
                    "reg_dt": "2026-08-16T18:35:23.003252Z"
                }
            ]
        }
    }

    **특이사항**
    1. audio_path의 경우 role 이 SYSTEM 인 경우에만 노출 됩니다. 
    2. 오디오 자체가 없는 경우도 있습니다. 아래의 정책을 따라 주세요
        role이 USER인 경우 -> content만 표시 
        role이 SYSTEM인데 -> audio 생성 실패로 간주-> content는 표시하고, audio 영역엔 not exist 워닝 표시 
        minio에 실제 데이터가 없는 경우 -> 만료로 간주 -> content는 표시하고, audio 영역엔 expire 워닝 표시
        audio_expire_yn이 Y인 경우 -> 만료로 간주 -> content는 표시하고, audio 영역엔 expire 워닝 표시
    
    3. 번역 후보가 여러 개인 경우 배열의 형태로 여러개가 넘어옵니다. 각 후보군 텍스트와 오디오를 바인딩 하여 노출하여아힙니다.
        role이 SYSTEM인데 두 길이가 다른경우 -> 백앤드 논리적 애러로 간주하며 content와 audio 영역을 바인딩 없이 순차적으로 노출 시키고, 일부 audio에 문제 있다고 워닝 표시 (재생은 되어야 함)

2. 소켓 응답 시 오디오 플레이어를 

    [Socket] 응답 수신(라우팅) 
    {sessionSeq: 1, payload: {…}}
    payload
    : 
    {result: 'success', llm_msg: '안녕ᄒᆞ신가^T|A^/audio/output_20260817124324364582.wav'}
    sessionSeq
    : 
    1
    [[Prototype]]
    : 
    Object

    [Socket] 응답 수신 1 
    {result: 'success', llm_msg: '안녕ᄒᆞ신가^T|A^/audio/output_20260817124351546619.wav\n\n평안ᄒᆞ신가^T|A^/audio/output_20260817124354396466.w'}
    llm_msg
    : 
    "안녕ᄒᆞ신가^T|A^/audio/output_20260817124351546619.wav\n\n평안ᄒᆞ신가^T|A^/audio/output_20260817124354396466.w"
    result
    : 
    "success"
    [[Prototype]]
    : 
    Object

    **특이사항**
    소켓 응답은 플레인 텍스트로 전송됩니다. 
    ^T|A^ 이 구분자이며, 앞부분이 텍스트, 뒷부분이 오디오 경로입니다.
    번역 후보가 여러 개인경우 \n\n으로 여러개가 넘어옵니다. 각 후보군 텍스트와 오디오를 바인딩 하여 노출하여아힙니다. 
    UI는 데이터 api 조회와 동일하여야 합니다. 


**참고사항**
audio_path를 제외한 컬럼들에 대해 기본적인 연동은 마무리 되었습니다. 

**오디오 패키지**
오디오 플레이어에 필요한 npm패키지는 별도로 설치해주세요. 

**minio 연동 샘플**
프론트 앤드 minio 연동 샘플입니다. 연동 테스트 완료되었으며 연동에 이슈 있으면 일시 정지 후 개발자에게 노티 주세요.

<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>MinIO Audio Player Toy</title>
<style>
  :root{
    --bg:#0f1512;
    --panel:#161f1b;
    --panel-2:#1c2622;
    --line:#2a3b34;
    --ink:#e7f0ea;
    --ink-dim:#8fa79b;
    --accent:#4fd1a5;     /* 판독/음성 파형 느낌의 민트 */
    --warn:#e0a840;
    --err:#e0616f;
    --mono: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    --serif: "Noto Serif KR", "Nanum Myeongjo", serif;
  }
  *{box-sizing:border-box;}
  body{
    margin:0; background:var(--bg); color:var(--ink);
    font-family: "Pretendard","Apple SD Gothic Neo",sans-serif;
    padding:28px; line-height:1.5;
  }
  h1{
    font-family:var(--serif); font-weight:600; font-size:22px; margin:0 0 4px;
    letter-spacing:.2px;
  }
  .sub{color:var(--ink-dim); font-size:13px; margin-bottom:22px;}
  .grid{display:grid; grid-template-columns: 360px 1fr; gap:18px; align-items:start;}
  @media (max-width:900px){ .grid{grid-template-columns:1fr;} }
  .card{
    background:var(--panel); border:1px solid var(--line); border-radius:10px;
    padding:16px 18px;
  }
  .card + .card{margin-top:16px;}
  label{display:block; font-size:12px; color:var(--ink-dim); margin:10px 0 4px;}
  label:first-child{margin-top:0;}
  input[type=text], textarea{
    width:100%; background:var(--panel-2); border:1px solid var(--line); color:var(--ink);
    border-radius:6px; padding:8px 10px; font-family:var(--mono); font-size:12.5px;
    outline:none;
  }
  input[type=text]:focus, textarea:focus{border-color:var(--accent);}
  textarea{resize:vertical; min-height:120px;}
  .row{display:flex; gap:8px;}
  .row > *{flex:1;}
  button{
    background:var(--accent); color:#08201a; border:none; border-radius:6px;
    padding:9px 14px; font-weight:700; font-size:13px; cursor:pointer; margin-top:12px;
  }
  button.ghost{
    background:transparent; color:var(--ink); border:1px solid var(--line); font-weight:500;
  }
  button:hover{filter:brightness(1.08);}
  .tabs{display:flex; gap:6px; margin-bottom:10px;}
  .tab{
    padding:7px 12px; border-radius:6px; font-size:12.5px; cursor:pointer;
    border:1px solid var(--line); color:var(--ink-dim);
  }
  .tab.active{background:var(--panel-2); color:var(--accent); border-color:var(--accent);}
  .status{font-size:12px; margin-top:10px; font-family:var(--mono); white-space:pre-wrap;}
  .status.ok{color:var(--accent);}
  .status.bad{color:var(--err);}

  .msg{
    border:1px solid var(--line); border-radius:10px; padding:14px 16px; margin-bottom:14px;
    background:var(--panel);
  }
  .msg.user{border-left:3px solid #5b7bd6;}
  .msg.system{border-left:3px solid var(--accent);}
  .meta{display:flex; justify-content:space-between; align-items:baseline; margin-bottom:8px;}
  .role{
    font-family:var(--mono); font-size:11px; padding:2px 7px; border-radius:4px;
    letter-spacing:.5px;
  }
  .role.USER{background:#5b7bd633; color:#9db3ea;}
  .role.SYSTEM{background:#4fd1a52a; color:var(--accent);}
  .seq{color:var(--ink-dim); font-size:11px; font-family:var(--mono);}
  .banner{
    font-size:12px; padding:6px 10px; border-radius:6px; margin-bottom:10px;
    font-family:var(--mono);
  }
  .banner.warn{background:#e0a84022; color:var(--warn); border:1px solid #e0a84055;}
  .cand{
    display:flex; gap:12px; align-items:center; padding:8px 0;
    border-top:1px dashed var(--line);
  }
  .cand:first-of-type{border-top:none;}
  .cand-text{flex:1; min-width:0;}
  .cand-text .ko{font-family:var(--serif); font-size:15px;}
  .cand-text .ipa{color:var(--ink-dim); font-size:12px; font-family:var(--mono); margin-top:2px;}
  .cand-audio{flex:0 0 auto; display:flex; align-items:center; gap:8px;}
  audio{height:32px; width:230px;}
  .badge{
    font-size:11px; font-family:var(--mono); padding:3px 8px; border-radius:20px;
    white-space:nowrap;
  }
  .badge.notexist{background:#e0616f22; color:var(--err); border:1px solid #e0616f55;}
  .badge.expired{background:#e0a84022; color:var(--warn); border:1px solid #e0a84055;}
  .badge.runtime-err{background:#e0616f22; color:var(--err); border:1px solid #e0616f55;}
  .empty{color:var(--ink-dim); font-size:13px; padding:30px; text-align:center;}
  code{font-family:var(--mono); background:var(--panel-2); padding:1px 5px; border-radius:4px; font-size:11.5px;}
</style>
</head>
<body>

<h1>MinIO Audio Player · Toy</h1>
<div class="sub">audio_path 배열 → MinIO 오브젝트 재생 테스트용 프로토타입 (익명 다운로드 정책 기반)</div>

<div class="grid">
  <!-- 좌측: 설정 + 입력 -->
  <div>
    <div class="card">
      <label>MinIO Endpoint</label>
      <input id="cfgEndpoint" type="text" value="http://localhost:9000">
      <div class="row">
        <div>
          <label>Bucket</label>
          <input id="cfgBucket" type="text" value="hkai-bucket">
        </div>
      </div>
      <button class="ghost" id="btnTest" style="width:100%">연결 테스트 (버킷 루트 조회)</button>
      <div class="status" id="testStatus"></div>
    </div>

    <div class="card">
      <div class="tabs">
        <div class="tab active" data-mode="api">API 응답 (JSON)</div>
        <div class="tab" data-mode="socket">소켓 메시지 (Plain)</div>
      </div>

      <div id="panelApi">
        <label>chat_message/list 의 data_list 를 붙여넣으세요</label>
        <textarea id="apiInput"></textarea>
      </div>

      <div id="panelSocket" style="display:none">
        <label>llm_msg 값을 붙여넣으세요 (^T|A^ 구분자, \n\n 로 다중 후보)</label>
        <textarea id="socketInput"></textarea>
      </div>

      <button id="btnRender" style="width:100%">렌더링</button>
      <button class="ghost" id="btnSample" style="width:100%">샘플 데이터 채우기</button>
    </div>
  </div>

  <!-- 우측: 결과 -->
  <div class="card" id="resultPanel">
    <div class="empty">왼쪽에서 데이터를 입력하고 [렌더링]을 눌러주세요.</div>
  </div>
</div>

<script>
const $ = (sel) => document.querySelector(sel);
const endpointEl = $('#cfgEndpoint');
const bucketEl = $('#cfgBucket');
const resultPanel = $('#resultPanel');

// ---- 탭 전환 ----
document.querySelectorAll('.tab').forEach(t => {
  t.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
    t.classList.add('active');
    const mode = t.dataset.mode;
    $('#panelApi').style.display = mode === 'api' ? 'block' : 'none';
    $('#panelSocket').style.display = mode === 'socket' ? 'block' : 'none';
  });
});

// ---- 연결 테스트 ----
$('#btnTest').addEventListener('click', async () => {
  const st = $('#testStatus');
  st.textContent = '조회 중...';
  st.className = 'status';
  const url = `${endpointEl.value.replace(/\/$/,'')}/${bucketEl.value}/`;
  try {
    const res = await fetch(url, { method: 'GET' });
    if (res.ok || res.status === 403) {
      st.textContent = `OK (HTTP ${res.status}) — ${url}\n※ 403이어도 버킷 자체엔 접근 가능. 개별 오브젝트가 anonymous download 정책이면 재생됨.`;
      st.className = 'status ok';
    } else {
      st.textContent = `HTTP ${res.status} — ${url}`;
      st.className = 'status bad';
    }
  } catch (e) {
    st.textContent = `요청 실패: ${e.message}\n(CORS 설정 또는 서버 접근 불가 가능성)`;
    st.className = 'status bad';
  }
});

// ---- 오디오 URL 빌더 ----
// audio_path 예: "/audio/output_xxx.wav" → endpoint/bucket/audio/output_xxx.wav
function buildAudioUrl(audioPath) {
  const ep = endpointEl.value.replace(/\/$/, '');
  const bucket = bucketEl.value.replace(/^\/|\/$/g, '');
  const path = audioPath.replace(/^\//, '');
  return `${ep}/${bucket}/${path}`;
}

// ---- 샘플 데이터 ----
const SAMPLE_API = [
  {
    "seq": 1, "role": "USER",
    "content": ["안녕하세요를 14세기 중세국어로 번역해줘."],
    "ipa": null, "audio_path": null, "audio_expire_yn": "",
    "reg_dt": "2026-08-16T18:35:09.760931Z"
  },
  {
    "seq": 2, "role": "SYSTEM",
    "content": ["안녕ᄒᆞ신가", "평안ᄒᆞ신가"],
    "ipa": ["an.njəŋ.hʌ.ɕin.ɡa", "pʰjəŋ.an.hʌ.ɕin.ɡa"],
    "audio_path": ["/audio/output_20260817033522834045.wav", "/audio/output_20260817033525112233.wav"],
    "audio_expire_yn": "",
    "reg_dt": "2026-08-16T18:35:23.003252Z"
  },
  {
    "seq": 3, "role": "SYSTEM",
    "content": ["오디오 생성 실패 예시"],
    "ipa": null, "audio_path": null, "audio_expire_yn": "",
    "reg_dt": "2026-08-16T18:36:00.000000Z"
  },
  {
    "seq": 4, "role": "SYSTEM",
    "content": ["오디오 만료 예시"],
    "ipa": null, "audio_path": ["/audio/output_expired_sample.wav"],
    "audio_expire_yn": "Y",
    "reg_dt": "2026-08-16T18:37:00.000000Z"
  },
  {
    "seq": 5, "role": "SYSTEM",
    "content": ["후보1", "후보2", "후보3"],
    "ipa": null,
    "audio_path": ["/audio/output_mismatch_1.wav", "/audio/output_mismatch_2.wav"],
    "audio_expire_yn": "",
    "reg_dt": "2026-08-16T18:38:00.000000Z"
  }
];

const SAMPLE_SOCKET =
`안녕ᄒᆞ신가^T|A^/audio/output_20260817124351546619.wav

평안ᄒᆞ신가^T|A^/audio/output_20260817124354396466.wav`;

$('#btnSample').addEventListener('click', () => {
  const activeMode = document.querySelector('.tab.active').dataset.mode;
  if (activeMode === 'api') {
    $('#apiInput').value = JSON.stringify(SAMPLE_API, null, 2);
  } else {
    $('#socketInput').value = SAMPLE_SOCKET;
  }
});

// ---- 소켓 메시지 → API 형태로 정규화 ----
// "text^T|A^path" 를 \n\n 로 분리 → content[], audio_path[] 로 변환한 SYSTEM 메시지 1개 생성
function parseSocketMessage(raw) {
  const parts = raw.split(/\n\n+/).map(s => s.trim()).filter(Boolean);
  const content = [];
  const audio_path = [];
  parts.forEach(p => {
    const [text, path] = p.split('^T|A^');
    content.push((text || '').trim());
    audio_path.push(path ? path.trim() : null);
  });
  // path 가 하나라도 null이면 전체를 null로 취급하지 않고 개별 유지 (소켓은 항상 쌍으로 온다는 전제)
  return [{
    seq: 'socket',
    role: 'SYSTEM',
    content,
    ipa: null,
    audio_path,
    audio_expire_yn: '',
    reg_dt: new Date().toISOString()
  }];
}

// ---- 렌더링 ----
$('#btnRender').addEventListener('click', () => {
  const activeMode = document.querySelector('.tab.active').dataset.mode;
  let items;
  try {
    if (activeMode === 'api') {
      const raw = JSON.parse($('#apiInput').value);
      items = Array.isArray(raw) ? raw : (raw.data_list || raw.data?.data_list || []);
    } else {
      const raw = $('#socketInput').value.trim();
      if (!raw) throw new Error('소켓 메시지가 비어있습니다.');
      items = parseSocketMessage(raw);
    }
  } catch (e) {
    resultPanel.innerHTML = `<div class="empty" style="color:var(--err)">파싱 실패: ${e.message}</div>`;
    return;
  }
  renderMessages(items);
});

function renderMessages(items) {
  if (!items || items.length === 0) {
    resultPanel.innerHTML = `<div class="empty">표시할 메시지가 없습니다.</div>`;
    return;
  }
  resultPanel.innerHTML = '';
  items.forEach(item => resultPanel.appendChild(renderMessage(item)));
}

function renderMessage(item) {
  const wrap = document.createElement('div');
  wrap.className = `msg ${item.role === 'USER' ? 'user' : 'system'}`;

  const meta = document.createElement('div');
  meta.className = 'meta';
  meta.innerHTML = `
    <span class="role ${item.role}">${item.role}</span>
    <span class="seq">#${item.seq ?? '-'} · ${item.reg_dt ?? ''}</span>
  `;
  wrap.appendChild(meta);

  // USER: content만 표시, audio 영역 없음
  if (item.role === 'USER') {
    const content = item.content || [];
    content.forEach(text => {
      const c = document.createElement('div');
      c.className = 'cand';
      c.innerHTML = `<div class="cand-text"><div class="ko">${escapeHtml(text)}</div></div>`;
      wrap.appendChild(c);
    });
    return wrap;
  }

  // SYSTEM 이하 규칙 처리
  const content = item.content || [];
  const audioPaths = item.audio_path; // null 가능
  const expired = item.audio_expire_yn === 'Y';

  // case: audio_path 자체가 없음 → 생성 실패(not exist)
  if (!audioPaths) {
    content.forEach((text, i) => {
      wrap.appendChild(renderCandidate(text, item.ipa?.[i], { type: 'notexist' }));
    });
    return wrap;
  }

  // case: 개수 불일치 → 백엔드 논리 오류, 바인딩 없이 순차 노출 + 경고 배너
  if (content.length !== audioPaths.length) {
    const banner = document.createElement('div');
    banner.className = 'banner warn';
    banner.textContent = `⚠ content(${content.length})와 audio_path(${audioPaths.length}) 개수 불일치 — 순차 노출 (바인딩 안 됨)`;
    wrap.appendChild(banner);

    const maxLen = Math.max(content.length, audioPaths.length);
    for (let i = 0; i < maxLen; i++) {
      const text = content[i];
      const path = audioPaths[i];
      if (text !== undefined) {
        wrap.appendChild(renderCandidate(text, item.ipa?.[i],
          path ? { type: expired ? 'expired' : 'play', path } : { type: 'notexist' }
        ));
      } else if (path) {
        // 텍스트 없이 오디오만 남는 경우 (개수 불일치 극단 케이스)
        wrap.appendChild(renderCandidate('(텍스트 없음)', null,
          { type: expired ? 'expired' : 'play', path }
        ));
      }
    }
    return wrap;
  }

  // case: 정상 바인딩
  content.forEach((text, i) => {
    const path = audioPaths[i];
    if (expired || !path) {
      wrap.appendChild(renderCandidate(text, item.ipa?.[i], { type: 'expired' }));
    } else {
      wrap.appendChild(renderCandidate(text, item.ipa?.[i], { type: 'play', path }));
    }
  });

  return wrap;
}

function renderCandidate(text, ipa, audioState) {
  const row = document.createElement('div');
  row.className = 'cand';

  const textDiv = document.createElement('div');
  textDiv.className = 'cand-text';
  textDiv.innerHTML = `
    <div class="ko">${escapeHtml(text ?? '')}</div>
    ${ipa ? `<div class="ipa">/${escapeHtml(ipa)}/</div>` : ''}
  `;
  row.appendChild(textDiv);

  const audioDiv = document.createElement('div');
  audioDiv.className = 'cand-audio';

  if (audioState.type === 'notexist') {
    audioDiv.innerHTML = `<span class="badge notexist">⛔ audio not exist</span>`;
  } else if (audioState.type === 'expired') {
    audioDiv.innerHTML = `<span class="badge expired">⏳ expired</span>`;
  } else if (audioState.type === 'play') {
    const url = buildAudioUrl(audioState.path);
    const audioEl = document.createElement('audio');
    audioEl.controls = true;
    audioEl.preload = 'none';
    audioEl.src = url;
    audioEl.title = url;

    const badge = document.createElement('span');
    badge.style.display = 'none';
    badge.className = 'badge runtime-err';
    badge.textContent = '⏳ expired (404 from minio)';

    // 실제 MinIO에 오브젝트가 없는 경우 → 런타임에 만료로 간주
    audioEl.addEventListener('error', () => {
      badge.style.display = 'inline-block';
      audioEl.style.opacity = '0.4';
    });

    audioDiv.appendChild(audioEl);
    audioDiv.appendChild(badge);
  }

  row.appendChild(audioDiv);
  return row;
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str ?? '';
  return div.innerHTML;
}
</script>
</body>
</html>

