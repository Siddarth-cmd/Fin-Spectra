@echo off
echo ============================================================
echo   Fin-Spectra Financial Crime Investigation Platform
echo ============================================================
echo.

REM Start FastAPI backend
echo [1/2] Starting Fin-Spectra Backend (port 8000)...
start "Fin-Spectra Backend" cmd /k "cd /d "%~dp0" && uvicorn app.main:app --reload --port 8000"

REM Wait 3 seconds for backend to initialize
timeout /t 3 /nobreak > nul

REM Start Next.js frontend
echo [2/2] Starting Fin-Spectra Frontend (port 3000)...
start "Fin-Spectra Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ============================================================
echo   Services starting...
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8000/docs
echo ============================================================
echo.
echo Both services are starting in separate windows.
echo Press any key to exit this launcher.
pause > nul
