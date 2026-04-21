@echo off
setlocal enabledelayedexpansion
title Chatbot IA Local - START

echo ==============================
echo INICIANDO CHATBOT IA LOCAL
echo ==============================

set "ROOT=%~dp0"
set "PID_DIR=%ROOT%.runtime"

if not exist "%PID_DIR%" mkdir "%PID_DIR%"

cd /d "%ROOT%"

echo.
echo [1/5] Activando entorno Python...
if not exist "%ROOT%venv\Scripts\activate.bat" (
    echo ERROR: no se ha encontrado el entorno virtual en:
    echo %ROOT%venv\Scripts\activate.bat
    pause
    exit /b 1
)

echo.
echo [2/5] Iniciando Ollama...
for /f %%i in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "$p = Start-Process cmd.exe -WorkingDirectory '%ROOT%' -ArgumentList '/k ""title Ollama && ollama serve""' -PassThru; $p.Id"') do set "OLLAMA_PID=%%i"
echo %OLLAMA_PID%>"%PID_DIR%\ollama.pid"

echo Esperando a que Ollama responda...
call :wait_http "http://127.0.0.1:11434/api/tags" 30
if errorlevel 1 (
    echo ERROR: Ollama no respondio a tiempo.
    pause
    exit /b 1
)

echo.
echo [3/5] Iniciando Backend (FastAPI)...
for /f %%i in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "$p = Start-Process cmd.exe -WorkingDirectory '%ROOT%' -ArgumentList '/k ""title Backend && call venv\Scripts\activate.bat && python -m uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000""' -PassThru; $p.Id"') do set "BACKEND_PID=%%i"
echo %BACKEND_PID%>"%PID_DIR%\backend.pid"

echo Esperando a que el backend responda...
call :wait_backend 40
if errorlevel 1 (
    echo ERROR: El backend no respondio a tiempo.
    echo Revisa la ventana "Backend" por si uvicorn ha dado algun error.
    pause
    exit /b 1
)

echo.
echo [4/5] Iniciando Frontend (Next.js)...
if not exist "%ROOT%src\frontend\package.json" (
    echo ERROR: no se encontro package.json en:
    echo %ROOT%src\frontend\
    pause
    exit /b 1
)

for /f %%i in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "$p = Start-Process cmd.exe -WorkingDirectory '%ROOT%src\frontend' -ArgumentList '/k ""title Frontend && npm run dev""' -PassThru; $p.Id"') do set "FRONTEND_PID=%%i"
echo %FRONTEND_PID%>"%PID_DIR%\frontend.pid"

echo Esperando a que el frontend responda...
call :wait_http "http://127.0.0.1:3000" 45
if errorlevel 1 (
    echo ERROR: El frontend no respondio a tiempo.
    echo Revisa la ventana "Frontend" por si npm ha dado algun error.
    pause
    exit /b 1
)

echo.
echo [5/5] Abriendo navegador...
start "" http://127.0.0.1:3000

echo.
echo ==============================
echo CHATBOT INICIADO CORRECTAMENTE
echo ==============================
echo Ollama PID:   %OLLAMA_PID%
echo Backend PID:  %BACKEND_PID%
echo Frontend PID: %FRONTEND_PID%
echo ==============================
pause
exit /b 0


:wait_backend
set /a COUNT=0

:wait_backend_loop
set /a COUNT+=1

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "try { Invoke-WebRequest -Uri 'http://127.0.0.1:8000/docs' -UseBasicParsing -TimeoutSec 3 | Out-Null; exit 0 } catch {} ; try { Invoke-WebRequest -Uri 'http://127.0.0.1:8000/openapi.json' -UseBasicParsing -TimeoutSec 3 | Out-Null; exit 0 } catch {} ; try { Invoke-WebRequest -Uri 'http://127.0.0.1:8000/' -UseBasicParsing -TimeoutSec 3 | Out-Null; exit 0 } catch { exit 1 }"

if %errorlevel%==0 exit /b 0
if %COUNT% GEQ %1 exit /b 1

timeout /t 2 >nul
goto wait_backend_loop


:wait_http
set "URL=%~1"
set "MAX_TRIES=%~2"
set /a COUNT=0

:wait_http_loop
set /a COUNT+=1

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "try { Invoke-WebRequest -Uri '%URL%' -UseBasicParsing -TimeoutSec 3 | Out-Null; exit 0 } catch { exit 1 }"

if %errorlevel%==0 exit /b 0
if %COUNT% GEQ %MAX_TRIES% exit /b 1

timeout /t 2 >nul
goto wait_http_loop