@echo off
setlocal

set ROOT=%~dp0

echo =========================
echo hk BUILD SCRIPT
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
echo [3] build postgres

cd /d "%~dp0postgres"
call build.bat

echo.
echo [4] build redis

cd /d "%~dp0redis"
call build.bat

echo.
echo [5] build minio

cd /d "%~dp0minio"
call build.bat

echo.
echo [6] build be llm

cd /d "%~dp0llm"
call build.bat

echo.
echo [7] build fe web

cd /d "%~dp0web"
call build.bat


echo.
echo =========================
echo ALL SERVICES BUILT
echo =========================

@REM pause