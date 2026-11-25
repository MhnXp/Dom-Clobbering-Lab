@echo off
setlocal
cd /d "%~dp0"

set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"

if not defined PY (
  echo.
  echo  Python 3 was not found in PATH.
  echo  Install it from https://www.python.org/downloads/
  echo  and tick "Add python.exe to PATH" during setup, then run this file again.
  echo.
  pause
  exit /b 1
)

echo.
echo  Starting DOM Clobbering Lab on http://127.0.0.1:8000/
echo  A second window will run the server. Close it to stop the lab.
echo.

start "DOM Clobbering Lab server" cmd /k %PY% server.py 8000
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8000/"

endlocal
exit /b 0
