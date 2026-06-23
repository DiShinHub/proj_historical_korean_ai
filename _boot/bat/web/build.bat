@echo off
cd ../../../proj_historical_korean_ai/frontend/web/docker-compose
docker-compose -p hk-ai-project-fe-web -f docker-compose.yml --env-file ./env/.env down
docker-compose -p hk-ai-project-fe-web -f docker-compose.yml --env-file ./env/.env build --no-cache