@echo off
setlocal
cd /d "%~dp0"
echo ===================================================
echo   TimePilot AI - Autonomous Cognitive Calendar
echo   Zetaris USL + Meterless H-MEM + NVIDIA Nemotron
echo ===================================================
echo.
set "PYTHON_CMD="
where py >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=py -3"
if not defined PYTHON_CMD (
  where python >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=python"
)
if not defined PYTHON_CMD (
  where python3 >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=python3"
)
if not defined PYTHON_CMD (
  echo Python 3.10 or newer was not found.
  echo Install Python from https://www.python.org/downloads/ and enable Add Python to PATH.
  goto :failed
)

echo Starting TimePilot AI on http://localhost:8000...
echo.
%PYTHON_CMD% run.py --serve --port 8000
if errorlevel 1 goto :failed
goto :end
:failed
echo.
echo TimePilot AI did not start. Read the error above.
pause
:end
endlocal
