@echo off
setlocal enabledelayedexpansion
title Chatbot IA Local - STOP

echo ==============================
echo DETENIENDO CHATBOT IA LOCAL
echo ==============================

set "ROOT=%~dp0"
set "PID_DIR=%ROOT%.runtime"

call :kill_pid_file "%PID_DIR%\frontend.pid" "Frontend"
call :kill_pid_file "%PID_DIR%\backend.pid" "Backend"
call :kill_pid_file "%PID_DIR%\ollama.pid" "Ollama"

echo.
echo Cerrando posibles ventanas CMD por titulo...
taskkill /FI "WINDOWTITLE eq Frontend" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Backend" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Ollama" /T /F >nul 2>&1

echo.
echo Liberando puertos por si quedo algo colgado...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do taskkill /PID %%a /T /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /PID %%a /T /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :11434') do taskkill /PID %%a /T /F >nul 2>&1

if exist "%PID_DIR%" (
    echo.
    echo Limpiando archivos PID...
    del /q "%PID_DIR%\*.pid" >nul 2>&1
)

echo.
echo ==============================
echo SERVICIOS DETENIDOS
echo ==============================
pause
exit /b 0


:kill_pid_file
set "FILE=%~1"
set "LABEL=%~2"

if exist "%FILE%" (
    set /p PID=<"%FILE%"
    if not "!PID!"=="" (
        echo Cerrando %LABEL% ^(PID !PID!^)^...
        taskkill /PID !PID! /T /F >nul 2>&1
    ) else (
        echo %LABEL%: PID vacio.
    )
) else (
    echo %LABEL%: no se encontro archivo PID.
)

exit /b 0