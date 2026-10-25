@echo off
setlocal
cd /d "%~dp0"
echo ==============================================
echo   TimePilot AI - Calendar + AI + Voice Input
echo ==============================================
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
%PYTHON_CMD% -c "import riva.client" >nul 2>nul
if errorlevel 1 (
  echo Installing NVIDIA speech-to-text client for first use...
  %PYTHON_CMD% -m pip install -r backend\requirements.txt
  if errorlevel 1 (
    echo.
    echo WARNING: STT setup failed. Calendar and text agent will still start.
    echo To enable voice later, run: %PYTHON_CMD% -m pip install -r backend\requirements.txt
  )
)
echo.
%PYTHON_CMD% -m backend.app
if errorlevel 1 goto :failed
goto :end
:failed
echo.
echo TimePilot did not start. Read the error above.
pause
:end
endlocal
