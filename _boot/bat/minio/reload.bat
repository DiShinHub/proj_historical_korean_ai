@echo off
cd ../../../proj_historical_korean_ai/minio/docker-compose
docker-compose -p hk-ai-project-minio -f docker-compose.yml --env-file ./env/.env down
docker-compose -p hk-ai-project-minio -f docker-compose.yml --env-file ./env/.env up -d