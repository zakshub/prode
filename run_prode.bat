@echo off
REM ============================================================================
REM PRODE Universal Windows Launcher
REM Automatically detects Python (py / python) OR Node.js (node) on Windows!
REM Usage:
REM   run_prode.bat validate
REM   run_prode.bat test
REM   run_prode.bat status
REM   run_prode.bat roles
REM   run_prode.bat roadmap
REM   run_prode.bat simulate all
REM   run_prode.bat serve
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

if NOT "%PY_CMD%"=="" goto :use_python

where node >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    goto :use_node
)

echo [ERROR] Neither Python 3 nor Node.js was found in your Windows PATH.
exit /b 1

:use_python
if "%~1"=="" goto :py_serve
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
if /I "%~1"=="serve" goto :py_serve
%PY_CMD% -m prode %*
exit /b %ERRORLEVEL%

:py_serve
echo Starting PRODE Web Control Center (Python runtime) on http://127.0.0.1:8080 ...
start "" http://127.0.0.1:8080
%PY_CMD% -m prode serve --host 127.0.0.1 --port 8080
exit /b %ERRORLEVEL%

:use_node
if "%~1"=="" goto :node_serve
if /I "%~1"=="serve" goto :node_serve
node scripts\prode_node.mjs %*
exit /b %ERRORLEVEL%

:node_serve
echo Starting PRODE Web Control Center (Node.js runtime) on http://127.0.0.1:8080 ...
start "" http://127.0.0.1:8080
node scripts\prode_node.mjs serve 8080
exit /b %ERRORLEVEL%
