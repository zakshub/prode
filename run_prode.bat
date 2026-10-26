@echo off
REM ============================================================================
REM PRODE Universal Windows Launcher
REM Automatically detects Python (py / python) OR Node.js (node) on Windows!
REM ============================================================================

setlocal
set "PY_CMD="

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py -3 -c "import sys; sys.exit(0)" >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        set "PY_CMD=py -3"
    )
)

if "%PY_CMD%"=="" (
    where python >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        python -c "import sys; sys.exit(0)" >nul 2>nul
        if %ERRORLEVEL% EQU 0 (
            set "PY_CMD=python"
        )
    )
)

if /I "%~1"=="open" goto :direct_open
if NOT "%PY_CMD%"=="" goto :use_python

where node >nul 2>nul
if %ERRORLEVEL% EQU 0 goto :use_node

echo [INFO] Neither Python nor Node was found in PATH. Opening standalone UI directly...
goto :direct_open

:direct_open
echo Opening PRODE Control Center directly in your default browser...
start "" "%~dp0prode\ui\index.html"
exit /b 0

:use_python
if "%~1"=="" goto :py_serve
if /I "%~1"=="serve" goto :py_serve
if /I "%~1"=="validate" (
    %PY_CMD% scripts\validate_workspace.py
    exit /b %ERRORLEVEL%
)
if /I "%~1"=="test" (
    %PY_CMD% scripts\validate_workspace.py
    if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
    %PY_CMD% -m unittest discover -s tests -v
    exit /b %ERRORLEVEL%
)
%PY_CMD% -m prode %*
exit /b %ERRORLEVEL%

:py_serve
echo ==============================================================================
echo  PRODE Control Center is starting!
echo  URL: http://127.0.0.1:8080 or http://localhost:8080
echo  NOTE: Keep this terminal window OPEN while using the browser dashboard.
echo  Press Ctrl+C to stop the server when finished.
echo ==============================================================================
start "" http://127.0.0.1:8080
%PY_CMD% -m prode serve --host 0.0.0.0 --port 8080
exit /b %ERRORLEVEL%

:use_node
if "%~1"=="" goto :node_serve
if /I "%~1"=="serve" goto :node_serve
node scripts\prode_node.mjs %*
exit /b %ERRORLEVEL%

:node_serve
echo ==============================================================================
echo  PRODE Control Center (Node.js engine) is starting!
echo  URL: http://127.0.0.1:8080 or http://localhost:8080
echo  NOTE: Keep this terminal window OPEN while using the browser dashboard.
echo  Press Ctrl+C to stop the server when finished.
echo ==============================================================================
start "" http://127.0.0.1:8080
node scripts\prode_node.mjs serve 8080
exit /b %ERRORLEVEL%
