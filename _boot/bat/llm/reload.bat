@echo off
cd ../../../proj_historical_korean_ai/backend/llm/docker-compose
docker-compose -p hk-ai-project-be-llm -f docker-compose.yml --env-file ./env/.env down
docker-compose -p hk-ai-project-be-llm -f docker-compose.yml --env-file ./env/.env up -d