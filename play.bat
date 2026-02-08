@echo off
REM PongWithIssues — Double-click launcher for Windows
REM Just double-click this file to play!

cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel%==0 (
    python play.py
) else (
    where python3 >nul 2>nul
    if %errorlevel%==0 (
        python3 play.py
    ) else (
        echo Error: Python not found. Install Python 3.8+ from https://python.org
        pause
        exit /b 1
    )
)
