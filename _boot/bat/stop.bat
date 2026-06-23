@echo off
setlocal

set ROOT=%~dp0

echo =========================
echo HK AI STOP SCRIPT
echo =========================

echo.
echo [3] Stop postgres

cd /d "%~dp0postgres"
call down.bat

echo.
echo [4] Stop redis

cd /d "%~dp0redis"
call down.bat

echo.
echo [5] Start minio

cd /d "%~dp0minio"
call down.bat

echo.
echo [6] Stop be llm

cd /d "%~dp0llm"
call down.bat


echo.
echo [7] Stop fe web

cd /d "%~dp0web"
call down.bat


echo.
echo =========================
echo ALL SERVICES STOPED
echo =========================

@REM pause