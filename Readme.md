# 🚀 HK AI Project Setup Guide
이 문서는 프로젝트 실행을 위한 환경 구성 및 실행 방법을 안내합니다.

---

## 📦 필수 소프트웨어
다음 소프트웨어가 설치되어 있어야 합니다.

- 🐳 Docker
- 🧑 Git
- 🐍 Python 3.11.7

---

## 💡 권장 소프트웨어
개발 편의를 위해 아래 도구 설치를 권장합니다.

- 🛠️ DBeaver (DB 관리)
- 📮 Postman (API 테스트)

---

## open-ai api key
https://platform.openai.com/home
https://platform.openai.com/api-keys

빌링 등록 후 키 신청

## 🌐 Docker 네트워크 설정
프로젝트 실행 전 Docker 네트워크를 생성합니다.
docker network create hk-ai-network

## 🛠️ 환경변수
환경 설정 관련 문의는 담당자에게 요청 바랍니다.

## Windows 빌드/실행/중지 방법
<pre>
- 빌드
cd _boot\bat
build.bat
</pre>

<pre>
- 실행
cd _boot\bat
start.bat
</pre>

<pre>
- 중지
cd _boot\bat
stop.bat
</pre>

## postgres 셋업
<pre>
작성 중
</pre>

## minio 셋업
<pre>
# 1. Set alias
mc alias set myminio http://hk-ai-minio-compose:9000 minio minioadmin
mc alias set local http://localhost:9000 minio minioadmin

# 2. Create the service account / access key
mc admin user svcacct add \
  --access-key "" \
  --secret-key "" \
  myminio minio

# 3. set download
mc anonymous set download myminio/hkai-bucket
mc anonymous set download local/hkai-bucket

# 4. set cors
mc admin config set myminio api cors_allow_origin="*"

# 5. restart to set
mc admin service restart myminio
</pre>