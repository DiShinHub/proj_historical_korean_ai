@echo off
setlocal

set ROOT=%~dp0

echo =========================
echo HK AI START SCRIPT
echo =========================

echo.
echo [1] Git Pull
call git-pull.bat

echo.
echo [2] Check Docker

docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker not running. Starting Docker Desktop...

    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"

    echo Waiting for Docker to start...
    :docker_wait
    timeout /t 5 >nul
    docker info >nul 2>&1
    if %errorlevel% neq 0 goto docker_wait
)

echo Docker is running.


echo.
echo [3] Start postgres

cd /d "%~dp0postgres"
call reload.bat

echo.
echo [4] Start redis

cd /d "%~dp0redis"
call reload.bat

echo.
echo [5] Start minio

cd /d "%~dp0minio"
call reload.bat

echo.
echo [6] Start be llm

cd /d "%~dp0llm"
call reload.bat

echo.
echo [7] Start fe web

cd /d "%~dp0web"
call reload.bat

 
echo.
echo =========================
echo ALL SERVICES STARTED
echo =========================

@REM pause