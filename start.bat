@echo off
echo ====================================
echo   Starting InfraMonitor SRE
echo ====================================

echo [1/3] Starting Backend API...
start "InfraMonitor Backend" cmd /k "cd /d %~dp0 && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 3 /nobreak > nul

echo [2/3] Starting Monitoring Agent...
start "InfraMonitor Agent" cmd /k "cd /d %~dp0 && python -m agent.main"

timeout /t 2 /nobreak > nul

echo [3/3] Starting Frontend...
start "InfraMonitor Frontend" cmd /k "cd /d %~dp0\frontend && npm run dev"

timeout /t 5 /nobreak > nul

echo [OK] Opening dashboard...
start http://localhost:5173

echo ====================================
echo   All services started!
echo   Close this window when done.
echo ====================================
pause
